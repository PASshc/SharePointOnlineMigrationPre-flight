# SharePoint Online Migration Preflight Scanner - PowerShell Quick Launch
# This script provides an interactive way to run the scanner with validation

param(
    [Parameter(Mandatory=$false)]
    [string]$ScanPath,
    
    [Parameter(Mandatory=$false)]
    [string]$OutputDir
)

# Determine Desktop location (handle OneDrive redirection)
if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    if (Test-Path "$env:USERPROFILE\OneDrive\Desktop") {
        $OutputDir = "$env:USERPROFILE\OneDrive\Desktop"
    } else {
        $OutputDir = "$env:USERPROFILE\Desktop"
    }
}

function Write-Banner {
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host "SharePoint Online Migration Preflight Scanner" -ForegroundColor Cyan
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Test-PythonInstalled {
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Python detected: $pythonVersion" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Host "✗ Python is not installed or not in PATH" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please install Python 3.10 or later from:" -ForegroundColor Yellow
        Write-Host "https://www.python.org/downloads/" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Yellow
        return $false
    }
    return $false
}

function Get-ValidatedPath {
    param([string]$Path)
    
    while ([string]::IsNullOrWhiteSpace($Path) -or -not (Test-Path $Path)) {
        if (-not [string]::IsNullOrWhiteSpace($Path)) {
            Write-Host "✗ Path does not exist: $Path" -ForegroundColor Red
            Write-Host ""
        }
        
        $Path = Read-Host "Enter the path to scan (local or UNC)"
        
        if ([string]::IsNullOrWhiteSpace($Path)) {
            Write-Host "✗ Path cannot be empty" -ForegroundColor Red
            continue
        }
        
        # Remove quotes if present
        $Path = $Path.Trim('"')
    }
    
    return $Path
}

# Main script
Clear-Host
Write-Banner

# Check Python
if (-not (Test-PythonInstalled)) {
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Get and validate scan path
$ScanPath = Get-ValidatedPath -Path $ScanPath
Write-Host "✓ Scan path validated: $ScanPath" -ForegroundColor Green
Write-Host ""

# Generate timestamped output filenames
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$reportPath = Join-Path $OutputDir "SPOMigrationReport_$timestamp.csv"
$logPath = Join-Path $OutputDir "SPOMigrationLog_$timestamp.txt"

# Ensure output directory exists
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Scan Path:  $ScanPath"
Write-Host "  Report:     $reportPath"
Write-Host "  Log:        $logPath"
Write-Host ""

$confirm = Read-Host "Start scan? (Y/N)"
if ($confirm -notmatch '^[Yy]') {
    Write-Host "Scan cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Starting scan..." -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$scannerScript = Join-Path $scriptDir "spo_preflight.py"

# Run the scanner
& python $scannerScript $ScanPath --report $reportPath --log $logPath

$exitCode = $LASTEXITCODE

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "Scan Complete" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Interpret exit code
switch ($exitCode) {
    0 {
        Write-Host "✓ Status: SUCCESS - No issues found" -ForegroundColor Green
    }
    10 {
        Write-Host "⚠ Status: ISSUES FOUND - Check the report for details" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Opening report in Excel..." -ForegroundColor Cyan
        Start-Process $reportPath
    }
    default {
        Write-Host "✗ Status: ERROR - Exit code $exitCode" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Report saved to: $reportPath" -ForegroundColor Cyan
Write-Host "Log saved to:    $logPath" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to exit"
