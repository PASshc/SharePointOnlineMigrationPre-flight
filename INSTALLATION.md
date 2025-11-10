# Installation Guide

## SharePoint Online Migration Preflight Scanner v2.1.1

This guide provides step-by-step installation instructions for end users.

---

## System Requirements

- **Operating System:** Windows 10 or Windows 11
- **Python:** Version 3.10 or later
- **Disk Space:** ~50 MB for Python dependencies (if needed)
- **Permissions:** User-level access (no admin rights required)

---

## Installation Methods

Choose **one** of the following installation methods:

### ✅ **Method 1: Portable USB Version (No Python Required)**

**Best for:** Users without Python installed or IT-restricted environments

1. **Download the portable package** from your IT department or project repository
2. **Copy** the `SPO_Preflight_Portable` folder to your USB drive or local computer
3. **Run** `Launch_GUI.bat` inside the folder
4. **Done!** No installation needed - runs immediately

**Advantages:**
- ✅ No Python installation required
- ✅ Runs on any Windows PC
- ✅ Portable - carry on USB drive
- ✅ No admin rights needed

**Note:** To create the portable package yourself, see "Building Portable Version" below.

---

### ✅ **Method 2: Python Installation (Recommended for Developers)**

**Best for:** Power users, developers, or those who already have Python

#### Step 1: Install Python

1. **Download Python 3.10+** from [python.org/downloads](https://www.python.org/downloads/)
2. **Run the installer**
3. **✅ IMPORTANT:** Check "Add Python to PATH" during installation
4. Click "Install Now"
5. Wait for installation to complete

**Verify installation:**
```cmd
python --version
```
You should see: `Python 3.12.x` (or similar)

#### Step 2: Download the Scanner

**Option A: Git Clone (if you have Git)**
```cmd
git clone https://github.com/PASshc/SharePointOnlineMigrationPre-flight.git
cd SharePointOnlineMigrationPre-flight
```

**Option B: Direct Download**
1. Go to [GitHub Repository](https://github.com/PASshc/SharePointOnlineMigrationPre-flight)
2. Click "Code" → "Download ZIP"
3. Extract the ZIP file to your desired location (e.g., `C:\Tools\SPO_Scanner`)

#### Step 3: Install Optional Dependencies (Recommended)

```cmd
pip install Pillow
```

**What this does:** Enables the logo in the GUI. The tool works without it, but the GUI looks nicer with Pillow installed.

#### Step 4: Verify Installation

```cmd
python spo_preflight.py --version
```

You should see: `SharePoint Online Migration Preflight Scanner v2.1.1`

#### Step 5: Create Desktop Shortcut (Optional)

**Double-click** `create_desktop_shortcut.vbs` to add a "SPO Scanner" icon to your desktop.

---

## First Run

### GUI Mode (Easiest)

1. **Double-click** `run_gui.bat`
2. The graphical interface will open
3. Choose your scan mode:
   - **Pre-Flight Check:** Scan for SharePoint migration issues
   - **Inventory Only:** Create file/folder inventory for comparison
4. Fill in the required fields
5. Click "Start Scan"

### Command-Line Wizard

1. **Double-click** `run_scan.bat`
2. Follow the interactive prompts
3. Choose scan mode and enter required information

### Command-Line Direct

```cmd
python spo_preflight.py --interactive
```

Or for advanced users:
```cmd
python spo_preflight.py "C:\Data" --spo-url "https://contoso.sharepoint.com/sites/Team" --spo-library "Shared Documents"
```

---

## Building Portable Version (Advanced)

If you want to create the portable EXE package yourself:

### Prerequisites
```cmd
pip install pyinstaller
```

### Build Process

1. **Run the build script:**
   ```cmd
   build_portable_exe.bat
   ```

2. **Wait for build to complete** (~2-3 minutes)

3. **Find your portable package:**
   - Location: `SPO_Preflight_Portable` folder
   - Contains: `SPOMigrationPreflight_GUI.exe`, `SPOMigrationPreflight_CLI.exe`, and documentation

4. **Copy to USB or distribute** the entire `SPO_Preflight_Portable` folder

**What gets built:**
- `SPOMigrationPreflight_GUI.exe` - Graphical interface (no console window)
- `SPOMigrationPreflight_CLI.exe` - Command-line version
- `Launch_GUI.bat` - Easy launcher for the GUI
- All documentation and images

---

## Troubleshooting

### "Python is not recognized"

**Problem:** Python not in PATH

**Solution:**
1. Reinstall Python
2. ✅ Check "Add Python to PATH" during installation
3. Or manually add Python to PATH:
   - Right-click "This PC" → Properties → Advanced system settings
   - Environment Variables → System variables → Path
   - Add: `C:\Python312` and `C:\Python312\Scripts`

### "ModuleNotFoundError: No module named 'tkinter'"

**Problem:** Tkinter not installed (rare on Windows)

**Solution:**
```cmd
pip install tk
```

Or reinstall Python ensuring "tcl/tk and IDLE" is selected.

### "Pillow not installed" warning

**Problem:** Optional Pillow library not installed

**Solution:**
```cmd
pip install Pillow
```

**Note:** The tool works fine without Pillow - you just won't see the logo in the GUI.

### GUI doesn't open

**Problem:** Multiple possible causes

**Solutions:**
1. Check Python version: `python --version` (must be 3.10+)
2. Run from command line to see errors: `python gui_launcher.py`
3. Try portable EXE version instead

### "Access Denied" errors during scan

**Problem:** Insufficient permissions to scan folder

**Solutions:**
- Run as administrator (right-click `run_gui.bat` → Run as administrator)
- Use an account with appropriate permissions
- The scanner will log permission errors and continue scanning accessible folders

---

## Configuration File

The GUI automatically saves your settings in `scanner_config.json`:

```json
{
  "dest_type": "sharepoint",
  "spo_url": "https://contoso.sharepoint.com/sites/Team",
  "library_name": "Shared Documents",
  "scan_path": "C:/Data",
  "last_updated": "2025-11-10T10:30:00"
}
```

**Purpose:** Remembers your last-used settings for convenience

**Location:** Same folder as the scanner

**Note:** This file is excluded from Git (.gitignore) as it contains local paths

**To reset:** Simply delete `scanner_config.json` and start fresh

---

## Getting Help

### Check Version
```cmd
python spo_preflight.py --version
```

### Command-Line Help
```cmd
python spo_preflight.py --help
```

### Documentation
- **README.md** - Full feature documentation
- **INVENTORY_MODE.md** - Inventory feature guide
- **USB_DEPLOYMENT_GUIDE.md** - Portable deployment guide
- **QUICK_REFERENCE.txt** - Quick command reference

### Support
Contact your IT department or the tool maintainer for assistance.

---

## Uninstallation

### Python Version
Simply delete the folder containing the scanner files.

Python installation is separate - uninstall via Windows Settings if desired.

### Portable Version
Delete the `SPO_Preflight_Portable` folder. No traces left on system.

---

## Next Steps

1. ✅ **Test with a small folder** first to understand the output
2. 📖 **Read** [QUICK_REFERENCE.txt](QUICK_REFERENCE.txt) for common commands
3. 🔍 **Run Pre-Flight scan** on your migration source
4. 📊 **Review CSV report** in Excel
5. 🛠️ **Fix identified issues** before migration
6. ✅ **Create inventory** for pre/post comparison

---

**Built by 818Ninja** | v2.1.1 | MIT License
