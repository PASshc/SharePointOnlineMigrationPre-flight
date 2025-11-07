# Launcher Guide

## Available Launchers

This project includes multiple ways to launch the SharePoint Migration Preflight Scanner. Choose the method that works best for you:

---

## 🖱️ GUI Launchers (Graphical Interface)

### 1. `run_gui.bat` (Recommended)
**Double-click this file** to launch the graphical interface.

✅ **Best for:**
- Users who prefer clicking over typing
- Visual form-based configuration
- Real-time validation feedback

✅ **Features:**
- Browse button for folder selection
- Radio buttons for destination type
- Live URL validation (turns green when valid)
- Progress bar during scan
- Auto-open report when issues found
- Scrollable log output

✅ **Requirements:**
- Python 3.10+
- No additional packages needed (uses Tkinter)

---

### 2. `run_gui.ps1` (PowerShell Version)
**Right-click → Run with PowerShell** to launch GUI with better error handling.

✅ **Best for:**
- Users who prefer PowerShell
- Better error messages
- More verbose startup logging

---

### 3. `create_desktop_shortcut.vbs`
**Double-click this file** to create a desktop shortcut named "SPO Scanner".

✅ **What it does:**
- Creates shortcut on your desktop
- Shortcut launches `run_gui.bat`
- Uses Python icon if available

✅ **After running:**
Look for **"SPO Scanner"** icon on your desktop - double-click it anytime to launch the GUI.

---

## 💬 Interactive Wizard (Command Line)

### 4. `run_scan.bat`
**Double-click this file** to launch the interactive command-line wizard.

✅ **Best for:**
- Step-by-step guidance
- Quick scans without opening GUI
- Automated timestamp-based reports

✅ **Features:**
- 4-step wizard asks for configuration
- Validates paths before scanning
- Auto-saves reports to Desktop
- Auto-opens CSV when issues found

---

## ⌨️ Direct Command Line

### 5. Manual Python Command
Open PowerShell or CMD and run:

```cmd
python spo_preflight.py --interactive
```

Or with all parameters:

```cmd
python spo_preflight.py "C:\Data" --spo-url "https://contoso.sharepoint.com/sites/Team" --spo-library "Shared Documents"
```

✅ **Best for:**
- Advanced users
- Automation scripts
- CI/CD pipelines
- Custom parameters

---

## 📊 Quick Comparison

| Launcher | Interface | Ease of Use | Features | Best For |
|----------|-----------|-------------|----------|----------|
| `run_gui.bat` | **Graphical** | ⭐⭐⭐⭐⭐ | Full GUI, validation | Most users |
| `run_scan.bat` | **Text Wizard** | ⭐⭐⭐⭐ | Step-by-step prompts | Quick scans |
| `create_desktop_shortcut.vbs` | **Shortcut Creator** | ⭐⭐⭐⭐⭐ | Desktop icon | One-time setup |
| `python spo_preflight.py` | **Command Line** | ⭐⭐⭐ | Full control | Power users |

---

## 🎯 Recommended Workflow

### First Time Setup:
1. **Double-click** `create_desktop_shortcut.vbs`
2. Look for "SPO Scanner" on your desktop
3. **Done!** Use the desktop icon from now on

### Daily Use:
- **Double-click** the "SPO Scanner" desktop icon
- Fill in the form
- Click "START SCAN"
- Wait for completion
- Review the report

---

## 🔧 Troubleshooting

### "Python is not installed or not in PATH"
- Install Python from https://python.org/downloads/
- **Important:** Check "Add Python to PATH" during installation
- Restart your computer after installing

### GUI doesn't open
- Try `run_gui.ps1` instead for better error messages
- Check that `gui_launcher.py` exists in the same folder
- Run `python --version` in CMD to verify Python is installed

### Shortcut doesn't work
- Re-run `create_desktop_shortcut.vbs`
- Check that `run_gui.bat` exists in the project folder
- Right-click shortcut → Properties → verify "Target" path is correct

### "Permission Denied" error
- Right-click the launcher → Run as Administrator
- Move the project folder out of system directories (e.g., Program Files)

---

## 📁 File Locations

All launchers are in the project root directory:
```
d:\devSHC\_SPOMigrationPre-Flight_v2\
├── run_gui.bat              ← GUI launcher (batch)
├── run_gui.ps1              ← GUI launcher (PowerShell)
├── run_scan.bat             ← Interactive wizard
├── create_desktop_shortcut.vbs  ← Shortcut creator
├── gui_launcher.py          ← GUI script (don't run directly)
└── spo_preflight.py         ← Main scanner script
```

---

## 💡 Tips

- **GUI remembers your settings** - Next time you open it, your last URL and paths are pre-filled
- **Resize the GUI window** - Drag corners or maximize to see all controls
- **Use the Browse button** - Easier than typing long paths
- **Watch for green checkmark** - URL field validates in real-time
- **Check the log output** - See scan progress as it runs

---

## 🆘 Need Help?

- **GUI Guide:** See [INTERACTIVE_MODE.md](INTERACTIVE_MODE.md)
- **Full Documentation:** See [README.md](README.md)
- **Examples:** See [EXAMPLES.md](EXAMPLES.md)
- **Quick Reference:** See [QUICK_START.md](QUICK_START.md)

---

**Version:** 2.1.0  
**Last Updated:** November 7, 2025  
**Author:** 818Ninja Production Tool
