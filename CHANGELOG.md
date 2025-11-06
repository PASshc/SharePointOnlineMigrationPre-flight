# Changelog

All notable changes to the SharePoint Online Migration Preflight Scanner will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-06

### Added
- Initial production release
- Recursive scanning of local and UNC paths
- Comprehensive issue detection:
  - Path length validation (≤400 characters)
  - Filename length validation (≤255 characters)
  - Invalid character detection (`~ " # % & * : < > ? / \ { | }`)
  - Blocked file extension checking (configurable)
  - File size limits (≤250 GB)
  - Leading/trailing spaces or periods detection
  - Folder depth analysis (>20 levels flagged)
- CSV report output with 8 columns:
  - ItemType, FullPath, IssueType, CurrentValue, SuggestedFix, CharacterCount, FileSizeMB, FolderDepth
- Detailed logging to file
- Progress indicators (every 1,000 items)
- Graceful permission error handling
- UNC-aware folder depth calculation
- Configurable thresholds via CLI flags
- UTF-8 CSV output with BOM (Excel-compatible)
- Exit codes for automation (0, 1, 2, 3, 10)
- Suggested fixes for detected issues
- PyInstaller support for standalone EXE

### Features
- Command-line interface with full argument parsing
- Windows batch script launcher (`run_scan.bat`)
- PowerShell launcher with validation (`run_scan.ps1`)
- Test data generator (`create_test_data.py`)
- Comprehensive documentation (README.md, EXAMPLES.md)
- Build script for creating EXE (`build_exe.bat`)

### Technical
- Pure Python 3.10+ implementation
- No external dependencies (standard library only)
- Cross-platform compatible (Windows focus)
- Handles long paths on Windows
- Efficient streaming to CSV (low memory footprint)
- Robust error handling throughout

### Documentation
- Complete README with usage examples
- Microsoft reference links for all checks
- Example configurations for various scenarios
- Build instructions for standalone EXE
- Troubleshooting guide

### Performance
- Scans 10,000-50,000 items per minute (depending on storage)
- Minimal memory footprint
- Progress logging for large scans

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
