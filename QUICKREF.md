# Quick Reference Guide

## One-Minute Start

```powershell
# Double-click: run_scan.bat
# or
python spo_preflight.py "\\server\share\path"
```

## Common Commands

### Basic Scan
```powershell
python spo_preflight.py "C:\Data"
```

### Custom Output Location
```powershell
python spo_preflight.py "C:\Data" --report "D:\Reports\output.csv"
```

### Stanford Health Care DSS Share
```powershell
python spo_preflight.py "\\enterprise.stanfordmed.org\depts\DSS\_4fpa" `
  --report "$env:USERPROFILE\Desktop\DSS_Report.csv"
```

### Stricter Limits
```powershell
python spo_preflight.py "C:\Data" --max-path 350 --max-filename 200
```

## What Gets Checked

| Check | Default Limit | Configurable |
|-------|--------------|--------------|
| Path length | 400 chars | `--max-path` |
| Filename length | 255 chars | `--max-filename` |
| File size | 250 GB | `--max-file-size-gb` |
| Folder depth | 20 levels | `--max-depth` |
| Invalid chars | `~ " # % & * : < > ? / \ { | }` | No |
| Blocked extensions | `.exe .dll .bat .cmd` | `--blocked-extensions` |
| Leading/trailing space/period | Any | No |

## Output Columns

1. **ItemType** - File or Folder
2. **FullPath** - Complete path to item
3. **IssueType** - What's wrong
4. **CurrentValue** - Current problematic value
5. **SuggestedFix** - How to fix it
6. **CharacterCount** - Length of name/path
7. **FileSizeMB** - File size (files only)
8. **FolderDepth** - Depth from scan root

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | ✓ No issues |
| 1 | ✗ Path not found |
| 2 | ✗ Not a directory |
| 3 | ✗ Can't write report |
| 10 | ⚠ Issues found (check report) |

## Quick Filters in Excel

After opening the CSV in Excel:

1. **Filter by Issue Type:**
   - Click header row → Filter
   - Click "IssueType" dropdown
   - Select specific issues

2. **Sort by Folder Depth:**
   - Click "FolderDepth" header
   - Sort Descending

3. **Find Large Files:**
   - Click "FileSizeMB" header
   - Sort Descending

4. **Show Only Files or Folders:**
   - Filter "ItemType" column

## Troubleshooting

### "Python is not recognized"
→ Install Python from python.org (check "Add to PATH")

### "Permission denied"
→ Run as admin or use account with share access

### "Path too long" errors
→ Run from a shorter base path (e.g., `C:\Scan\`)

### Report opens with garbled characters
→ Use Excel's "Get Data" → "From Text/CSV" → UTF-8

### Scan is slow
→ Normal for network shares; ~10k-50k items/min typical

## Power User Tips

### Scan Multiple Shares
```powershell
# Create scan_all.ps1:
$shares = "\\srv\share1", "\\srv\share2", "\\srv\share3"
foreach ($s in $shares) {
    python spo_preflight.py $s --report "${s}_report.csv"
}
```

### Schedule Daily Scans
```cmd
schtasks /create /tn "SPO Scan" /tr "python C:\Scripts\spo_preflight.py \\server\share" /sc daily /st 02:00
```

### Build EXE
```powershell
pip install pyinstaller
pyinstaller --onefile --name SPOPreflight spo_preflight.py
# EXE in: dist\SPOPreflight.exe
```

### Export to SharePoint List
1. Save CSV
2. Open SharePoint site
3. New → List → From CSV
4. Upload report

## Get Help

```powershell
python spo_preflight.py --help
```

## Microsoft References

- [SPO Limits](https://learn.microsoft.com/en-us/office365/servicedescriptions/sharepoint-online-service-description/sharepoint-online-limits)
- [Restrictions](https://support.microsoft.com/en-us/office/restrictions-and-limitations-in-onedrive-and-sharepoint-64883a5d-228e-48f5-b3d2-eb39e07630fa)
- [File Upload](https://support.microsoft.com/en-us/office/upload-photos-and-files-to-onedrive-b00ad3fe-6643-4b16-9212-de00ef02b586)

---

**Need more?** See README.md for full documentation.
