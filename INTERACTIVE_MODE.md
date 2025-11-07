# Interactive Mode Guide

## Overview

Version 2.1.0 introduces an **interactive wizard** that guides you through configuring the scanner for accurate SharePoint Online path validation. This mode ensures the scanner calculates **SharePoint URL lengths** rather than just local path lengths, catching issues that would otherwise cause migration failures.

## Why Interactive Mode?

SharePoint Online has a **400-character URL limit**, not a 400-character local path limit. This means:

❌ **Wrong**: Checking `C:\Data\Project\file.txt` (30 chars) ✅ passes
✅ **Correct**: Checking `https://contoso.sharepoint.com/sites/Team/Shared Documents/Project/file.txt` (90 chars)

The difference is the **SharePoint URL overhead** (typically 50-120 characters) which includes:
- Tenant URL: `https://contoso.sharepoint.com` (~30 chars)
- Site path: `/sites/Team` (~12 chars)
- Library name: `/Shared Documents` (~18 chars)
- Path separators and encoding

## How to Use Interactive Mode

### Starting the Wizard

```cmd
python spo_preflight.py --interactive
```

### Wizard Steps

#### Step 1: Select Destination Type
```
Where will the content be migrated to?
  1 - SharePoint Online Document Library (includes Microsoft Teams sites)
  2 - OneDrive for Business
  Q - Quit

Enter your choice [1/2/Q]: 1
```

**Choose:**
- **1** if migrating to a SharePoint site (Team Site, Communication Site, **Microsoft Teams**)
- **2** if migrating to a user's OneDrive for Business

**Note**: Microsoft Teams sites are SharePoint sites and should use option 1.

#### Step 2: Enter Tenant URL

**For SharePoint (Option 1):**
```
SharePoint URL formats:
  • Root site:        https://<tenant>.sharepoint.com
  • Team/Site:        https://<tenant>.sharepoint.com/sites/<sitename>
  • Teams (legacy):   https://<tenant>.sharepoint.com/teams/<sitename>
Example: https://contoso.sharepoint.com/sites/Marketing

Enter tenant URL: https://contoso.sharepoint.com/sites/Team
✓ Valid URL: https://contoso.sharepoint.com/sites/Team
```

**Microsoft Teams URLs:**
- **Modern Teams**: Use `/sites/` path (e.g., `https://contoso.sharepoint.com/sites/MarketingTeam`)
- **Legacy Teams**: Use `/teams/` path (e.g., `https://contoso.sharepoint.com/teams/MarketingTeam`)
- Both formats work identically - Teams is built on SharePoint!

**For OneDrive (Option 2):**
```
OneDrive URL format: https://<tenant>-my.sharepoint.com
Example: https://contoso-my.sharepoint.com

Enter tenant URL: https://contoso-my.sharepoint.com
✓ Valid URL: https://contoso-my.sharepoint.com
```

**Important**: OneDrive URLs must contain `-my` between the tenant name and `.sharepoint.com`

#### Step 3: Enter Document Library Name

**For SharePoint:**
```
Examples:
  • 'Shared Documents' (default Document Library)
  • 'General' (default Teams channel - becomes 'General' folder)
  • 'ProjectFiles' (custom library)

Note: For Microsoft Teams, the channel name becomes a library.
      Most Teams use 'General' as the default channel.

Enter library name (or press Enter for 'Shared Documents'): General
✓ Library: General
```

**For Microsoft Teams**:
- Each Teams **channel** creates a folder in the "Documents" library
- The **General** channel is the default (most common)
- For other channels, use the exact channel name (e.g., "Marketing", "Projects")
- If unsure, navigate to your Team's Files tab in Teams - the URL shows the library name

**For OneDrive:**
```
✓ Using default OneDrive library: 'Documents'
```
*(This step is automatic for OneDrive)*

#### Step 4: Enter Local Path to Scan

```
Examples:
  • C:\Data\ProjectFiles
  • \\server\share\folder

Enter path to scan: C:\Data\Marketing
✓ Scan path: C:\Data\Marketing
```

The wizard validates that the path exists and is accessible.

#### Step 5: Review Configuration

```
======================================================================
Configuration Summary
======================================================================
Destination Type:  SharePoint Online Document Library
Tenant URL:        https://contoso.sharepoint.com/sites/Team
Document Library:  Shared Documents
Local Scan Path:   C:\Data\Marketing

SharePoint URL Base:    https://contoso.sharepoint.com/sites/Team/Shared%20Documents/
URL Overhead:           68 characters
Effective Path Limit:   332 characters
  (400 character limit - 68 overhead = 332 remaining)

======================================================================
Proceed with scan? [Y/n]:
```

Press **Y** to start the scan, or **n** to cancel.

## CLI Mode (Non-Interactive)

If you prefer command-line parameters:

### SharePoint Example
```cmd
python spo_preflight.py "C:\Data" ^
  --spo-url "https://contoso.sharepoint.com/sites/Team" ^
  --spo-library "Shared Documents"
```

### OneDrive Example
```cmd
python spo_preflight.py "C:\Data" ^
  --spo-url "https://contoso-my.sharepoint.com" ^
  --onedrive
```

### Legacy Mode (No SharePoint URL)
```cmd
python spo_preflight.py "C:\Data"
```
This uses an estimated overhead of 80 characters. **Not recommended** as it may produce false negatives.

## Understanding the Report

The CSV report now includes two path length columns:

| Column | Description | Example |
|--------|-------------|---------|
| `CharacterCountPath` | SharePoint URL length (primary validation) | 395 |
| `LocalPathLength` | Local Windows path length (reference only) | 250 |
| `SharePointURL` | Full SharePoint URL that will be created | `https://contoso.sharepoint.com/sites/Team/Shared%20Documents/folder/file.xlsx` |

### Example Issue Row

```csv
ItemType,FullPath,IssueType,CurrentValue,SuggestedFix,CharacterCount,CharacterCountPath,SharePointURL,LocalPathLength,FileSizeMB,FolderDepth
File,C:\Data\VeryLongFolder\AnotherFolder\YetAnotherFolder\file.xlsx,Path too long,SharePoint URL: 405 chars,Shorten to ≤400 chars (current: 405, limit: 400),9,405,https://contoso.sharepoint.com/sites/Team/Shared%20Documents/VeryLongFolder/AnotherFolder/YetAnotherFolder/file.xlsx,85,2.50,3
```

**Key Points:**
- `LocalPathLength`: 85 chars (would pass old validation ❌)
- `CharacterCountPath`: 405 chars (fails SharePoint validation ✅)
- This file would **fail migration** despite passing local path checks

## URL Format Validation

### Valid SharePoint URLs ✅
- `https://contoso.sharepoint.com`
- `https://contoso.sharepoint.com/sites/Team`
- `https://contoso.sharepoint.com/sites/Marketing/SubSite`

### Valid OneDrive URLs ✅
- `https://contoso-my.sharepoint.com`
- `https://northwind-my.sharepoint.com`

### Invalid URLs ❌
| URL | Reason |
|-----|--------|
| `http://contoso.sharepoint.com` | Must use HTTPS |
| `contoso.sharepoint.com` | Missing protocol |
| `https://contoso.sharepoint.com/` | Trailing slash (auto-removed) |
| `https://contoso-my.sharepoint.com/sites/Team` | OneDrive URLs don't have `/sites/` |
| `https://contoso.sharepoint.com` + OneDrive flag | SharePoint URL with OneDrive flag |
| `https://contoso-my.sharepoint.com` + SharePoint flag | OneDrive URL without OneDrive flag |

## Benefits of Interactive Mode

✅ **Accurate Validation**: Calculates actual SharePoint URL lengths
✅ **Fewer Migration Failures**: Catches path length issues before migration
✅ **User-Friendly**: Guided prompts with examples and validation
✅ **URL Validation**: Ensures correct format for SharePoint vs OneDrive
✅ **Overhead Calculation**: Shows exactly how much overhead your tenant/site adds
✅ **Configuration Summary**: Review all settings before scanning

## Troubleshooting

### "Path does not exist"
Ensure you enter the full path including drive letter or UNC path:
- ✅ `C:\Data\Marketing`
- ✅ `\\server\share\folder`
- ❌ `\Data\Marketing`

### "Invalid URL format"
Check that your URL:
- Starts with `https://`
- Contains `.sharepoint.com`
- For OneDrive: Contains `-my` (e.g., `contoso-my.sharepoint.com`)
- For SharePoint: Does NOT contain `-my`

### "This is a OneDrive URL. Please select OneDrive destination type instead."
You entered a URL with `-my.sharepoint.com` but selected SharePoint. Re-run and select **Option 2** (OneDrive).

### "OneDrive URL must contain '-my'"
You selected OneDrive but entered a SharePoint URL. The correct format for OneDrive is:
`https://<tenant>-my.sharepoint.com` (note the hyphen before `my`)

## Version History

- **v2.1.0**: Added interactive wizard and SharePoint URL validation
- **v2.0.0**: Initial release with basic path scanning

## Next Steps

After running the scan with interactive mode:

1. **Review the report**: Open `SPOMigrationReport.csv` in Excel
2. **Sort by `CharacterCountPath`**: Find files with longest SharePoint URLs
3. **Check `SharePointURL` column**: See the exact URL that will be created
4. **Fix issues**: Shorten folder names, move files up in hierarchy
5. **Re-scan**: Verify fixes by running the scanner again

For questions or issues, refer to the main [README.md](README.md) or submit an issue on GitHub.
