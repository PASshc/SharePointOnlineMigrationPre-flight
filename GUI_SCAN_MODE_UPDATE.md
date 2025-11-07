# GUI Scan Mode Selection - User Guide

## Overview

The SharePoint Migration Preflight Scanner GUI now features **Scan Mode Selection** as the **first step** in the workflow. This streamlines the user experience by showing only the relevant fields based on your chosen mode.

## What Changed?

### Before (v2.1.0)
- Users had to fill out SharePoint URL fields regardless of scan type
- Inventory mode was a checkbox at the bottom (Section 5)
- All fields were always visible

### After (v2.1.1+)
- **Section 1: Select Scan Mode** - Choose your mode FIRST
- Fields dynamically show/hide based on mode
- Inventory mode users skip unnecessary SharePoint URL configuration

## Two Scan Modes

### 📋 **Inventory Only Mode**

**Purpose:** Create a complete file/folder list for pre/post migration verification

**When to use:**
- Before migration: Create baseline inventory
- After migration: Verify all files transferred
- Change tracking: Compare inventories over time
- Migration planning: Get accurate counts and sizes

**Required Fields:**
1. ✅ **Scan Mode**: Select "Inventory Only"
2. ✅ **Folder to Scan**: Select the folder path

**Hidden Fields:**
- ❌ Destination Type (not needed)
- ❌ SharePoint Site URL (not needed)
- ❌ Document Library / Channel Name (not needed)

**Output:**
- CSV file with complete file/folder listing
- Summary statistics (file count, folder count, total size)
- Saved as: `SPOMigrationInventory_YYYYMMDD_HHMMSS.csv`

---

### 🔍 **Pre-Flight Check Mode**

**Purpose:** Scan for SharePoint migration issues and compatibility problems

**When to use:**
- Before migration: Identify blocking issues
- Planning phase: Understand what needs fixing
- Compliance check: Ensure files meet SharePoint limits

**Required Fields:**
1. ✅ **Scan Mode**: Select "Pre-Flight Check"
2. ✅ **Destination Type**: SharePoint/Teams/OneDrive
3. ✅ **SharePoint Site URL**: Full URL to your site
4. ✅ **Document Library**: Library/channel name
5. ✅ **Folder to Scan**: Select the folder path

**Output:**
- CSV file with identified issues
- Issue categories (blocked characters, file size, path length, etc.)
- Recommended fixes
- Saved as: `SPOMigrationReport_YYYYMMDD_HHMMSS.csv`

---

## Step-by-Step Usage

### Option 1: Inventory Mode (Simple & Fast)

```
STEP 1: Launch GUI
├─ Run: run_gui.bat (or python gui_launcher.py)

STEP 2: Select Scan Mode
├─ Choose: ● Inventory Only (Create complete file/folder list with counts)
├─ Notice: SharePoint URL fields are hidden (not needed!)

STEP 3: Choose Folder
├─ Click "Browse..." button
└─ Select folder: C:\Data\HR_Files

STEP 4: Start Scan
├─ Click "START SCAN"
├─ Watch progress
└─ Report saved to Desktop: SPOMigrationInventory_20251107_143022.csv

STEP 5: Review Results
├─ Click "Open Report"
├─ See: 12,456 files, 345 folders, 45.67 GB
└─ Use for: Pre/post migration comparison
```

### Option 2: Pre-Flight Check Mode (Full Validation)

```
STEP 1: Launch GUI
├─ Run: run_gui.bat (or python gui_launcher.py)

STEP 2: Select Scan Mode
├─ Choose: ○ Pre-Flight Check (Scan for SharePoint migration issues)
├─ Notice: SharePoint URL fields are visible

STEP 3: Select Destination Type
├─ Choose: ○ SharePoint Online Document Library
└─ (or Teams, OneDrive)

STEP 4: Enter SharePoint Site URL
├─ Type: https://contoso.sharepoint.com/sites/HR
└─ Validation: URL format checked in real-time

STEP 5: Enter Document Library
├─ Type: Shared Documents
└─ Example: "Shared Documents" or "General" (for Teams)

STEP 6: Choose Folder
├─ Click "Browse..." button
└─ Select folder: C:\Data\HR_Files

STEP 7: Start Scan
├─ Click "START SCAN"
├─ Watch progress
└─ Report saved to Desktop: SPOMigrationReport_20251107_143022.csv

STEP 8: Review Issues
├─ Click "Open Report"
├─ See: 23 issues found
└─ Fix: Rename files, reduce sizes, etc.
```

---

## UI Behavior

### Inventory Mode Selected
- **Section 1**: Scan Mode (VISIBLE - showing Inventory selected)
- **Section 2**: Destination Type (HIDDEN)
- **Section 3**: SharePoint Site URL (HIDDEN)
- **Section 4**: Document Library (HIDDEN)
- **Section 5**: Folder to Scan (VISIBLE)
- **Section 6**: Scan Button (VISIBLE)

**Help Text:** 
> 📋 Inventory mode: Creates complete list of all files/folders with counts (no issue checking). SharePoint URL not required.

### Pre-Flight Mode Selected
- **Section 1**: Scan Mode (VISIBLE - showing Pre-Flight selected)
- **Section 2**: Destination Type (VISIBLE)
- **Section 3**: SharePoint Site URL (VISIBLE)
- **Section 4**: Document Library (VISIBLE)
- **Section 5**: Folder to Scan (VISIBLE)
- **Section 6**: Scan Button (VISIBLE)

**Help Text:** 
> Pre-Flight: Validates files against SharePoint limits and naming rules • Inventory: Lists all files/folders for pre/post migration comparison

---

## Benefits

### For Users
✅ **Simplified workflow**: Only see fields you need  
✅ **Faster inventory scans**: Skip SharePoint URL entry  
✅ **Clear mode distinction**: Know exactly what the scan will do  
✅ **Reduced errors**: Can't submit without required fields  

### For Administrators
✅ **Less training needed**: Intuitive interface  
✅ **Fewer support tickets**: Clear validation messages  
✅ **Consistent results**: Mode selection prevents user confusion  

---

## Validation Rules

### Inventory Mode
- ✅ **Required**: Folder path only
- ❌ **Not Required**: SharePoint URL, Library name
- ⚡ **Validation**: Path must exist and be a directory

### Pre-Flight Mode
- ✅ **Required**: All fields (URL, Library, Folder)
- ⚡ **Validation**: 
  - URL format must match SharePoint/Teams/OneDrive pattern
  - Library name required (except OneDrive)
  - Path must exist and be a directory

---

## Troubleshooting

### Issue: Can't see SharePoint URL fields
**Solution:** Select "Pre-Flight Check" mode in Section 1

### Issue: Validation error about SharePoint URL
**Solution:** Check that you selected Pre-Flight mode (not Inventory)

### Issue: Want to scan without SharePoint URL
**Solution:** Use Inventory mode - it doesn't require SharePoint configuration

### Issue: Fields disappeared after clicking mode
**Solution:** This is expected behavior - fields show/hide based on mode

---

## Comparison: Before vs After

| Feature | Old (v2.1.0) | New (v2.1.1+) |
|---------|-------------|---------------|
| **Mode Selection** | Checkbox at bottom | Radio buttons at top |
| **Field Visibility** | Always visible | Dynamic (show/hide) |
| **User Flow** | Fill everything first | Choose mode first |
| **Inventory Simplicity** | Required URL entry | Only folder required |
| **Error Prevention** | Could submit without mode | Mode required first |
| **UI Clarity** | All modes mixed | Clear separation |

---

## Examples

### Example 1: Quick Inventory for 50GB Data

```
User: "I just need to count files before migration"

Solution:
1. Select: ● Inventory Only
2. Browse: \\server\share\Finance
3. Click: START SCAN
4. Wait: ~2 minutes (for 50,000 files)
5. Result: 48,234 files, 1,567 folders, 49.87 GB

No SharePoint URL needed! ✅
```

### Example 2: Pre-Migration Issue Check

```
User: "Need to find blocking issues before migrating to Teams"

Solution:
1. Select: ○ Pre-Flight Check
2. Choose: Microsoft Teams Channel
3. Enter URL: https://contoso.sharepoint.com/teams/Finance
4. Enter Library: General
5. Browse: \\server\share\Finance
6. Click: START SCAN
7. Result: 23 issues found (invalid characters, long paths)

Fix issues, then re-scan! ✅
```

### Example 3: Post-Migration Verification

```
User: "Migrated files - need to verify counts match"

Workflow:
PRE-MIGRATION:
├─ Mode: Inventory Only
├─ Scan: \\server\share\Finance
└─ Result: 48,234 files, 49.87 GB

MIGRATION:
├─ Use SharePoint Migration Tool
└─ Migrate to SharePoint Online

POST-MIGRATION:
├─ Mode: Inventory Only
├─ Scan: C:\MigratedData\Finance (synced via OneDrive)
├─ Result: 48,234 files, 49.87 GB
└─ Compare: MATCH! ✅

100% verification without SharePoint URL! ✅
```

---

## Keyboard Shortcuts

- **Tab**: Navigate between fields
- **Space**: Toggle radio button
- **Enter**: Submit (when on scan button)
- **Alt+B**: Browse for folder (if button has focus)

---

## Technical Details

### Code Changes (v2.1.1)

**File Modified:** `gui_launcher.py`

**Changes:**
1. Moved scan mode to Section 1 (first in form)
2. Changed from checkbox to radio buttons
3. Added `on_scan_mode_change()` handler
4. Implemented dynamic field visibility (grid/grid_remove)
5. Updated validation to skip SharePoint URL in inventory mode
6. Modified command building to exclude URL when not needed

**Lines Modified:** ~100 lines
**New Method:** `on_scan_mode_change()` (35 lines)
**Updated Methods:** `validate_inputs()`, `start_scan()`, `create_widgets()`

---

## FAQs

**Q: Do I still need SharePoint URL for inventory mode?**  
A: No! Inventory mode only needs the folder path. SharePoint URL fields are hidden.

**Q: Can I switch modes after filling out fields?**  
A: Yes! Fields will show/hide automatically. Your folder path is preserved.

**Q: What happens if I select Pre-Flight but don't enter URL?**  
A: Validation will prevent the scan and show an error: "SharePoint URL is required for Pre-Flight checks."

**Q: Can I use inventory mode for cloud locations?**  
A: Yes! You can inventory any accessible folder (local, network, OneDrive sync folder).

**Q: Will old scans still work?**  
A: Yes! The CLI interface is unchanged. This only affects the GUI workflow.

**Q: Can I save my mode preference?**  
A: Not yet - mode resets to Pre-Flight on launch. Feature planned for future release.

---

## Version History

- **v2.1.1** (November 7, 2025)
  - Added scan mode selection as first step
  - Implemented dynamic field visibility
  - Updated validation logic for inventory mode
  - Improved user experience with clearer workflow

- **v2.1.0** (November 7, 2025)
  - Added inventory mode feature
  - Checkbox for inventory-only scans

---

## Next Steps

After reviewing this guide:

1. **Test both modes** - Run a quick inventory and a pre-flight check
2. **Review outputs** - Compare CSV formats for each mode
3. **Train your team** - Share this guide with migration team members
4. **Provide feedback** - Report any issues or suggestions

---

**Author:** 818Ninja Production Tool  
**Date:** November 7, 2025  
**Tool:** SharePoint Migration Preflight Scanner v2.1.1
