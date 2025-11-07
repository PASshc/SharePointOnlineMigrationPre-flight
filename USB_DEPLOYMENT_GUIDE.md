# USB Portable Deployment Guide

## Overview

This guide covers TWO ways to run the SharePoint Migration Preflight Scanner from a USB drive:

1. **🏆 BEST OPTION: Portable EXE** - No prerequisites needed, works on any Windows PC
2. **Alternative: Python Scripts** - Requires Python on the target machine

---

## 🏆 Option 1: Portable EXE (RECOMMENDED)

### Advantages
✅ **NO prerequisites** - Works on any Windows 10/11 PC  
✅ **NO Python needed** - Standalone executables  
✅ **NO installation** - Just copy and run  
✅ **USB ready** - Plug and play  
✅ **Professional** - Single-click launch  

### How to Build the Portable Package

**On your development machine (one-time setup):**

1. **Double-click:** `build_portable_exe.bat`

2. **Wait for build** (2-3 minutes)
   - Builds CLI executable
   - Builds GUI executable  
   - Creates portable package folder
   - Adds launcher batch files
   - Includes all documentation

3. **Result:** A new folder called `SPO_Preflight_Portable`

### Package Contents

```
SPO_Preflight_Portable/
│
├── SPOMigrationPreflight_GUI.exe      ← Main GUI (double-click this!)
├── SPOMigrationPreflight_CLI.exe      ← Command-line version
│
├── Launch_GUI.bat                     ← Easy launcher for GUI
├── Show_CLI_Help.bat                  ← Show command options
├── Example_Inventory_Scan.bat         ← Interactive inventory demo
│
├── images/                            ← Application logo
│   └── Designer.png
│
├── PORTABLE_README.txt                ← Quick start guide
├── README.md                          ← Full documentation
├── INVENTORY_MODE.md                  ← Inventory feature guide
├── GUI_SCAN_MODE_UPDATE.md            ← GUI usage guide
└── EXAMPLES.md                        ← Usage examples
```

### Deploy to USB

1. **Copy the entire `SPO_Preflight_Portable` folder to USB drive**
   ```
   Copy: D:\devSHC\_SPOMigrationPre-Flight_v2\SPO_Preflight_Portable
   To:   E:\SPO_Preflight_Portable (your USB drive)
   ```

2. **That's it!** The package is ready to use.

### Use on Any Windows PC

**On the target PC (no Python needed):**

1. **Plug in USB drive**

2. **Browse to:** `E:\SPO_Preflight_Portable`

3. **Double-click:** `Launch_GUI.bat`
   - OR directly: `SPOMigrationPreflight_GUI.exe`

4. **Use the GUI:**
   - Select scan mode (Pre-Flight Check or Inventory)
   - Browse for folder to scan
   - Configure options
   - Click "Start Scan"
   - Reports saved automatically

### Command-Line Usage (USB)

From the USB folder, you can also run:

**Pre-Flight Check:**
```cmd
SPOMigrationPreflight_CLI.exe --scan-path "C:\Data" --spo-url "contoso.sharepoint.com"
```

**Inventory Only:**
```cmd
SPOMigrationPreflight_CLI.exe --scan-path "C:\Data" --inventory-only
```

**Show Help:**
```cmd
SPOMigrationPreflight_CLI.exe --help
```

---

## Option 2: Python Scripts (Requires Python)

### Prerequisites on Target PC

The target PC **must have**:
- Python 3.10 or later
- Python added to PATH

**Optional but recommended:**
- Pillow library (for logo in GUI)
  ```cmd
  pip install Pillow
  ```

### Deploy to USB

1. **Copy the entire source folder to USB:**
   ```
   Copy: D:\devSHC\_SPOMigrationPre-Flight_v2\
   To:   E:\SPOMigrationPreflight\
   ```

2. **Include these files:**
   - `gui_launcher.py`
   - `spo_preflight.py`
   - `run_gui.bat`
   - `run_scan.bat`
   - `images/` folder (for logo)
   - All `.md` documentation files

### Use on Target PC (Python Required)

**On the target PC:**

1. **Verify Python is installed:**
   ```cmd
   python --version
   ```
   Should show Python 3.10 or higher

2. **Browse to USB folder**

3. **Run GUI:**
   - Double-click `run_gui.bat`
   - Or: `python gui_launcher.py`

4. **Run CLI:**
   - Double-click `run_scan.bat` (interactive)
   - Or: `python spo_preflight.py --help`

### Install Optional Dependencies (Target PC)

**For logo support in GUI:**
```cmd
pip install Pillow
```

**Note:** The tool works without Pillow, just won't show the logo.

---

## Comparison

| Feature | Portable EXE | Python Scripts |
|---------|--------------|----------------|
| **Prerequisites on target PC** | None! | Python 3.10+ |
| **Installation needed** | No | No (if Python already installed) |
| **Pillow needed for logo** | No (included) | Optional |
| **File size** | ~15-20 MB | ~1-2 MB |
| **Startup speed** | Fast | Very fast |
| **Ease of use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Best for** | Any PC, USB deployment | Developer machines |

---

## Features Available (Both Options)

### Pre-Flight Check Mode
✅ Path length validation (≤400 chars)  
✅ Filename length validation (≤255 chars)  
✅ Invalid character detection  
✅ Blocked file extensions  
✅ File size limits (≤250 GB)  
✅ Leading/trailing spaces/periods  
✅ Folder depth analysis  

### Inventory Mode
✅ Complete file/folder listing  
✅ File counts and sizes  
✅ Modified dates  
✅ Extensions  
✅ Folder depths  
✅ CSV export for comparison  

### GUI Features
✅ Scan mode selection (first option shown)  
✅ Dynamic fields (only show what's needed)  
✅ Progress tracking  
✅ Browse for folders  
✅ Save reports anywhere  
✅ Professional logo (if Pillow available)  

---

## Recommended Workflow

### For Most Users (Non-Technical)
1. Build portable EXE package (one time)
2. Copy to USB drive
3. Share USB with users
4. Users just double-click `Launch_GUI.bat`
5. No training needed!

### For IT/Power Users
1. Use Python scripts for flexibility
2. Install Python on workstations
3. Copy scripts to USB or network share
4. Run via batch files or command line
5. Customize parameters as needed

### For Distribution to Multiple Sites
1. Build portable EXE package
2. ZIP the package folder
3. Email or upload to SharePoint
4. Users extract and run
5. No installation or prerequisites!

---

## Troubleshooting

### Portable EXE Issues

**"Windows protected your PC" SmartScreen warning:**
- Click "More info"
- Click "Run anyway"
- This is normal for unsigned executables

**EXE won't run:**
- Check if antivirus is blocking it
- Try running as Administrator (right-click → Run as administrator)
- Check Windows Defender exclusions

### Python Script Issues

**"Python is not recognized":**
- Python not installed or not in PATH
- Install Python and check "Add to PATH"
- Use portable EXE instead

**"No module named 'PIL'" but GUI still works:**
- This is expected! Logo won't show but GUI works
- Optional: Install Pillow with `pip install Pillow`

**GUI won't launch:**
- Check Python version (must be 3.10+)
- Try: `python gui_launcher.py` to see errors
- Verify tkinter is available (comes with Python)

---

## File Size Estimates

### Portable EXE Package
- GUI EXE: ~12-15 MB
- CLI EXE: ~10-12 MB
- Images: ~1.2 MB
- Documentation: ~1 MB
- **Total:** ~25-30 MB

### Python Scripts
- Python files: ~200 KB
- Images: ~1.2 MB
- Documentation: ~1 MB
- **Total:** ~2-3 MB

**Both easily fit on any USB drive!**

---

## Security Considerations

### Portable EXE
- Built with PyInstaller (open source)
- No network access required
- All scanning is local
- No data sent anywhere
- Can be scanned with antivirus

### Python Scripts
- Source code visible
- Can be audited
- No obfuscation
- Standard Python libraries only

---

## Updates and Maintenance

### To Update Portable EXE
1. Make code changes
2. Re-run `build_portable_exe.bat`
3. Copy new package to USB
4. Distribute updated version

### To Update Python Scripts
1. Make code changes
2. Copy updated `.py` files to USB
3. Distribute
4. No rebuild needed

---

## Best Practices

### For USB Distribution
✅ Use a high-quality USB drive (USB 3.0+)  
✅ Label the USB clearly ("SPO Preflight Scanner")  
✅ Include PORTABLE_README.txt in root  
✅ Test on a clean PC before distributing  
✅ Keep a backup copy on network share  

### For Network Distribution
✅ ZIP the portable package  
✅ Upload to SharePoint or network share  
✅ Include extraction instructions  
✅ Provide direct link to package  
✅ Version the ZIP file (e.g., `SPO_Preflight_v2.1.1.zip`)  

---

## Quick Reference

### Build Portable Package
```cmd
build_portable_exe.bat
```

### Launch GUI (USB/Portable)
```cmd
Launch_GUI.bat
```

### Launch GUI (Python)
```cmd
run_gui.bat
or
python gui_launcher.py
```

### Run Inventory (USB/Portable)
```cmd
SPOMigrationPreflight_CLI.exe --scan-path "C:\Data" --inventory-only
```

### Run Inventory (Python)
```cmd
python spo_preflight.py --scan-path "C:\Data" --inventory-only
```

---

## Support Resources

- **Full Documentation:** README.md
- **Inventory Guide:** INVENTORY_MODE.md
- **GUI Guide:** GUI_SCAN_MODE_UPDATE.md
- **Examples:** EXAMPLES.md
- **CLI Help:** `SPOMigrationPreflight_CLI.exe --help`

---

**Last Updated:** November 7, 2025  
**Version:** 2.1.1+  
**Portable Ready:** ✅ Yes!
