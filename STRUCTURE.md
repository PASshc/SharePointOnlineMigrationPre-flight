# SharePoint Online Migration Preflight Scanner
## Project Structure

```
SPOMigrationPre-Flight_v2/
│
├── 📄 spo_preflight.py          # Main scanner script (production-ready)
│   ├── PreflightScanner class    # Core scanning logic
│   ├── Issue detection methods   # 7 comprehensive checks
│   ├── CSV output writer         # UTF-8 with BOM
│   └── CLI argument parser       # Full configuration support
│
├── 🚀 Launcher Scripts
│   ├── run_scan.bat              # Windows batch launcher (drag-and-drop friendly)
│   ├── run_scan.ps1              # PowerShell launcher (interactive with validation)
│   └── build_exe.bat             # Automated EXE build script
│
├── 📖 Documentation
│   ├── README.md                 # Comprehensive user guide
│   ├── QUICKREF.md               # One-page quick reference
│   ├── EXAMPLES.md               # Configuration examples and scenarios
│   ├── CHANGELOG.md              # Version history and roadmap
│   └── LICENSE                   # MIT License
│
├── 🧪 Testing & Development
│   ├── create_test_data.py       # Test structure generator
│   ├── requirements.txt          # Python dependencies (none required!)
│   └── .gitignore               # Version control exclusions
│
└── 🏗️ Build Configuration
    └── spo_preflight.spec        # PyInstaller spec (advanced EXE builds)

```

## Component Overview

### Core Script (`spo_preflight.py`)
**Lines of Code:** ~600  
**Dependencies:** Python 3.10+ standard library only  
**Key Classes:**
- `PreflightScanner` - Main scanning engine
  - `check_item()` - Individual file/folder validation
  - `scan_directory()` - Recursive traversal
  - `suggest_fix()` - Remediation suggestions

**Validation Rules Implemented:**
1. ✅ Path length (≤400 chars) - Microsoft SPO limit
2. ✅ Filename length (≤255 chars) - Practical limit
3. ✅ Invalid characters - SPO restricted chars
4. ✅ Blocked extensions - Configurable security policy
5. ✅ File size (≤250 GB) - Microsoft upload limit
6. ✅ Leading/trailing spaces/periods - Sync blockers
7. ✅ Folder depth (>20 levels) - Best practice threshold

### Launcher Scripts

#### `run_scan.bat`
- Simple double-click execution
- Drag-and-drop path support
- Timestamped outputs
- Auto-opens report in Excel
- Progress feedback

#### `run_scan.ps1`
- Interactive PowerShell interface
- Path validation before scan
- Color-coded output
- Professional formatting
- Error handling with user prompts

#### `build_exe.bat`
- One-click EXE creation
- PyInstaller wrapper
- Automatic cleanup
- Build verification
- Optional testing

### Documentation Suite

#### README.md (Primary Reference)
- Quick start guide
- Complete feature list
- Configuration options
- Microsoft reference links
- Troubleshooting section
- EXE build instructions

#### QUICKREF.md (Cheat Sheet)
- One-page reference
- Common commands
- Excel filtering tips
- Power user tricks
- Exit code reference

#### EXAMPLES.md (Scenarios)
- 5 pre-configured scenarios
- Stanford Health Care settings
- Batch processing scripts
- Multi-share scanning
- Custom configurations

#### CHANGELOG.md
- Version history
- Planned features
- Known limitations
- Compatibility matrix

### Testing Tools

#### `create_test_data.py`
Creates a validation directory with:
- Normal files (no issues)
- Invalid character filenames
- Long filenames (>255 chars)
- Blocked extensions
- Deep folder structures (25 levels)
- Long paths (>400 chars)
- Sample large files

**Usage:**
```powershell
python create_test_data.py
# Creates: C:\Users\<user>\AppData\Local\Temp\SPO_Preflight_Test\
```

## Workflow Diagram

```
┌─────────────────┐
│  User executes  │
│  run_scan.bat   │
│      or         │
│  spo_preflight  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Validate Path  │
│  & Parameters   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Recursive      │
│  Directory      │
│  Scan           │
│  (os.scandir)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  For each item: │
│  - Path length  │
│  - Filename     │
│  - Chars        │
│  - Extension    │
│  - Size         │
│  - Depth        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Issues found?  │
│  Write to CSV   │
│  Log details    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Generate       │
│  - Report.csv   │
│  - Log.txt      │
│  - Exit code    │
└─────────────────┘
```

## Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| Scan Speed | 10k-50k items/min | Network-dependent |
| Memory | <50 MB | Streaming CSV writes |
| Startup Time | <1 second | Pure Python |
| EXE Size | ~8-10 MB | PyInstaller bundle |
| CPU Usage | Low | I/O bound |

## Exit Code Strategy

```python
sys.exit(0)   # No issues - safe to migrate
sys.exit(1)   # Path not found
sys.exit(2)   # Not a directory
sys.exit(3)   # Report write failed
sys.exit(10)  # Issues detected - review report
```

**Automation friendly:**
```powershell
python spo_preflight.py "\\server\share"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Ready for migration"
} elseif ($LASTEXITCODE -eq 10) {
    Write-Host "⚠ Issues require attention"
}
```

## Future Enhancements (Roadmap)

### v1.1 (Planned)
- [ ] HTML report output
- [ ] Tkinter GUI wrapper
- [ ] Auto-remediation mode (safe fixes)

### v1.2 (Planned)
- [ ] Power BI template
- [ ] SharePoint site validation
- [ ] Azure File Share support

### v2.0 (Future)
- [ ] Migration wave planner
- [ ] Parallel scanning
- [ ] Real-time sync monitoring

## Technical Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.10+ |
| Standard Library | os, csv, logging, argparse | Built-in |
| Optional Build | PyInstaller | 5.0+ |
| Target OS | Windows | 10/11, Server 2019/2022 |
| File Systems | NTFS, SMB/CIFS | UNC paths supported |

## Configuration Matrix

All defaults align with Microsoft's documented limits (as of Nov 2025):

| Setting | Default | Microsoft Limit | Configurable |
|---------|---------|-----------------|--------------|
| `--max-path` | 400 | 400 chars | Yes |
| `--max-filename` | 255 | Derived | Yes |
| `--max-file-size-gb` | 250 | 250 GB | Yes |
| `--max-depth` | 20 | Best practice | Yes |
| `--blocked-extensions` | .exe,.dll,.bat,.cmd | Policy-dependent | Yes |

## Support & Maintenance

**Primary Maintainer:** 818Ninja  
**Project Sponsor:** Stanford Health Care IT  
**Support Channel:** IT Service Desk  

**Update Frequency:** As-needed for:
- Microsoft policy changes
- Critical bugs
- Feature requests

---

**Version:** 1.0.0  
**Last Updated:** November 6, 2025  
**Status:** Production Ready ✅
