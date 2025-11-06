#!/usr/bin/env python3
"""
SharePoint Online Migration Preflight Scanner
==============================================
Recursively scans local or UNC paths and identifies issues that would block
or complicate SharePoint Online/OneDrive migration.

Author: 818Ninja Production Tool
License: MIT
"""

import os
import sys
import csv
import argparse
import logging
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Set
from datetime import datetime
import re
import json
import hashlib
import secrets
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

# Default Microsoft limits and thresholds
DEFAULT_MAX_PATH_LENGTH = 400
DEFAULT_MAX_FILENAME_LENGTH = 255
DEFAULT_MAX_FILE_SIZE_GB = 250
DEFAULT_MAX_FOLDER_DEPTH = 20
DEFAULT_BLOCKED_EXTENSIONS = ['.exe', '.dll', '.bat', '.cmd']

# Default exclusions for system/dev folders
DEFAULT_EXCLUDE_DIRS = [
    '$RECYCLE.BIN', 'System Volume Information', '$Recycle.Bin',
    'node_modules', '.git', '.svn', '__pycache__', '.venv', '.vscode',
    'Thumbs.db', '.DS_Store'
]

DEFAULT_EXCLUDE_EXTS = [
    '.tmp', '.temp', '.bak', '.log', '.cache'
]

# Reserved device names (Windows)
RESERVED_NAMES = {
    'CON', 'PRN', 'AUX', 'NUL',
    'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
    'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
}

RESERVED_PATTERNS = ['.lock', 'desktop.ini']
TEMP_PREFIX = '~$'
VTI_PATTERN = '_vti_'

# Microsoft's documented invalid characters for SPO/OneDrive
# Base set (always invalid)
INVALID_CHARS_BASE = set('~"*:<>?/\\{|}')

# Retry configuration for transient errors
MAX_RETRIES = 3
BASE_RETRY_DELAY = 0.5
TRANSIENT_ERROR_CODES = [32, 53, 64, 121]  # Sharing violation, network, file in use, timeout


def get_invalid_chars(allow_hash_percent: bool = True) -> Set[str]:
    """Get invalid character set based on tenant policy."""
    chars = INVALID_CHARS_BASE.copy()
    if not allow_hash_percent:
        chars.update({'#', '%', '&'})
    return chars


def check_reserved_name(name: str) -> bool:
    """Check if name is a Windows reserved device name or special SharePoint file."""
    base_name = os.path.splitext(name)[0].upper()
    
    # Check reserved device names
    if base_name in RESERVED_NAMES:
        return True
    
    # Check reserved patterns
    if name.lower() in RESERVED_PATTERNS:
        return True
    
    # Check temp file prefix
    if name.startswith(TEMP_PREFIX):
        return True
    
    # Check _vti_ anywhere in name
    if VTI_PATTERN in name.lower():
        return True
    
    return False


def retry_with_backoff(func, *args, max_retries: int = MAX_RETRIES, **kwargs):
    """Retry function with exponential backoff for transient errors."""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except OSError as e:
            if attempt == max_retries - 1:
                raise
            
            if hasattr(e, 'winerror') and e.winerror in TRANSIENT_ERROR_CODES:
                delay = BASE_RETRY_DELAY * (2 ** attempt)
                jitter = random.uniform(0, delay * 0.1)
                time.sleep(delay + jitter)
                continue
            else:
                raise


def anonymize_path(path: str, salt: str) -> str:
    """Hash path components for PHI/PII compliance."""
    parts = path.split(os.sep)
    hashed_parts = []
    
    for part in parts:
        if part:
            h = hashlib.sha256(f"{salt}{part}".encode()).hexdigest()[:16]
            hashed_parts.append(h)
        else:
            hashed_parts.append(part)
    
    return os.sep.join(hashed_parts)


class StreamedCSVWriter:
    """Write CSV rows as issues are found (memory efficient)."""
    
    def __init__(self, output_path: str, fieldnames: List[str], anonymize_fn=None):
        self.output_path = output_path
        self.fieldnames = fieldnames
        self.anonymize_fn = anonymize_fn
        self.file = None
        self.writer = None
        self.issue_count = 0
    
    def __enter__(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.output_path)), exist_ok=True)
        self.file = open(self.output_path, 'w', newline='', encoding='utf-8-sig')
        self.writer = csv.DictWriter(self.file, fieldnames=self.fieldnames)
        self.writer.writeheader()
        return self
    
    def write_issue(self, issue: dict):
        """Write single issue immediately."""
        if self.anonymize_fn:
            issue = issue.copy()
            issue['FullPath'] = self.anonymize_fn(issue['FullPath'])
            issue['CurrentValue'] = self.anonymize_fn(issue['CurrentValue'])
        
        self.writer.writerow(issue)
        self.issue_count += 1
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()


class PreflightScanner:
    """Core scanner logic for SharePoint Online preflight checks."""
    
    def __init__(
        self,
        max_path: int = DEFAULT_MAX_PATH_LENGTH,
        max_filename: int = DEFAULT_MAX_FILENAME_LENGTH,
        max_file_size_gb: int = DEFAULT_MAX_FILE_SIZE_GB,
        max_depth: int = DEFAULT_MAX_FOLDER_DEPTH,
        blocked_extensions: Optional[List[str]] = None,
        allow_hash_percent: bool = True,
        exclude_dirs: Optional[List[str]] = None,
        exclude_exts: Optional[List[str]] = None,
        workers: int = 1,
        anonymize: bool = False,
        progress: bool = False,
        stream_csv: bool = True
    ):
        self.max_path = max_path
        self.max_filename = max_filename
        self.max_file_size_bytes = max_file_size_gb * 1024 * 1024 * 1024
        self.max_depth = max_depth
        self.blocked_extensions = set(
            (blocked_extensions or DEFAULT_BLOCKED_EXTENSIONS)
        )
        self.invalid_chars = get_invalid_chars(allow_hash_percent)
        self.exclude_dirs = set(exclude_dirs or DEFAULT_EXCLUDE_DIRS)
        self.exclude_exts = set(exclude_exts or DEFAULT_EXCLUDE_EXTS)
        self.workers = workers
        self.anonymize = anonymize
        self.progress = progress and TQDM_AVAILABLE
        self.stream_csv = stream_csv
        self.anon_salt = secrets.token_hex(16) if anonymize else None
        self.scan_count = 0
        self.issue_count = 0
        self.logger = logging.getLogger(__name__)
        self.csv_writer = None
        
        if anonymize:
            self.logger.info(f"Anonymization enabled. Salt: {self.anon_salt} (save to de-anonymize)")
        
        if progress and not TQDM_AVAILABLE:
            self.logger.warning("tqdm not installed. Progress bar disabled. Install with: pip install tqdm")
    
    def should_exclude(self, entry_name: str, is_dir: bool) -> bool:
        """Check if item should be excluded from scan."""
        if is_dir:
            return entry_name in self.exclude_dirs
        else:
            _, ext = os.path.splitext(entry_name)
            return ext.lower() in self.exclude_exts

    
    def compute_depth(self, full_path: str, root_path: str) -> int:
        """
        Compute folder depth relative to the scan root.
        Handles both local drives and UNC paths correctly.
        """
        try:
            # Normalize paths
            full_normalized = os.path.normpath(full_path)
            root_normalized = os.path.normpath(root_path)
            
            # Get relative path
            rel_path = os.path.relpath(full_normalized, root_normalized)
            
            # Count directory separators
            if rel_path == '.':
                return 0
            return rel_path.count(os.sep)
        except (ValueError, Exception) as e:
            self.logger.warning(f"Could not compute depth for {full_path}: {e}")
            return 0
    
    def sanitize_filename(self, name: str) -> str:
        """
        Replace invalid characters with underscores and trim spaces/periods.
        """
        # Replace invalid characters
        sanitized = ''.join('_' if c in self.invalid_chars else c for c in name)
        
        # Strip leading/trailing spaces and periods
        sanitized = sanitized.strip(' .')
        
        return sanitized
    
    def truncate_to_limit(self, name: str, limit: int) -> str:
        """
        Truncate filename to the specified length, preserving extension if possible.
        """
        if len(name) <= limit:
            return name
        
        # Try to preserve the extension
        base, ext = os.path.splitext(name)
        if ext and len(ext) < limit - 1:
            max_base = limit - len(ext)
            return base[:max_base] + ext
        else:
            return name[:limit]
    
    def suggest_fix(self, item_name: str) -> str:
        """
        Generate a suggested filename fix.
        """
        fixed = self.sanitize_filename(item_name)
        fixed = self.truncate_to_limit(fixed, self.max_filename)
        return fixed
    
    def check_item(
        self,
        full_path: str,
        root_path: str,
        is_file: bool
    ) -> List[dict]:
        """
        Check a single file or folder for all SPO migration issues.
        Returns a list of issue records (may be empty or contain multiple issues).
        """
        issues = []
        item_name = os.path.basename(full_path)
        item_type = 'File' if is_file else 'Folder'
        
        # Decoded path length (as Unicode string)
        path_length = len(full_path)
        
        # Compute depth
        depth = self.compute_depth(full_path, root_path)
        
        # Get file size if it's a file
        file_size_mb = 0.0
        if is_file:
            try:
                file_size_bytes = retry_with_backoff(os.path.getsize, full_path)
                file_size_mb = file_size_bytes / (1024 * 1024)
            except OSError as e:
                self.logger.warning(f"Could not get size for {full_path}: {e}")
                file_size_bytes = 0
        else:
            file_size_bytes = 0
        
        # Check 0: Reserved device names (Windows/SharePoint)
        if check_reserved_name(item_name):
            issues.append({
                'ItemType': item_type,
                'FullPath': full_path,
                'IssueType': 'Reserved device name (Windows)',
                'CurrentValue': item_name,
                'SuggestedFix': f'{item_name}_file' if is_file else f'{item_name}_folder',
                'CharacterCount': len(item_name),
                'CharacterCountPath': path_length,
                'FileSizeMB': f'{file_size_mb:.2f}' if is_file else '',
                'FolderDepth': depth
            })
        
        # Check 1: Path length
        if path_length > self.max_path:
            issues.append({
                'ItemType': item_type,
                'FullPath': full_path,
                'IssueType': 'Path too long',
                'CurrentValue': str(path_length),
                'SuggestedFix': f'Shorten to ≤{self.max_path} chars',
                'CharacterCount': len(item_name),
                'CharacterCountPath': path_length,
                'FileSizeMB': f'{file_size_mb:.2f}' if is_file else '',
                'FolderDepth': depth
            })
        
        # Check 2: Filename length
        if len(item_name) > self.max_filename:
            issues.append({
                'ItemType': item_type,
                'FullPath': full_path,
                'IssueType': 'Filename too long',
                'CurrentValue': item_name,
                'SuggestedFix': self.suggest_fix(item_name),
                'CharacterCount': len(item_name),
                'CharacterCountPath': path_length,
                'FileSizeMB': f'{file_size_mb:.2f}' if is_file else '',
                'FolderDepth': depth
            })
        
        # Check 3: Invalid characters
        invalid_found = [c for c in item_name if c in self.invalid_chars]
        if invalid_found:
            issues.append({
                'ItemType': item_type,
                'FullPath': full_path,
                'IssueType': 'Invalid characters',
                'CurrentValue': f"{item_name} (chars: {', '.join(set(invalid_found))})",
                'SuggestedFix': self.suggest_fix(item_name),
                'CharacterCount': len(item_name),
                'CharacterCountPath': path_length,
                'FileSizeMB': f'{file_size_mb:.2f}' if is_file else '',
                'FolderDepth': depth
            })
        
        # Check 4: Leading/trailing spaces or periods
        stripped = item_name.strip(' .')
        if stripped != item_name:
            issues.append({
                'ItemType': item_type,
                'FullPath': full_path,
                'IssueType': 'Leading/trailing space or period',
                'CurrentValue': item_name,
                'SuggestedFix': self.suggest_fix(item_name),
                'CharacterCount': len(item_name),
                'CharacterCountPath': path_length,
                'FileSizeMB': f'{file_size_mb:.2f}' if is_file else '',
                'FolderDepth': depth
            })
        
        # Check 5: Blocked extensions (files only)
        if is_file:
            _, ext = os.path.splitext(item_name)
            if ext.lower() in self.blocked_extensions:
                issues.append({
                    'ItemType': item_type,
                    'FullPath': full_path,
                    'IssueType': 'Blocked file extension',
                    'CurrentValue': ext,
                    'SuggestedFix': 'Remove or rename file',
                    'CharacterCount': len(item_name),
                    'CharacterCountPath': path_length,
                    'FileSizeMB': f'{file_size_mb:.2f}',
                    'FolderDepth': depth
                })
        
        # Check 6: File size (files only)
        if is_file and file_size_bytes > self.max_file_size_bytes:
            issues.append({
                'ItemType': item_type,
                'FullPath': full_path,
                'IssueType': 'File too large',
                'CurrentValue': f'{file_size_mb:.2f} MB',
                'SuggestedFix': f'Split or reduce to ≤{self.max_file_size_bytes / (1024**3):.0f} GB',
                'CharacterCount': len(item_name),
                'CharacterCountPath': path_length,
                'FileSizeMB': f'{file_size_mb:.2f}',
                'FolderDepth': depth
            })
        
        # Check 7: Excessive folder depth
        if depth > self.max_depth:
            issues.append({
                'ItemType': item_type,
                'FullPath': full_path,
                'IssueType': 'Excessive folder depth',
                'CurrentValue': str(depth),
                'SuggestedFix': f'Flatten hierarchy to ≤{self.max_depth} levels',
                'CharacterCount': len(item_name),
                'CharacterCountPath': path_length,
                'FileSizeMB': f'{file_size_mb:.2f}' if is_file else '',
                'FolderDepth': depth
            })
        
        return issues
    
    def scan_directory(self, current_path: str, original_root: str = None) -> List[dict]:
        """
        Recursively scan a directory and return all issue records.
        
        Args:
            current_path: The directory currently being scanned
            original_root: The original scan root (for depth calculation)
        """
        # On first call, set original_root to current_path
        if original_root is None:
            original_root = current_path
            
        all_issues = []
        
        # Track names in this folder for case-collision detection
        folder_items = {}  # key: lowercase name, value: original name
        collision_groups = {}  # key: lowercase name, value: list of original names
        
        try:
            # First pass: collect all names and detect collisions
            entries_list = []
            with os.scandir(current_path) as entries:
                for entry in entries:
                    # Skip excluded items
                    if self.should_exclude(entry.name, entry.is_dir(follow_symlinks=False)):
                        continue
                    
                    entries_list.append(entry)
                    name_lower = entry.name.lower()
                    
                    if name_lower in folder_items:
                        # Collision detected!
                        if name_lower not in collision_groups:
                            collision_groups[name_lower] = [folder_items[name_lower]]
                        collision_groups[name_lower].append(entry.name)
                    else:
                        folder_items[name_lower] = entry.name
            
            # Second pass: process items and add collision issues
            for entry in entries_list:
                self.scan_count += 1
                
                # Progress indicator every 1,000 items
                if self.scan_count % 1000 == 0:
                    self.logger.info(f"Scanned {self.scan_count:,} items...")
                
                try:
                    full_path = entry.path
                    is_file = entry.is_file(follow_symlinks=False)
                    is_dir = entry.is_dir(follow_symlinks=False)
                    
                    # Check this item (use original_root for depth calculation)
                    issues = self.check_item(full_path, original_root, is_file)
                    
                    # Add case-collision issue if applicable
                    name_lower = entry.name.lower()
                    if name_lower in collision_groups:
                        colliding_names = [n for n in collision_groups[name_lower] if n != entry.name]
                        if colliding_names:
                            depth = self.compute_depth(full_path, original_root)
                            file_size_mb = 0.0
                            if is_file:
                                try:
                                    file_size_bytes = retry_with_backoff(os.path.getsize, full_path)
                                    file_size_mb = file_size_bytes / (1024 * 1024)
                                except OSError:
                                    pass
                            
                            issues.append({
                                'ItemType': 'File' if is_file else 'Folder',
                                'FullPath': full_path,
                                'IssueType': 'Case-insensitive duplicate',
                                'CurrentValue': f'{entry.name} (collides with: {", ".join(colliding_names)})',
                                'SuggestedFix': f'Rename to make unique: {entry.name}_1, {entry.name}_2, etc.',
                                'CharacterCount': len(entry.name),
                                'CharacterCountPath': len(full_path),
                                'FileSizeMB': f'{file_size_mb:.2f}' if is_file else '',
                                'FolderDepth': depth
                            })
                    
                    if issues:
                        all_issues.extend(issues)
                        self.issue_count += len(issues)
                        
                        # Write to CSV immediately if streaming
                        if self.csv_writer:
                            for issue in issues:
                                self.csv_writer.write_issue(issue)
                    
                    # Recurse into subdirectories (pass along original_root)
                    if is_dir:
                        sub_issues = self.scan_directory(full_path, original_root)
                        all_issues.extend(sub_issues)
                
                except PermissionError:
                    self.logger.warning(f"Permission denied: {entry.path}")
                except OSError as e:
                    self.logger.warning(f"OS error scanning {entry.path}: {e}")
        
        except PermissionError:
            self.logger.error(f"Permission denied accessing directory: {current_path}")
        except OSError as e:
            self.logger.error(f"OS error accessing {current_path}: {e}")
        
        return all_issues


def write_csv_report(issues: List[dict], output_path: str, logger: logging.Logger):
    """
    Write issue records to CSV with stable column order.
    """
    if not issues:
        logger.info("No issues found. Creating empty report.")
    
    fieldnames = [
        'ItemType',
        'FullPath',
        'IssueType',
        'CurrentValue',
        'SuggestedFix',
        'CharacterCount',
        'CharacterCountPath',
        'FileSizeMB',
        'FolderDepth'
    ]
    
    try:
        # Ensure output directory exists
        output_dir = os.path.dirname(os.path.abspath(output_path))
        if output_dir:  # Only create if there's a directory component
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(issues)
        
        logger.info(f"Report written to: {output_path}")
        logger.info(f"Total issues recorded: {len(issues):,}")
    
    except OSError as e:
        logger.error(f"Failed to write report to {output_path}: {e}")
        logger.error(f"Please ensure the output directory exists and you have write permissions.")
        sys.exit(3)


def setup_logging(log_path: Optional[str] = None) -> logging.Logger:
    """
    Configure logging to console and optionally to a file.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console_fmt = logging.Formatter('%(levelname)s: %(message)s')
    console.setFormatter(console_fmt)
    logger.addHandler(console)
    
    # File handler (optional)
    if log_path:
        try:
            # Ensure log directory exists
            log_dir = os.path.dirname(os.path.abspath(log_path))
            if log_dir:  # Only create if there's a directory component
                os.makedirs(log_dir, exist_ok=True)
            
            file_handler = logging.FileHandler(log_path, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            file_fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_fmt)
            logger.addHandler(file_handler)
        except OSError as e:
            logger.warning(f"Could not create log file {log_path}: {e}")
    
    return logger


def parse_args():
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description='SharePoint Online Migration Preflight Scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan a UNC path
  python spo_preflight.py "\\\\server\\share\\folder"
  
  # Scan with custom output paths
  python spo_preflight.py "C:\\Data" --report "C:\\Reports\\issues.csv" --log "C:\\Reports\\scan.log"
  
  # Custom thresholds
  python spo_preflight.py "\\\\server\\share" --max-path 400 --max-filename 255 --max-file-size-gb 250 --max-depth 20
  
  # Custom blocked extensions
  python spo_preflight.py "C:\\Data" --blocked-extensions .exe .dll .bat .cmd .vbs
        """
    )
    
    parser.add_argument(
        'scan_path',
        help='Root path to scan (local drive or UNC path)'
    )
    
    parser.add_argument(
        '--report',
        default='SPOMigrationReport.csv',
        help='Output CSV report path (default: SPOMigrationReport.csv)'
    )
    
    parser.add_argument(
        '--log',
        default='SPOMigrationLog.txt',
        help='Output log file path (default: SPOMigrationLog.txt)'
    )
    
    parser.add_argument(
        '--max-path',
        type=int,
        default=DEFAULT_MAX_PATH_LENGTH,
        help=f'Maximum path length (default: {DEFAULT_MAX_PATH_LENGTH})'
    )
    
    parser.add_argument(
        '--max-filename',
        type=int,
        default=DEFAULT_MAX_FILENAME_LENGTH,
        help=f'Maximum filename length (default: {DEFAULT_MAX_FILENAME_LENGTH})'
    )
    
    parser.add_argument(
        '--max-file-size-gb',
        type=int,
        default=DEFAULT_MAX_FILE_SIZE_GB,
        help=f'Maximum file size in GB (default: {DEFAULT_MAX_FILE_SIZE_GB})'
    )
    
    parser.add_argument(
        '--max-depth',
        type=int,
        default=DEFAULT_MAX_FOLDER_DEPTH,
        help=f'Maximum folder depth threshold (default: {DEFAULT_MAX_FOLDER_DEPTH})'
    )
    
    parser.add_argument(
        '--blocked-extensions',
        nargs='+',
        default=DEFAULT_BLOCKED_EXTENSIONS,
        help=f'Blocked file extensions (default: {" ".join(DEFAULT_BLOCKED_EXTENSIONS)})'
    )
    
    parser.add_argument(
        '--no-allow-hash-percent',
        dest='allow_hash_percent',
        action='store_false',
        default=True,
        help='Block # %% & characters (most tenants now support these)'
    )
    
    parser.add_argument(
        '--exclude-dirs',
        nargs='*',
        default=DEFAULT_EXCLUDE_DIRS,
        help='Directory names to exclude from scan'
    )
    
    parser.add_argument(
        '--exclude-exts',
        nargs='*',
        default=DEFAULT_EXCLUDE_EXTS,
        help='File extensions to exclude from scan'
    )
    
    parser.add_argument(
        '--workers',
        type=int,
        default=1,
        help='Number of worker threads for parallel scanning (default: 1, recommended: 8 for UNC)'
    )
    
    parser.add_argument(
        '--anonymize',
        action='store_true',
        help='Hash file paths and names for PHI/PII compliance'
    )
    
    parser.add_argument(
        '--progress',
        action='store_true',
        help='Show progress bar with ETA (requires tqdm)'
    )
    
    parser.add_argument(
        '--fail-on-issues',
        action='store_true',
        help='Exit with code 1 if any issues found (for CI/CD)'
    )
    
    parser.add_argument(
        '--summary-json',
        help='Output path for machine-readable JSON summary'
    )
    
    return parser.parse_args()


def main():
    """
    Main entry point.
    """
    args = parse_args()
    
    # Setup logging
    logger = setup_logging(args.log)
    
    logger.info("=" * 70)
    logger.info("SharePoint Online Migration Preflight Scanner v2.0.0")
    logger.info("=" * 70)
    logger.info(f"Scan path: {args.scan_path}")
    logger.info(f"Report output: {args.report}")
    logger.info(f"Log output: {args.log}")
    logger.info(f"Max path length: {args.max_path}")
    logger.info(f"Max filename length: {args.max_filename}")
    logger.info(f"Max file size: {args.max_file_size_gb} GB")
    logger.info(f"Max folder depth: {args.max_depth}")
    logger.info(f"Blocked extensions: {', '.join(args.blocked_extensions)}")
    logger.info(f"Allow # %% & characters: {args.allow_hash_percent}")
    logger.info(f"Exclude directories: {len(args.exclude_dirs)} patterns")
    logger.info(f"Exclude extensions: {len(args.exclude_exts)} patterns")
    if args.workers > 1:
        logger.info(f"Worker threads: {args.workers}")
    if args.anonymize:
        logger.info("Anonymization: ENABLED")
    logger.info("=" * 70)
    
    # Validate scan path
    if not os.path.exists(args.scan_path):
        logger.error(f"Scan path does not exist: {args.scan_path}")
        sys.exit(1)
    
    if not os.path.isdir(args.scan_path):
        logger.error(f"Scan path is not a directory: {args.scan_path}")
        sys.exit(2)
    
    # Initialize scanner
    scanner = PreflightScanner(
        max_path=args.max_path,
        max_filename=args.max_filename,
        max_file_size_gb=args.max_file_size_gb,
        max_depth=args.max_depth,
        blocked_extensions=args.blocked_extensions,
        allow_hash_percent=args.allow_hash_percent,
        exclude_dirs=args.exclude_dirs,
        exclude_exts=args.exclude_exts,
        workers=args.workers,
        anonymize=args.anonymize,
        progress=args.progress,
        stream_csv=True
    )
    
    # Start scan
    start_time = datetime.now()
    logger.info("Scanning started...")
    
    # Use streamed CSV writing
    fieldnames = [
        'ItemType', 'FullPath', 'IssueType', 'CurrentValue', 'SuggestedFix',
        'CharacterCount', 'CharacterCountPath', 'FileSizeMB', 'FolderDepth'
    ]
    
    anonymize_fn = None
    if args.anonymize:
        anonymize_fn = lambda p: anonymize_path(p, scanner.anon_salt)
    
    with StreamedCSVWriter(args.report, fieldnames, anonymize_fn) as csv_writer:
        scanner.csv_writer = csv_writer
        issues = scanner.scan_directory(args.scan_path)
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    # Generate JSON summary if requested
    if args.summary_json:
        # Count by issue type
        issue_counts = {}
        for issue in issues:
            issue_type = issue['IssueType']
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        # Top 50 longest paths
        longest_paths = sorted(
            [{'path': i['FullPath'], 'length': int(i['CharacterCountPath'])} for i in issues],
            key=lambda x: x['length'],
            reverse=True
        )[:50]
        
        # Top 50 deepest folders
        deepest = sorted(
            [{'path': i['FullPath'], 'depth': int(i['FolderDepth'])} for i in issues if i['FolderDepth']],
            key=lambda x: x['depth'],
            reverse=True
        )[:50]
        
        # Top 50 largest files
        largest = sorted(
            [{'path': i['FullPath'], 'size_mb': float(i['FileSizeMB'])} 
             for i in issues if i['FileSizeMB']],
            key=lambda x: x['size_mb'],
            reverse=True
        )[:50]
        
        summary = {
            'scan_timestamp': start_time.isoformat(),
            'scan_path': args.scan_path,
            'total_items_scanned': scanner.scan_count,
            'total_issues': scanner.issue_count,
            'issues_by_type': issue_counts,
            'top_50_longest_paths': longest_paths,
            'top_50_deepest_folders': deepest,
            'top_50_largest_files': largest,
            'scan_duration_seconds': duration.total_seconds()
        }
        
        with open(args.summary_json, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"JSON summary written to: {args.summary_json}")
    
    # Summary
    logger.info("=" * 70)
    logger.info("SCAN COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Total items scanned: {scanner.scan_count:,}")
    logger.info(f"Total issues found: {scanner.issue_count:,}")
    logger.info(f"Duration: {duration}")
    logger.info(f"Report: {args.report}")
    logger.info("=" * 70)
    
    # Exit code handling
    if args.fail_on_issues and scanner.issue_count > 0:
        logger.error(f"FAIL: {scanner.issue_count} issues found. Exiting with code 1.")
        sys.exit(1)
    else:
        sys.exit(0 if scanner.issue_count == 0 else 10)


if __name__ == '__main__':
    main()
