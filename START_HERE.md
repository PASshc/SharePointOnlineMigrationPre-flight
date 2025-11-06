# 🎯 GET STARTED - Read This First!

Welcome to the **SharePoint Online Migration Preflight Scanner**!

This tool was built specifically for the Stanford Health Care DSS migration project, but works for any SharePoint Online migration.

---

## ⚡ Quick Start (30 Seconds)

### Option 1: Double-Click Method (Easiest)
1. **Double-click:** `run_scan.bat`
2. **Paste your path** when prompted (or drag folder into window)
3. **Press Enter** and wait for scan to complete
4. **Excel opens automatically** with your report

### Option 2: PowerShell (Recommended)
```powershell
cd d:\devSHC\_SPOMigrationPre-Flight_v2
.\run_scan.ps1
```
Follow the interactive prompts!

### Option 3: Command Line (For Power Users)
```powershell
python .\spo_preflight.py "\\enterprise.stanfordmed.org\depts\DSS\_4fpa"
```

---

## 📋 What You Need

✅ **Windows 10/11** (or Server 2019/2022)  
✅ **Python 3.10+** ([Download here](https://www.python.org/downloads/))  
✅ **5 minutes** of your time  

**That's it!** No pip installs, no dependencies, no complicated setup.

---

## 📂 What You Get

After running the scan, you'll have two files on your Desktop:

### 1. `SPOMigrationReport.csv` 📊
Excel-ready report with all detected issues:
- Full paths to problematic files/folders
- Specific issues (long names, invalid characters, etc.)
- Suggested fixes
- File sizes and folder depths

### 2. `SPOMigrationLog.txt` 📝
Detailed scan log:
- Number of items scanned
- Number of issues found
- Scan duration
- Any permission errors encountered

---

## 🎓 What This Tool Checks

| ✅ Check | Why It Matters |
|---------|---------------|
| **Path too long** (>400 chars) | SharePoint won't sync these files |
| **Filename too long** (>255 chars) | Migration will fail |
| **Invalid characters** (`~ " # % & * : < > ? / \ { | }`) | SharePoint blocks these |
| **Blocked extensions** (`.exe`, `.dll`, `.bat`) | Security policy violations |
| **Files too large** (>250 GB) | Upload limit exceeded |
| **Leading/trailing spaces** | Sync errors guaranteed |
| **Deep folders** (>20 levels) | Path length problems ahead |

---

## 🚀 Next Steps

### 1. Run Your First Scan
```powershell
# Example for Stanford Health Care DSS share:
python .\spo_preflight.py "\\enterprise.stanfordmed.org\depts\DSS\_4fpa" `
  --report "$env:USERPROFILE\Desktop\DSS_PreflightReport.csv"
```

### 2. Open the Report in Excel
- Sort by `IssueType` to group similar problems
- Filter by `FolderDepth` to find deep structures
- Review `SuggestedFix` column for remediation ideas

### 3. Plan Your Remediation
Use the report to:
- Identify files that need renaming
- Find folders that need flattening
- Locate blocked file types
- Calculate remediation effort

### 4. Create a Standalone EXE (Optional)
If you want to share this tool with colleagues who don't have Python:

```powershell
.\build_exe.bat
```

The EXE will be in `dist\SPOMigrationPreflight.exe` - copy it anywhere!

---

## 📚 Documentation Quick Links

| Document | What's Inside | When to Read |
|----------|--------------|--------------|
| **[README.md](README.md)** | Complete user guide | For detailed instructions |
| **[QUICKREF.md](QUICKREF.md)** | One-page cheat sheet | Keep this open while working |
| **[EXAMPLES.md](EXAMPLES.md)** | 5 ready-to-use scenarios | For custom configurations |
| **[STRUCTURE.md](STRUCTURE.md)** | Technical architecture | For developers/customization |
| **[CHANGELOG.md](CHANGELOG.md)** | Version history & roadmap | For updates & future features |

---

## ❓ Common Questions

### "I don't have Python installed. What do I do?"
→ [Download Python](https://www.python.org/downloads/) (choose 3.11 or newer)  
→ **Important:** Check "Add Python to PATH" during installation!

### "The scan found thousands of issues. Now what?"
→ Start with the most critical issues first:
1. Blocked extensions (security risk)
2. Path/filename too long (migration blockers)
3. Invalid characters (sync failures)
4. Everything else can be evaluated by severity

### "Can I scan multiple shares at once?"
→ Yes! See [EXAMPLES.md](EXAMPLES.md) for batch scanning scripts.

### "How long does a scan take?"
→ Typical speeds: 10,000-50,000 items per minute  
→ A 100,000-item share takes 2-10 minutes

### "Will this modify my files?"
→ **NO!** This tool is read-only. It only generates reports.

### "I get 'Permission Denied' errors"
→ Normal! The tool logs these and continues. Run with an account that has read access to the entire share for complete results.

---

## 🆘 Need Help?

1. **Check the logs:** `SPOMigrationLog.txt` has details
2. **Review troubleshooting:** See README.md § Troubleshooting
3. **Test with sample data:** Run `python create_test_data.py` to create test files
4. **Contact support:** Your IT department or project team

---

## 🏆 Pro Tips

### Tip #1: Run Test Scans First
```powershell
# Create test data to verify tool works:
python .\create_test_data.py

# Then scan it:
python .\spo_preflight.py "C:\Users\<you>\AppData\Local\Temp\SPO_Preflight_Test"
```

### Tip #2: Use Timestamps for Reports
```powershell
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
python .\spo_preflight.py "\\server\share" --report "Report_$timestamp.csv"
```

### Tip #3: Filter Issues in Excel
After opening the CSV:
1. Click any header → **Data** tab → **Filter**
2. Use dropdowns to focus on specific issue types
3. Sort by `FolderDepth` descending to find deepest paths

### Tip #4: Schedule Regular Scans
```powershell
# Windows Task Scheduler - daily scan at 2 AM:
schtasks /create /tn "SPO Daily Scan" `
  /tr "python d:\devSHC\_SPOMigrationPre-Flight_v2\spo_preflight.py \\server\share" `
  /sc daily /st 02:00
```

---

## 🎉 You're Ready!

**Three ways to start right now:**

```powershell
# 1. Interactive (easiest):
.\run_scan.ps1

# 2. Quick batch (double-click):
run_scan.bat

# 3. Direct command (fastest):
python .\spo_preflight.py "YOUR_PATH_HERE"
```

---

## ✅ Validation Checklist

Before your first scan, verify:

- [ ] Python 3.10+ installed (`python --version`)
- [ ] You have read access to the target share
- [ ] You have write access to the output location (Desktop)
- [ ] Your antivirus allows Python scripts (if applicable)
- [ ] You have ~100MB free disk space (for large reports)

---

## 📞 Support Information

**Project:** Stanford Health Care SharePoint Migration  
**Tool Version:** 1.0.0  
**Built by:** 818Ninja  
**Last Updated:** November 6, 2025  

**For Issues:**
- Review documentation first
- Check QUICKREF.md for common solutions
- Contact your IT migration team

---

## 🚦 Status Indicators

When the scan completes, you'll see one of these:

| Exit Code | Status | What It Means |
|-----------|--------|---------------|
| **0** | ✅ SUCCESS | No issues - ready to migrate! |
| **10** | ⚠️ ISSUES FOUND | Check report for details |
| **1, 2, 3** | ❌ ERROR | Check path/permissions |

---

**Ready to scan? Pick a method above and go! 🚀**

*Questions? Start with [README.md](README.md) for the complete guide.*
