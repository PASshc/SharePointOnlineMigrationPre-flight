# Quick Start Guide

## 🚀 Fastest Way to Run the Scanner

### Option 1: Double-Click `run_scan.bat` (Recommended)

1. **Double-click** `run_scan.bat` in Windows Explorer
2. Follow the 4-step wizard:

```
Step 1: Select destination type
  1 - SharePoint Online Document Library (includes Microsoft Teams)
  2 - OneDrive for Business
  
Step 2: Enter tenant URL
  SharePoint:     https://contoso.sharepoint.com/sites/Team
  Teams (modern): https://contoso.sharepoint.com/sites/MarketingTeam
  Teams (legacy): https://contoso.sharepoint.com/teams/MarketingTeam
  OneDrive:       https://contoso-my.sharepoint.com
  
Step 3: Enter library name
  SharePoint:      "Shared Documents" (most common)
  Teams channels:  "General" (default), "Marketing", "Projects", etc.
  OneDrive:        Auto-set to "Documents"
  
Step 4: Enter path to scan
  Examples: C:\Data, \\server\share\folder
```

3. **Review** configuration summary
4. **Press Y** to start scan
5. Report opens automatically when complete

### Option 2: Command Line

```cmd
python spo_preflight.py --interactive
```

### Option 3: Direct CLI (Skip Wizard)

**For SharePoint:**
```cmd
python spo_preflight.py "C:\Data" ^
  --spo-url "https://contoso.sharepoint.com/sites/Team" ^
  --spo-library "Shared Documents"
```

**For OneDrive:**
```cmd
python spo_preflight.py "C:\Data" ^
  --spo-url "https://contoso-my.sharepoint.com" ^
  --onedrive
```

## 📋 What You Need to Know Before Running

### Information to Gather:

1. **Where is the content going?**
   - [ ] SharePoint Online site
   - [ ] Microsoft Teams (built on SharePoint - use SharePoint option)
   - [ ] OneDrive for Business

2. **What is the SharePoint URL?**
   - SharePoint: Your site URL (e.g., `https://contoso.sharepoint.com/sites/Marketing`)
   - Teams: Your Teams site URL (e.g., `https://contoso.sharepoint.com/sites/MarketingTeam`)
   - OneDrive: Your OneDrive URL (e.g., `https://contoso-my.sharepoint.com`)

3. **What is the target library?**
   - SharePoint: Library name (e.g., "Shared Documents", "ProjectFiles")
   - Teams: Channel name (e.g., "General", "Marketing", "Projects")
   - OneDrive: Always "Documents" (automatic)

4. **Where is the data to scan?**
   - Local drive: `C:\Data\ProjectFiles`
   - Network share: `\\server\share\folder`

### How to Find Your SharePoint/Teams URL:

**For SharePoint Sites:**
1. **Open SharePoint** in your web browser
2. **Copy the URL** from the address bar
3. **Remove everything after** the site name

**For Microsoft Teams:**
1. **Open Teams** and go to the **Files** tab of your channel
2. Click **"Open in SharePoint"** (top right)
3. **Copy the URL** from the address bar
4. **Keep only** up to `/sites/<teamname>` or `/teams/<teamname>`

**Example:**
```
Full SharePoint URL:
https://contoso.sharepoint.com/sites/Team/Shared Documents/Forms/AllItems.aspx

SharePoint URL to use:
https://contoso.sharepoint.com/sites/Team

Library name:
Shared Documents


Full Teams URL (from Files tab → Open in SharePoint):
https://contoso.sharepoint.com/sites/MarketingTeam/Shared Documents/General/project.xlsx

Teams URL to use:
https://contoso.sharepoint.com/sites/MarketingTeam

Channel/Library name:
General
```

## 📊 Understanding the Results

### Report Location

Reports are saved to your **Desktop**:
```
SPOMigrationReport_YYYYMMDD_HHMMSS.csv
SPOMigrationLog_YYYYMMDD_HHMMSS.txt
```

### Key Report Columns

| Column | What It Means |
|--------|---------------|
| `IssueType` | What's wrong (path too long, invalid chars, etc.) |
| `CharacterCountPath` | **SharePoint URL length** (must be ≤400) |
| `SharePointURL` | Exact URL that will be created in SharePoint |
| `LocalPathLength` | Local path length (for reference) |
| `SuggestedFix` | How to fix the issue |

### Exit Codes

- **0**: Success, no issues found
- **10**: Issues found (check report)
- **1**: Error occurred

## ⚠️ Common Issues

### "ERROR: Path does not exist"

✅ **Fix:** Enter the full path including drive letter:
- Good: `C:\Data\Marketing`
- Bad: `\Data\Marketing`

### "Invalid URL format"

✅ **Fix:** Ensure URL starts with `https://` and includes `.sharepoint.com`
- Good: `https://contoso.sharepoint.com/sites/Team`
- Bad: `contoso.sharepoint.com/sites/Team`

### "This is a OneDrive URL. Please select OneDrive destination type instead."

✅ **Fix:** You entered a URL with `-my.sharepoint.com` but selected SharePoint. 
- Re-run and select **Option 2** (OneDrive for Business)

### "OneDrive URL must contain '-my'"

✅ **Fix:** OneDrive URLs must have `-my` before `.sharepoint.com`
- Good: `https://contoso-my.sharepoint.com`
- Bad: `https://contoso.sharepoint.com`

## 🔍 What Gets Checked?

✅ Path length (SharePoint URL ≤400 chars)  
✅ Filename length (≤255 chars)  
✅ Invalid characters (`~ " # % & * : < > ? / \ { | }`)  
✅ Reserved names (CON, PRN, AUX, NUL, COM1-9, LPT1-9)  
✅ Leading/trailing spaces or periods  
✅ Blocked extensions (.exe, .dll, .bat, .cmd)  
✅ File size (≤250 GB)  
✅ Folder depth (>20 levels)  
✅ Case-insensitive duplicates  

## 💡 Pro Tips

1. **Use Interactive Mode**: It's faster and catches configuration errors
2. **Re-scan After Fixes**: Run again after fixing issues to verify
3. **Check SharePointURL Column**: See exactly what URL will be created
4. **Sort by CharacterCountPath**: Find longest paths first
5. **Save Configuration**: Note your tenant URL and library for future scans

## 📚 Need More Help?

- Full documentation: See [README.md](README.md)
- Interactive mode details: See [INTERACTIVE_MODE.md](INTERACTIVE_MODE.md)
- Examples: See [EXAMPLES.md](EXAMPLES.md)
- Changes: See [CHANGELOG.md](CHANGELOG.md)

## 🎯 Quick Decision Tree

```
START
  |
  ├─ I know the SharePoint URL
  |    └─> Use run_scan.bat (interactive wizard)
  |
  ├─ I don't know the SharePoint URL
  |    └─> Ask your SharePoint admin or check your site in browser
  |
  ├─ I just want to scan without SharePoint URL
  |    └─> python spo_preflight.py "C:\Data"
  |        (Uses estimated overhead - less accurate)
  |
  └─ I want to automate this (CI/CD)
       └─> Use CLI mode with all parameters
           python spo_preflight.py "C:\Data" --spo-url "..." --spo-library "..." --fail-on-issues
```

---

**Last Updated:** November 6, 2025  
**Version:** 2.1.0  
**Author:** 818Ninja Production Tool
