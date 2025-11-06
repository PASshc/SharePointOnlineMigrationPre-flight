# Example Configuration for SPO Preflight Scanner

This directory contains sample configuration files showing how to run the scanner
with different settings for various scenarios.

## Scenario 1: Stanford Health Care Default
```powershell
python spo_preflight.py "\\enterprise.stanfordmed.org\depts\DSS\_4fpa" `
  --report "C:\Reports\SHC_DSS_PreflightReport.csv" `
  --log "C:\Reports\SHC_DSS_PreflightLog.txt" `
  --max-path 400 `
  --max-filename 255 `
  --max-file-size-gb 250 `
  --max-depth 20 `
  --blocked-extensions .exe .dll .bat .cmd .vbs .ps1
```

## Scenario 2: Conservative Settings (Stricter)
For tenants with more restrictive policies:
```powershell
python spo_preflight.py "C:\Data" `
  --max-path 350 `
  --max-filename 200 `
  --max-file-size-gb 100 `
  --max-depth 15 `
  --blocked-extensions .exe .dll .bat .cmd .vbs .ps1 .msi .app .deb .zip
```

## Scenario 3: Relaxed Settings
For initial assessments or less critical migrations:
```powershell
python spo_preflight.py "C:\Data" `
  --max-path 400 `
  --max-filename 255 `
  --max-file-size-gb 250 `
  --max-depth 30 `
  --blocked-extensions .exe .dll
```

## Scenario 4: OneDrive-Specific (Personal)
OneDrive personal has some slightly different limits:
```powershell
python spo_preflight.py "C:\Users\John\Documents" `
  --max-path 400 `
  --max-filename 255 `
  --max-file-size-gb 250 `
  --max-depth 20 `
  --blocked-extensions .exe .dll .bat .cmd .vbs
```

## Scenario 5: Teams-Backed SharePoint Sites
```powershell
python spo_preflight.py "\\server\TeamShare" `
  --max-path 400 `
  --max-filename 255 `
  --max-file-size-gb 100 `
  --max-depth 20 `
  --blocked-extensions .exe .dll .bat .cmd .vbs .ps1 .jar
```

## Creating Your Own Configuration

1. Copy one of the examples above
2. Modify the paths and thresholds
3. Save as a `.ps1` file in this directory
4. Run: `powershell -ExecutionPolicy Bypass -File your_config.ps1`

## Batch Processing Multiple Shares

Create a PowerShell script to scan multiple locations:

```powershell
# scan_multiple.ps1
$shares = @(
    "\\server\share1",
    "\\server\share2",
    "\\server\share3"
)

foreach ($share in $shares) {
    $shareName = ($share -replace '\\', '_').Trim('_')
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    
    Write-Host "Scanning: $share" -ForegroundColor Cyan
    
    python spo_preflight.py $share `
      --report "C:\Reports\${shareName}_${timestamp}.csv" `
      --log "C:\Reports\${shareName}_${timestamp}.log"
    
    Write-Host "Completed: $share" -ForegroundColor Green
    Write-Host ""
}

Write-Host "All scans complete!" -ForegroundColor Green
```
