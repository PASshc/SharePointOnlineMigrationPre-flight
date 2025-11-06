# SharePoint Online Migration Preflight Scanner - Improvement Roadmap

**Last Updated:** November 6, 2025  
**Project:** Stanford Health Care DSS SharePoint Migration  
**Version:** 1.0.0 → 2.0.0

---

## Executive Summary

This roadmap outlines critical improvements to transform the scanner from a diagnostic tool into a production-grade, enterprise-ready migration platform. Focus is on **accuracy, performance, and actionable remediation**.

---

## Phase 1: Critical Compliance & Accuracy Fixes 🔴 SHIP THIS WEEK

### 1.1 Reserved Device Names Check (Windows) ⚠️ CRITICAL
**Priority:** P0  
**Effort:** 15 minutes  
**Status:** 🔴 Not Started

**Problem:** Files/folders named CON, PRN, AUX, NUL, COM1-COM9, LPT1-LPT9, .lock, desktop.ini, _vti_, or starting with ~$ cause **silent migration failures** in OneDrive/SharePoint.

**Implementation:**
```python
RESERVED_NAMES = {
    'CON', 'PRN', 'AUX', 'NUL',
    'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
    'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
}
RESERVED_PATTERNS = ['.lock', 'desktop.ini', '_vti_']
TEMP_PREFIX = '~$'

def check_reserved_name(name: str) -> bool:
    """Check if name is a Windows reserved device name."""
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
    if '_vti_' in name.lower():
        return True
    
    return False
```

**Issue Type:** `Reserved device name (Windows)`  
**Suggested Fix:** `Rename to {name}_file or {name}_folder`  
**Reference:** [Microsoft Support - Reserved names](https://support.microsoft.com/en-us/office/invalid-file-names-and-file-types-in-onedrive-and-sharepoint-64883a5d-228e-48f5-b3d2-eb39e07630fa)

---

### 1.2 Case-Collision Detection (Per Folder) 🎯 CRITICAL
**Priority:** P0  
**Effort:** 20 minutes  
**Status:** 🔴 Not Started

**Problem:** SharePoint paths are case-preserving but case-insensitive for uniqueness. `Readme.txt` and `README.txt` in the same folder cause upload conflicts and "duplicate file name" sync errors.

**Implementation:**
```python
def scan_directory(self, current_path: str, original_root: str = None) -> List[dict]:
    """Scan directory and detect case-insensitive collisions."""
    # ... existing code ...
    
    # Track names in this folder (case-insensitive)
    folder_items = {}  # key: lowercase name, value: original name
    collision_groups = {}  # key: lowercase name, value: list of original names
    
    with os.scandir(current_path) as entries:
        for entry in entries:
            name_lower = entry.name.lower()
            
            if name_lower in folder_items:
                # Collision detected!
                if name_lower not in collision_groups:
                    collision_groups[name_lower] = [folder_items[name_lower]]
                collision_groups[name_lower].append(entry.name)
            else:
                folder_items[name_lower] = entry.name
    
    # Report collisions
    for lower_name, original_names in collision_groups.items():
        for name in original_names:
            issues.append({
                'ItemType': 'File' if os.path.isfile(...) else 'Folder',
                'FullPath': full_path,
                'IssueType': 'Case-insensitive duplicate',
                'CurrentValue': f'{name} (collides with: {", ".join([n for n in original_names if n != name])})',
                'SuggestedFix': f'{name}_1, {name}_2, etc.',
                'CharacterCount': len(name),
                'CharacterCountPath': len(full_path),
                'FileSizeMB': file_size_mb if is_file else '',
                'FolderDepth': depth
            })
```

**Issue Type:** `Case-insensitive duplicate`  
**Current Value:** `Readme.txt (collides with: README.txt, readme.TXT)`  
**Suggested Fix:** `Rename to make case differences meaningful: Readme_personal.txt, README_project.txt`  
**Reference:** [Microsoft Support - Case sensitivity](https://support.microsoft.com/en-us/office/invalid-file-names-and-file-types-in-onedrive-and-sharepoint-64883a5d-228e-48f5-b3d2-eb39e07630fa)

---

### 1.3 Streamed CSV Writing 💾 HIGH
**Priority:** P0  
**Effort:** 10 minutes  
**Status:** 🔴 Not Started

**Problem:** Current implementation holds all issues in memory. For scans with 100K+ issues, this causes memory bloat and slow CSV writes.

**Implementation:**
```python
class StreamedCSVWriter:
    """Write CSV rows as issues are found, not all at once."""
    
    def __init__(self, output_path: str, fieldnames: List[str]):
        self.output_path = output_path
        self.fieldnames = fieldnames
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
        """Write a single issue immediately."""
        self.writer.writerow(issue)
        self.issue_count += 1
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()

# Usage in scan_directory:
with StreamedCSVWriter(report_path, fieldnames) as csv_writer:
    for issue in scanner.scan_directory(scan_path):
        csv_writer.write_issue(issue)
```

**Benefit:** Scans 1M+ items without memory issues. CSV writes incrementally.

---

### 1.4 Character Policy: # and % Tenant Variability 📋 HIGH
**Priority:** P1  
**Effort:** 10 minutes  
**Status:** 🔴 Not Started

**Problem:** Many tenants now support `#` and `%`, but some orgs still block them. Scanner needs to be configurable.

**Implementation:**
```python
# Add to argument parser
parser.add_argument(
    '--allow-hash-percent',
    action='store_true',
    default=True,
    help='Allow # and %% characters (most tenants support these now, but some block them)'
)

# Update INVALID_CHARS based on flag
def get_invalid_chars(allow_hash_percent: bool) -> set:
    """Get invalid character set based on tenant policy."""
    base_chars = set('~"*:<>?/\\{|}')
    if not allow_hash_percent:
        base_chars.update('#%')
    return base_chars
```

**CLI Usage:**
```bash
# Default: allows # and %
python spo_preflight.py "C:\Data"

# Strict mode: blocks # and %
python spo_preflight.py "C:\Data" --no-allow-hash-percent
```

**Reference:** [Microsoft Support - Character restrictions](https://support.microsoft.com/en-us/office/invalid-file-names-and-file-types-in-onedrive-and-sharepoint-64883a5d-228e-48f5-b3d2-eb39e07630fa)

---

### 1.5 Exclusions & Filters ⚡ HIGH
**Priority:** P1  
**Effort:** 15 minutes  
**Status:** 🔴 Not Started

**Problem:** Scans include system folders ($RECYCLE.BIN, System Volume Information) and development artifacts (node_modules, .git) that will never be migrated. This wastes time and fills reports with noise.

**Implementation:**
```python
DEFAULT_EXCLUDE_DIRS = [
    '$RECYCLE.BIN', 'System Volume Information', '$Recycle.Bin',
    'node_modules', '.git', '.svn', '__pycache__', '.venv',
    'Thumbs.db', '.DS_Store'
]

DEFAULT_EXCLUDE_EXTS = [
    '.tmp', '.temp', '.bak', '.log', '.cache'
]

parser.add_argument(
    '--exclude-dirs',
    nargs='*',
    default=DEFAULT_EXCLUDE_DIRS,
    help='Directory names to exclude from scan (space-separated)'
)

parser.add_argument(
    '--exclude-exts',
    nargs='*',
    default=DEFAULT_EXCLUDE_EXTS,
    help='File extensions to exclude from scan (space-separated)'
)

def should_exclude(entry_name: str, is_dir: bool, exclude_dirs: List[str], exclude_exts: List[str]) -> bool:
    """Check if item should be excluded from scan."""
    if is_dir:
        return entry_name in exclude_dirs
    else:
        _, ext = os.path.splitext(entry_name)
        return ext.lower() in exclude_exts
```

**Benefit:** 10-50x faster scans on development repos and file shares with system folders.

---

## Phase 2: Actionable Remediation 🟡 SHIP NEXT WEEK

### 2.1 Auto-Generate PowerShell Remediation Script 🔧 VERY HIGH VALUE
**Priority:** P1  
**Effort:** 45 minutes  
**Status:** 🔴 Not Started

**Problem:** Users get a CSV of issues but ask "what do I do now?" They need an **executable remediation plan**.

**Implementation:**
Generate `RemediateNames.ps1` alongside CSV report:

```powershell
# RemediateNames.ps1
# Auto-generated by SPO Preflight Scanner v2.0.0
# Generated: 2025-11-06 10:45:23
# Source CSV: SPOMigrationReport_20251106_104523.csv

[CmdletBinding(SupportsShouldProcess=$true)]
param(
    [switch]$WhatIf
)

$ErrorActionPreference = 'Stop'
$renameLog = @()

# Read remediation plan
$issues = Import-Csv "SPOMigrationReport_20251106_104523.csv"

# Group by folder to detect collisions
$byFolder = $issues | Group-Object {Split-Path $_.FullPath}

foreach ($folder in $byFolder) {
    $usedNames = @{}
    
    foreach ($issue in $folder.Group) {
        $oldPath = $issue.FullPath
        $oldName = Split-Path $oldPath -Leaf
        $newName = $issue.SuggestedFix
        
        # Handle collision: if newName already used, append hash
        if ($usedNames.ContainsKey($newName.ToLower())) {
            $hash = ($oldName | Get-FileHash -Algorithm MD5).Hash.Substring(0,6)
            $base = [IO.Path]::GetFileNameWithoutExtension($newName)
            $ext = [IO.Path]::GetExtension($newName)
            $newName = "${base}_${hash}${ext}"
        }
        
        $usedNames[$newName.ToLower()] = $true
        $newPath = Join-Path (Split-Path $oldPath) $newName
        
        if (Test-Path $oldPath) {
            try {
                if ($PSCmdlet.ShouldProcess($oldPath, "Rename to $newName")) {
                    Rename-Item -Path $oldPath -NewName $newName -Force
                    $renameLog += [PSCustomObject]@{
                        Status = 'Success'
                        OldPath = $oldPath
                        NewPath = $newPath
                        IssueType = $issue.IssueType
                    }
                }
            }
            catch {
                $renameLog += [PSCustomObject]@{
                    Status = 'Failed'
                    OldPath = $oldPath
                    NewPath = $newPath
                    Error = $_.Exception.Message
                }
            }
        }
    }
}

# Export log
$renameLog | Export-Csv "RemediationLog_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv" -NoTypeInformation

Write-Host "`nRemediation complete. Log saved to RemediationLog_*.csv" -ForegroundColor Green
```

**Python Generator:**
```python
def write_remediation_script(issues: List[dict], csv_path: str, output_dir: str):
    """Generate PowerShell remediation script."""
    script_path = os.path.join(output_dir, 'RemediateNames.ps1')
    
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(REMEDIATION_SCRIPT_TEMPLATE.format(
            version='2.0.0',
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            csv_file=os.path.basename(csv_path)
        ))
    
    logger.info(f"Remediation script written to: {script_path}")
    logger.info("Run with: powershell -ExecutionPolicy Bypass -File RemediateNames.ps1 -WhatIf")
```

**User Workflow:**
```bash
# 1. Scan
python spo_preflight.py "C:\Data" --report report.csv

# 2. Review
# Open report.csv in Excel

# 3. Dry-run
powershell -File RemediateNames.ps1 -WhatIf

# 4. Execute
powershell -File RemediateNames.ps1

# 5. Verify
python spo_preflight.py "C:\Data" --report report_after.csv
```

---

### 2.2 --fail-on-issues for CI 🤖 MEDIUM-HIGH
**Priority:** P2  
**Effort:** 5 minutes  
**Status:** 🔴 Not Started

**Implementation:**
```python
parser.add_argument(
    '--fail-on-issues',
    action='store_true',
    help='Exit with non-zero code if any issues are found (for CI/CD gates)'
)

# At end of main():
if args.fail_on_issues and scanner.issue_count > 0:
    logger.error(f"FAIL: {scanner.issue_count} issues found. Exiting with code 1.")
    sys.exit(1)
else:
    sys.exit(0 if scanner.issue_count == 0 else 10)
```

**CI Usage:**
```yaml
# Azure Pipelines / GitHub Actions
- name: Scan for SPO Issues
  run: |
    python spo_preflight.py "$(Build.SourcesDirectory)" \
      --report scan_results.csv \
      --fail-on-issues
  continueOnError: false
```

---

### 2.3 --summary-json for Dashboards 📊 MEDIUM-HIGH
**Priority:** P2  
**Effort:** 20 minutes  
**Status:** 🔴 Not Started

**Implementation:**
```python
def write_summary_json(scanner: PreflightScanner, issues: List[dict], output_path: str):
    """Write machine-readable summary for dashboards."""
    
    # Count by issue type
    issue_counts = {}
    for issue in issues:
        issue_type = issue['IssueType']
        issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
    
    # Top 50 longest paths
    longest_paths = sorted(
        [{'path': i['FullPath'], 'length': i['CharacterCountPath']} for i in issues],
        key=lambda x: x['length'],
        reverse=True
    )[:50]
    
    # Deepest folders
    deepest = sorted(
        [{'path': i['FullPath'], 'depth': i['FolderDepth']} for i in issues],
        key=lambda x: x['depth'],
        reverse=True
    )[:50]
    
    # Largest files
    largest = sorted(
        [{'path': i['FullPath'], 'size_mb': float(i['FileSizeMB'])} 
         for i in issues if i['FileSizeMB']],
        key=lambda x: x['size_mb'],
        reverse=True
    )[:50]
    
    summary = {
        'scan_timestamp': datetime.now().isoformat(),
        'scan_path': scanner.scan_path,
        'total_items_scanned': scanner.scan_count,
        'total_issues': scanner.issue_count,
        'issues_by_type': issue_counts,
        'top_50_longest_paths': longest_paths,
        'top_50_deepest_folders': deepest,
        'top_50_largest_files': largest,
        'scan_duration_seconds': scanner.duration.total_seconds()
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
```

**Dashboard Integration:**
```javascript
// Power BI / Grafana / Custom Dashboard
fetch('/api/scan_summary.json')
  .then(r => r.json())
  .then(data => {
    renderChart('issues-by-type', data.issues_by_type);
    renderTable('longest-paths', data.top_50_longest_paths);
  });
```

---

### 2.4 Progress Bar with tqdm 📈 MEDIUM
**Priority:** P2  
**Effort:** 10 minutes  
**Status:** 🔴 Not Started

**Implementation:**
```python
# requirements.txt
tqdm>=4.66.0

# In scanner
parser.add_argument(
    '--progress',
    action='store_true',
    help='Show progress bar with ETA'
)

def scan_directory(self, current_path: str, original_root: str = None, pbar=None) -> List[dict]:
    """Scan with optional progress bar."""
    
    with os.scandir(current_path) as entries:
        for entry in entries:
            self.scan_count += 1
            
            if pbar:
                pbar.update(1)
                pbar.set_postfix({
                    'issues': self.issue_count,
                    'current': entry.name[:30]
                })
            
            # ... rest of scan logic ...

# In main():
if args.progress:
    from tqdm import tqdm
    with tqdm(desc="Scanning", unit=" items") as pbar:
        issues = scanner.scan_directory(args.scan_path, pbar=pbar)
else:
    issues = scanner.scan_directory(args.scan_path)
```

**Output:**
```
Scanning: 24,905 items [00:01<00:00, 17,234.56 items/s, issues=328, current=report.xlsx]
```

---

## Phase 3: Performance & Scale 🟢 SHIP WITHIN 2 WEEKS

### 3.1 ThreadPool Workers for UNC/SMB 🏃 MEDIUM
**Priority:** P2  
**Effort:** 30 minutes  
**Status:** 🔴 Not Started

**Problem:** Single-threaded directory walks on SMB/UNC paths are slow due to network latency. Multi-threading I/O operations can speed up scans by 5-10x.

**Implementation:**
```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue

parser.add_argument(
    '--workers',
    type=int,
    default=1,
    help='Number of worker threads for parallel scanning (default: 1, recommended: 8 for UNC)'
)

def scan_directory_parallel(self, root_path: str, workers: int = 1) -> List[dict]:
    """Scan directory tree using thread pool for I/O parallelism."""
    
    if workers == 1:
        return self.scan_directory(root_path)  # Fall back to single-threaded
    
    all_issues = []
    folder_queue = Queue()
    folder_queue.put((root_path, root_path))  # (current_path, original_root)
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = []
        
        while not folder_queue.empty() or futures:
            # Submit work for folders in queue
            while not folder_queue.empty() and len(futures) < workers * 2:
                current_path, original_root = folder_queue.get()
                future = executor.submit(self._scan_folder_worker, current_path, original_root, folder_queue)
                futures.append(future)
            
            # Collect completed work
            for future in as_completed(futures):
                issues = future.result()
                all_issues.extend(issues)
                futures.remove(future)
                break
    
    return all_issues

def _scan_folder_worker(self, current_path: str, original_root: str, folder_queue: Queue) -> List[dict]:
    """Worker function to scan a single folder."""
    issues = []
    
    try:
        with os.scandir(current_path) as entries:
            for entry in entries:
                self.scan_count += 1
                
                # Check item
                item_issues = self.check_item(entry.path, original_root, entry.is_file())
                issues.extend(item_issues)
                
                # Queue subdirectories
                if entry.is_dir(follow_symlinks=False):
                    folder_queue.put((entry.path, original_root))
    
    except (PermissionError, OSError) as e:
        self.logger.warning(f"Error scanning {current_path}: {e}")
    
    return issues
```

**Usage:**
```bash
# Single-threaded (default)
python spo_preflight.py "\\server\share\data"

# 8 workers (recommended for UNC)
python spo_preflight.py "\\server\share\data" --workers 8
```

**Benefit:** 5-10x faster on network shares with high latency.

---

### 3.2 Graceful Retry & Backoff 🔄 MEDIUM
**Priority:** P2  
**Effort:** 20 minutes  
**Status:** 🔴 Not Started

**Problem:** Transient errors (WinError 64 "file in use", WinError 121 "semaphore timeout", WinError 53 "network path not found") fail scans unnecessarily.

**Implementation:**
```python
import time
import random

MAX_RETRIES = 3
BASE_DELAY = 0.5  # seconds

def retry_with_backoff(func, *args, max_retries=MAX_RETRIES, **kwargs):
    """Retry function with exponential backoff and jitter."""
    
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except (PermissionError, OSError) as e:
            if attempt == max_retries - 1:
                raise  # Give up
            
            # Check if error is transient
            if e.winerror in [64, 121, 53, 32]:  # File in use, timeout, network error, sharing violation
                delay = BASE_DELAY * (2 ** attempt)  # Exponential
                jitter = random.uniform(0, delay * 0.1)  # 10% jitter
                time.sleep(delay + jitter)
                continue
            else:
                raise  # Not transient, give up

# Usage:
try:
    file_size = retry_with_backoff(os.path.getsize, full_path)
except OSError as e:
    logger.warning(f"Could not get size after {MAX_RETRIES} retries: {e}")
```

---

### 3.3 --anonymize for PHI/PII Compliance 🔒 MEDIUM
**Priority:** P2  
**Effort:** 15 minutes  
**Status:** 🔴 Not Started

**Problem:** Healthcare/finance orgs cannot share reports with vendors because file paths contain PHI/PII (patient names, SSNs in folder names, etc.).

**Implementation:**
```python
import hashlib

parser.add_argument(
    '--anonymize',
    action='store_true',
    help='Hash file paths and names in report (for sharing with vendors)'
)

def anonymize_path(path: str, salt: str) -> str:
    """Hash path while preserving structure."""
    parts = path.split(os.sep)
    hashed_parts = []
    
    for part in parts:
        if part:  # Skip empty parts
            h = hashlib.sha256(f"{salt}{part}".encode()).hexdigest()[:16]
            hashed_parts.append(h)
        else:
            hashed_parts.append(part)
    
    return os.sep.join(hashed_parts)

# In main():
if args.anonymize:
    import secrets
    ANON_SALT = secrets.token_hex(16)
    logger.info(f"Anonymization enabled. Salt: {ANON_SALT} (save this to de-anonymize)")
    
    for issue in issues:
        issue['FullPath'] = anonymize_path(issue['FullPath'], ANON_SALT)
        issue['CurrentValue'] = anonymize_path(issue['CurrentValue'], ANON_SALT)
```

**Output:**
```
INFO: Anonymization enabled. Salt: 3f8a9c2b... (save this to de-anonymize)
```

**CSV:**
```
FullPath: C:\7d3f21a\4e5b2c8\9a1d3f5\report.xlsx
```

---

## Success Metrics

### Phase 1 (Critical Fixes)
- ✅ Zero false negatives on reserved device names
- ✅ 100% accuracy on case-collision detection
- ✅ Scan 1M+ items without memory issues
- ✅ 50% fewer false positives on # and % characters

### Phase 2 (Remediation)
- ✅ 90% of users run remediation script successfully
- ✅ CI integration in Azure Pipelines / GitHub Actions
- ✅ Executive dashboard with summary stats
- ✅ 80% of users report "progress bar is helpful"

### Phase 3 (Performance)
- ✅ 5-10x faster UNC scans with --workers 8
- ✅ 95% reduction in transient error failures
- ✅ Healthcare/finance orgs can share anonymized reports

---

## Testing Strategy

### Unit Tests (Phase 1 & 2)
```python
# tests/test_reserved_names.py
def test_reserved_device_names():
    assert check_reserved_name('CON') == True
    assert check_reserved_name('con.txt') == True
    assert check_reserved_name('LPT9.xlsx') == True
    assert check_reserved_name('~$report.xlsx') == True
    assert check_reserved_name('desktop.ini') == True
    assert check_reserved_name('_vti_cnf') == True
    assert check_reserved_name('normal.txt') == False

def test_case_collision():
    issues = detect_collisions(['README.md', 'readme.md', 'ReadMe.MD'])
    assert len(issues) == 3
    assert all('Case-insensitive duplicate' in i['IssueType'] for i in issues)

def test_depth_calculation():
    assert compute_depth('C:\\a\\b\\c', 'C:\\a') == 2
    assert compute_depth('\\\\server\\share\\a\\b', '\\\\server\\share') == 2
```

### Integration Tests (Phase 2 & 3)
```python
# tests/test_integration.py
def test_full_scan_with_exclusions():
    scanner = PreflightScanner()
    issues = scanner.scan_directory(
        test_data_path,
        exclude_dirs=['node_modules', '.git']
    )
    assert 'node_modules' not in str(issues)

def test_remediation_script_generation():
    write_remediation_script(sample_issues, 'report.csv', output_dir)
    assert os.path.exists(os.path.join(output_dir, 'RemediateNames.ps1'))

def test_parallel_scan():
    issues_single = scanner.scan_directory(test_path, workers=1)
    issues_parallel = scanner.scan_directory(test_path, workers=8)
    assert len(issues_single) == len(issues_parallel)
```

---

## Implementation Checklist

### Phase 1: Critical Fixes (Week 1)
- [ ] 1.1 Reserved device names check
- [ ] 1.2 Case-collision detection
- [ ] 1.3 Streamed CSV writing
- [ ] 1.4 --allow-hash-percent flag
- [ ] 1.5 Exclusions (--exclude-dirs, --exclude-exts)
- [ ] Unit tests for Phase 1
- [ ] Update README.md with new flags
- [ ] Update CHANGELOG.md → v2.0.0-alpha

### Phase 2: Remediation (Week 2)
- [ ] 2.1 Auto-generate PowerShell remediation script
- [ ] 2.2 --fail-on-issues flag
- [ ] 2.3 --summary-json output
- [ ] 2.4 Progress bar (--progress)
- [ ] Integration tests for Phase 2
- [ ] Update QUICKREF.md with new workflows
- [ ] Update CHANGELOG.md → v2.0.0-beta

### Phase 3: Performance (Week 3-4)
- [ ] 3.1 ThreadPool workers (--workers N)
- [ ] 3.2 Retry with backoff
- [ ] 3.3 --anonymize for compliance
- [ ] Performance benchmarks
- [ ] Load testing (1M+ items)
- [ ] Update CHANGELOG.md → v2.0.0-rc1

### Release (Week 4)
- [ ] Full regression testing
- [ ] User acceptance testing with Stanford Health Care DSS team
- [ ] Documentation review
- [ ] Tag v2.0.0
- [ ] Push to GitHub

---

## Notes

- **No Phase 4 (Enterprise)** until after GitHub push and user feedback
- Focus on **production-grade reliability** for Stanford Health Care DSS migration
- Keep changes **backward-compatible** where possible
- Maintain **single-file simplicity** for easy deployment

---

## References

- [Microsoft: Invalid file names and file types in OneDrive and SharePoint](https://support.microsoft.com/en-us/office/invalid-file-names-and-file-types-in-onedrive-and-sharepoint-64883a5d-228e-48f5-b3d2-eb39e07630fa)
- [Microsoft: Restrictions and limitations in OneDrive and SharePoint](https://support.microsoft.com/en-us/office/restrictions-and-limitations-in-onedrive-and-sharepoint-64883a5d-228e-48f5-b3d2-eb39e07630fa)
- [Microsoft: SharePoint limits](https://learn.microsoft.com/en-us/office365/servicedescriptions/sharepoint-online-service-description/sharepoint-online-limits)
