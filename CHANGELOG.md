# Changelog

All notable changes to the SharePoint Online Migration Preflight Scanner will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-11-06

### 🔥 CRITICAL FIX - SharePoint URL Validation

**Breaking Discovery**: Previous versions (≤2.0.0) validated LOCAL path lengths instead of SharePoint URL lengths, causing **false negatives** that would result in migration failures.

### Added
- **Interactive Wizard Mode** (`--interactive` or `-i`):
  - Step-by-step guided setup for SharePoint destination configuration
  - Automatic URL format validation for SharePoint vs OneDrive
  - Real-time overhead calculation and effective path limit display
  - Path existence validation with retry prompts
  - Configuration summary before scan execution
- **SharePoint URL Validation**:
  - Calculates actual SharePoint URL lengths (not just local paths)
  - URL-encodes path components for accurate byte count
  - Distinguishes between SharePoint and OneDrive destinations
  - Validates URL formats with comprehensive error messages
- **New CLI Parameters**:
  - `--interactive` / `-i`: Launch interactive wizard
  - `--spo-url`: SharePoint tenant URL
  - `--spo-library`: Document library or Teams channel name
  - `--onedrive`: Flag for OneDrive for Business destination
  - `--spo-overhead`: Manual overhead estimate (default: 80 chars)
- **Enhanced CSV Report Columns**:
  - `SharePointURL`: Full SharePoint URL that will be created during migration
  - `LocalPathLength`: Local Windows path length (reference only)
  - `CharacterCountPath`: Now shows **SharePoint URL length** (primary validation)

### Changed
- **Path Length Validation Logic** (CRITICAL):
  - OLD: Checked local path `C:\Data\file.txt` length
  - NEW: Checks SharePoint URL `https://tenant.sharepoint.com/sites/Team/Shared Documents/file.txt` length
  - Accounts for tenant URL, site path, library name, and URL encoding overhead
  - Effective path limit = 400 - overhead (typically 320-350 characters)
- **Scanner Initialization**:
  - Now requires `scan_root` parameter to calculate relative paths
  - Accepts optional `spo_url`, `spo_library`, `is_onedrive` parameters
  - Calculates SharePoint URL base and overhead automatically
- **Version**: Updated from 2.0.0 to 2.1.0 in main() logging

### Fixed
- **False Negatives in Path Validation**: Files with 320-char local paths but 420-char SharePoint URLs now correctly flagged as errors
- **URL Format Validation**: OneDrive URLs (`-my.sharepoint.com`) properly distinguished from SharePoint URLs
- **Case-Collision Issues**: Now include SharePoint URL and path length metadata

### Documentation
- Added `INTERACTIVE_MODE.md`: Complete guide to interactive wizard
- Updated `README.md`: New quick start with interactive mode
- Updated help text: Examples for both interactive and CLI modes

### Impact Assessment

**Before v2.1.0 (FALSE NEGATIVES):**
```
Local Path: C:\Data\Project\Folder\File.xlsx (85 chars)
✅ Scanner: PASS (under 400)
❌ Migration: FAIL (SharePoint URL is 405 chars)
```

**After v2.1.0 (ACCURATE):**
```
Local Path: C:\Data\Project\Folder\File.xlsx (85 chars)
SharePoint URL: https://contoso.sharepoint.com/sites/Team/Shared Documents/Project/Folder/File.xlsx (405 chars)
❌ Scanner: FAIL (over 400)
✅ Migration: Pre-emptively caught and flagged
```

### Migration Guide (v2.0.0 → v2.1.0)

**For Users:**
1. **Re-scan all previously scanned locations** using interactive mode or `--spo-url` parameter
2. Previous scan reports likely contain **false negatives** (files marked OK that will fail)
3. Use new `SharePointURL` column to see actual URLs that will be created

**CLI Changes:**
- `scan_path` is now **optional** if using `--interactive`
- When using `--spo-url`, provide the full tenant/site URL
- OneDrive URLs must contain `-my` (e.g., `https://contoso-my.sharepoint.com`)
- Use `--onedrive` flag to auto-set library to "Documents"

**Backward Compatibility:**
- Legacy mode (no SharePoint URL) still works but uses estimated overhead
- Old command syntax still valid: `python spo_preflight.py "C:\Data"`
- Warning logged when SharePoint URL not configured

### Technical Details

**URL Overhead Components:**
| Component | Example | Typical Length |
|-----------|---------|----------------|
| Protocol | `https://` | 8 chars |
| Tenant | `contoso.sharepoint.com` | 25-35 chars |
| Site Path | `/sites/Team` | 10-20 chars |
| Library | `/Shared%20Documents/` | 15-30 chars |
| **Total Overhead** | | **50-120 chars** |

**Effective Path Limits:**
- Low overhead (50 chars): 350 chars remaining
- Medium overhead (80 chars): 320 chars remaining
- High overhead (120 chars): 280 chars remaining

### Security
- No changes to anonymization features
- URL validation does not transmit data to external services
- All processing remains local

---

## [2.0.0] - 2025-11-06

### Added
- Streaming CSV writer for memory efficiency
- Case-insensitive filename collision detection
- Reserved device name checking (CON, PRN, AUX, NUL, COM1-9, LPT1-9)
- SharePoint-specific reserved patterns (_vti_, .lock, desktop.ini, ~$)
- Retry logic with exponential backoff for transient errors
- PHI/PII anonymization mode with path hashing
- JSON summary report with top 50 insights
- Progress bar support (optional tqdm dependency)
- Configurable exclusion lists for directories and extensions
- `--fail-on-issues` flag for CI/CD integration
- Multi-threaded scanning capability (experimental)

### Changed
- CSV format: Added `CharacterCountPath` column
- Depth calculation: Now relative to scan root (not drive root)
- File size reporting: Now in MB for readability
- Exit codes: 0 (success), 1 (error), 10 (issues found)

### Fixed
- UNC path depth calculation accuracy
- Permission error handling for locked files
- Memory usage for large directory scans

---

## [1.0.0] - 2025-11-06

### Added
- Initial production release
- Recursive scanning of local and UNC paths
- Comprehensive issue detection:
  - Path length validation (≤400 characters) **[NOTE: v2.1.0 fixes validation logic]**
  - Filename length validation (≤255 characters)
  - Invalid character detection (`~ " # % & * : < > ? / \ { | }`)
  - Blocked file extension checking (configurable)
  - File size limits (≤250 GB)
  - Leading/trailing spaces or periods detection
  - Folder depth analysis (>20 levels flagged)
- CSV report output with columns
- Detailed logging to file
- Progress indicators (every 1,000 items)
- Graceful permission error handling
- Configurable thresholds via CLI flags
- UTF-8 CSV output with BOM (Excel-compatible)
- Exit codes for automation
- Suggested fixes for detected issues
- PyInstaller support for standalone EXE

### Features
- Command-line interface with full argument parsing
- Windows batch script launcher (`run_scan.bat`)
- PowerShell launcher with validation (`run_scan.ps1`)
- Test data generator (`create_test_data.py`)
- Comprehensive documentation
- Build script for creating EXE (`build_exe.bat`)

### Technical
- Pure Python 3.10+ implementation
- No external dependencies (standard library only)
- Cross-platform compatible (Windows focus)
- Handles long paths on Windows
- Efficient streaming to CSV
- Robust error handling throughout

---

## [Unreleased]

### Planned Features
- [ ] GUI wrapper (Tkinter)
- [ ] Windows Explorer context menu integration
- [ ] HTML report generation
- [ ] Excel XLSX output option
- [ ] Parallel scanning for improved performance
- [ ] Remediation automation (auto-fix mode)
- [ ] SharePoint Online site URL validation
- [ ] Migration wave planning features
- [ ] Azure File Share support
- [ ] Office 365 tenant configuration import
- [ ] Custom rule engine
- [ ] Email report delivery
- [ ] Scheduled scanning (Windows Task Scheduler integration)
- [ ] Power BI dashboard template
- [ ] Multi-language support

### Known Limitations
- Very deep folder structures (>25 levels) may cause OS errors on some systems
- Files/folders with names containing `:` or `|` cannot be created on Windows (logged as warnings)
- Network share scanning speed depends on network latency
- No built-in remediation (reports only)

### Compatibility
- **Tested on:**
  - Windows 10 (21H2, 22H2)
  - Windows 11 (22H2, 23H2)
  - Windows Server 2019, 2022
- **Python versions:**
  - Python 3.10+
  - Python 3.11 (recommended)
  - Python 3.12 (tested)

---

## Version History

### Version Numbering
- **Major.Minor.Patch** (e.g., 1.0.0)
- **Major:** Breaking changes or significant new features
- **Minor:** New features, backward compatible
- **Patch:** Bug fixes, minor improvements

### Release Notes

#### 1.0.0 - Initial Release (2025-11-06)
First production-ready release of the SharePoint Online Migration Preflight Scanner.
Built for Stanford Health Care DSS migration project.

**Highlights:**
- Complete SharePoint Online validation rule set
- Enterprise-ready error handling
- Flexible configuration options
- Professional documentation
- Standalone EXE support

**Built by:** 818Ninja  
**Project:** Stanford Health Care SharePoint Migration  
**License:** MIT

---

## Contributing

Feature requests and bug reports can be submitted to your IT department or project maintainer.

## Support

For issues or questions:
1. Check the README.md troubleshooting section
2. Review EXAMPLES.md for usage patterns
3. Contact your IT department or migration team
