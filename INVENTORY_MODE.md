# Inventory Mode Documentation

## Overview

The **Inventory Mode** feature creates a complete inventory of all files and folders in your scan path, providing detailed statistics for pre/post migration verification and comparison.

## What is Inventory Mode?

Unlike the standard scan mode that checks for migration issues, Inventory Mode:

- ✅ **Lists ALL files and folders** (not just problem items)
- ✅ **Counts files and folders** with summary statistics
- ✅ **Calculates total size** in MB and GB
- ✅ **Includes metadata** like modified dates, extensions, depth
- ✅ **Generates SharePoint URLs** for each item (if configured)
- ✅ **Skips issue checking** for faster scans

## Use Cases

### 1. Pre-Migration Baseline
Create an inventory **before** migration to establish:
- Total file/folder counts
- Total data size
- File distribution by type
- Folder structure depth

### 2. Post-Migration Verification
Create an inventory **after** migration to:
- Compare counts with pre-migration baseline
- Verify all files were migrated
- Identify any missing items
- Validate folder structure

### 3. Change Tracking
Run periodic inventories to:
- Track file growth over time
- Monitor storage usage trends
- Identify inactive folders
- Audit file type distribution

### 4. Migration Planning
Use inventory data to:
- Estimate migration duration
- Plan batching strategies
- Identify large files that need special handling
- Understand folder depth for path planning

---

## How to Use Inventory Mode

### Option 1: GUI Interface (Easiest)

1. Launch the GUI: `run_gui.bat` or `python gui_launcher.py`
2. Fill in destination details (SharePoint/Teams/OneDrive URL)
3. Select folder to scan
4. **✓ Check "Inventory Only" checkbox** in Section 5
5. Click "START SCAN"
6. Wait for completion
7. Open the inventory CSV when prompted

**Result:** `SPOMigrationInventory_YYYYMMDD_HHMMSS.csv` on your Desktop

---

### Option 2: Command Line

```cmd
python spo_preflight.py "C:\Data" --spo-url "https://contoso.sharepoint.com/sites/Team" --spo-library "Shared Documents" --inventory-only
```

**Result:** `SPOMigrationInventory.csv` in current directory

---

### Option 3: Custom Output Path

```cmd
python spo_preflight.py "C:\Data" --inventory-only --inventory-report "C:\Reports\PreMigration_Inventory.csv"
```

---

## Inventory CSV Format

The inventory CSV contains the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| **ItemType** | File or Folder | File |
| **FileName** | Name with extension | Document1.docx |
| **Extension** | File extension (lowercase) | .docx |
| **FullPath** | Complete local path | C:\Data\Docs\Document1.docx |
| **ParentPath** | Parent folder path | C:\Data\Docs |
| **FileSizeMB** | Size in MB (files only) | 2.45 |
| **FolderDepth** | Depth from scan root | 2 |
| **SharePointURL** | Calculated SPO URL | https://contoso.sharepoint.com/sites/Team/Shared%20Documents/Docs/Document1.docx |
| **SiteURLCount** | SharePoint URL length | 112 |
| **CharacterCountPath** | Local path length | 28 |
| **ModifiedDate** | Last modified timestamp | 2025-11-07 14:23:15 |

---

## Summary Statistics

At the end of each inventory CSV, a summary section is included:

```
=== INVENTORY SUMMARY ===
Total Files:        1,234
Total Folders:      56
Total Items:        1,290
Total Size (MB):    12,345.67
Total Size (GB):    12.05
```

---

## Comparing Pre/Post Migration Inventories

### Step 1: Create Pre-Migration Baseline
```cmd
python spo_preflight.py "C:\Data" --inventory-only --inventory-report "PreMigration.csv"
```

**Record these values:**
- Total Files: ________
- Total Folders: ________
- Total Size (GB): ________

---

### Step 2: Migrate Data to SharePoint
Perform your migration using:
- SharePoint Migration Tool
- Third-party migration software
- Manual upload

---

### Step 3: Create Post-Migration Inventory

**Option A: Scan SharePoint site (if accessible locally)**
```cmd
python spo_preflight.py "\\server\SPOMigrated" --inventory-only --inventory-report "PostMigration.csv"
```

**Option B: Export SharePoint inventory using PowerShell**
Use SharePoint PnP PowerShell to list all files/folders after migration.

---

### Step 4: Compare Inventories

Open both CSV files in Excel and compare:

| Metric | Pre-Migration | Post-Migration | Match? |
|--------|---------------|----------------|--------|
| Total Files | 1,234 | 1,234 | ✓ |
| Total Folders | 56 | 56 | ✓ |
| Total Size (GB) | 12.05 | 12.05 | ✓ |

**Advanced Comparison:**
- Sort both CSVs by `FullPath` or `FileName`
- Use Excel VLOOKUP to find missing items
- Compare file sizes to detect corruption
- Check modified dates for data integrity

---

## Performance Considerations

### Inventory Mode is Faster
- **No issue checking** = less processing per item
- **No validation** = fewer CPU cycles
- **Streamlined output** = faster CSV writing

### Expected Scan Speeds

| Item Count | Estimated Duration | Notes |
|------------|-------------------|-------|
| 1,000 | 10-30 seconds | Local drive |
| 10,000 | 1-3 minutes | Local drive |
| 100,000 | 10-30 minutes | Local drive |
| 1,000 | 30 seconds - 2 minutes | Network UNC path |
| 10,000 | 5-15 minutes | Network UNC path (use --workers 8) |

### Speed Tips
1. **Use local drive** for fastest scans
2. **Network paths**: Add `--workers 8` for parallel scanning
3. **Exclude temp folders**: Speeds up scan significantly
4. **SSD vs HDD**: SSDs are 2-5x faster

---

## Example Use Case Workflow

### Scenario: Migrating 50,000 files (100 GB) to SharePoint

**Week 1: Planning**
```cmd
# Create baseline inventory
python spo_preflight.py "\\server\FileShare\HR" --inventory-only --inventory-report "HR_PreMigration.csv"

# Results:
# Total Files: 47,823
# Total Folders: 2,156
# Total Size (GB): 98.45
```

**Week 2: Migration**
- Use SharePoint Migration Tool
- Migrate in batches of 10,000 files
- Monitor progress

**Week 3: Verification**
```cmd
# Create post-migration inventory
python spo_preflight.py "\\server\NewSPOMount\HR" --inventory-only --inventory-report "HR_PostMigration.csv"

# Results:
# Total Files: 47,823 ✓ MATCH
# Total Folders: 2,156 ✓ MATCH
# Total Size (GB): 98.45 ✓ MATCH
```

**Outcome:** Successful migration verified with 100% accuracy!

---

## Advanced Filtering

### Exclude System Files
```cmd
python spo_preflight.py "C:\Data" --inventory-only --exclude-dirs "node_modules" ".git" "$RECYCLE.BIN"
```

### Exclude Temp Files
```cmd
python spo_preflight.py "C:\Data" --inventory-only --exclude-exts ".tmp" ".bak" ".log"
```

### Full Scan (No Exclusions)
```cmd
python spo_preflight.py "C:\Data" --inventory-only --exclude-dirs --exclude-exts
```

---

## Inventory vs Standard Mode Comparison

| Feature | Standard Mode | Inventory Mode |
|---------|---------------|----------------|
| **Purpose** | Find migration blockers | Count & list all items |
| **Speed** | Slower (validates everything) | Faster (list only) |
| **Output** | Issues CSV | Complete inventory CSV |
| **File Count** | Only problematic files | ALL files |
| **Folder Count** | Only deep folders | ALL folders |
| **Size Calculation** | Large files only | ALL files totaled |
| **Use Case** | Pre-migration remediation | Pre/post verification |
| **Summary Stats** | Issue counts by type | File/folder/size totals |

---

## Tips & Best Practices

### ✓ DO:
- Run inventory **before** AND **after** migration
- Save inventory CSVs with descriptive names (include dates)
- Compare file counts between pre/post inventories
- Use inventory to estimate migration duration
- Archive inventory CSVs for audit trails

### ✗ DON'T:
- Use inventory mode to find issues (use standard mode instead)
- Delete pre-migration inventory before verifying post-migration
- Scan during heavy file activity (results may be inconsistent)
- Forget to configure SharePoint URL (needed for accurate URL calculations)

---

## Troubleshooting

### "No items found in inventory scan"
- Check that the scan path exists
- Verify you have read permissions
- Check if exclusion filters are too aggressive

### "Permission denied accessing directory"
- Run as Administrator
- Check folder permissions
- Verify network share access

### "Inventory CSV is incomplete"
- Check log file for errors
- Look for permission issues in specific folders
- Verify disk space for output file

### "File counts don't match pre/post migration"
- Check for excluded system folders (.git, node_modules, etc.)
- Verify same exclusion settings were used in both scans
- Look for files still in use or locked during scan

---

## Command-Line Reference

### Basic Inventory Scan
```cmd
python spo_preflight.py <PATH> --inventory-only
```

### With SharePoint URL
```cmd
python spo_preflight.py <PATH> --spo-url <URL> --spo-library <LIBRARY> --inventory-only
```

### Custom Output Path
```cmd
python spo_preflight.py <PATH> --inventory-only --inventory-report <OUTPUT.csv>
```

### With Parallel Processing (Network Paths)
```cmd
python spo_preflight.py <UNC_PATH> --inventory-only --workers 8
```

### Full Example
```cmd
python spo_preflight.py "\\server\share\HR" ^
  --spo-url "https://contoso.sharepoint.com/sites/HR" ^
  --spo-library "Documents" ^
  --inventory-only ^
  --inventory-report "C:\Reports\HR_Inventory_PreMigration.csv" ^
  --log "C:\Reports\HR_Inventory.log" ^
  --workers 8 ^
  --progress
```

---

## Integration with Excel/Power BI

### Excel Analysis
1. Open inventory CSV in Excel
2. Create PivotTable for:
   - File count by extension
   - Folder count by depth
   - Size distribution
3. Use COUNTIF/SUMIF for custom metrics

### Power BI Dashboard
1. Import inventory CSV as data source
2. Create visualizations:
   - Treemap of file sizes
   - Bar chart of file types
   - Line chart of folder depth distribution
3. Build pre/post migration comparison dashboard

---

## FAQ

**Q: Can I use inventory mode without configuring SharePoint URL?**  
A: Yes, but SharePoint URL columns will show "N/A". Local path info will still be captured.

**Q: Does inventory mode check for issues?**  
A: No, it only lists items. Use standard mode for issue detection.

**Q: How long does inventory scanning take?**  
A: Depends on file count and location. ~1-3 minutes per 10,000 files on local drives.

**Q: Can I run inventory mode on OneDrive/Teams?**  
A: Yes, use `--onedrive` flag or select OneDrive in GUI.

**Q: Will inventory mode show hidden files?**  
A: Yes, unless they match exclusion patterns (e.g., .git, node_modules).

**Q: Can I cancel an inventory scan?**  
A: Yes, press Ctrl+C in CLI or click "STOP SCAN" in GUI.

---

## Version History

- **v2.1.0** - Added inventory mode feature
- Introduced `--inventory-only` flag
- Added summary statistics to inventory CSV
- GUI checkbox for easy inventory mode selection

---

**Need Help?**
- Check [README.md](README.md) for general usage
- See [QUICK_START.md](QUICK_START.md) for examples
- Review [LAUNCHER_GUIDE.md](LAUNCHER_GUIDE.md) for GUI instructions

---

**Author:** 818Ninja Production Tool  
**License:** MIT  
**Last Updated:** November 7, 2025
