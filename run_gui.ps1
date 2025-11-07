# SharePoint Online Migration Preflight Scanner - GUI Launcher (PowerShell)
# Right-click and select "Run with PowerShell" to launch the GUI

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SharePoint Migration Preflight Scanner" -ForegroundColor Cyan
Write-Host "GUI Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python detected: $pythonVersion" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.10 or later from:" -ForegroundColor Yellow
    Write-Host "https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$guiScript = Join-Path $scriptDir "gui_launcher.py"

# Check if GUI script exists
if (-not (Test-Path $guiScript)) {
    Write-Host "ERROR: gui_launcher.py not found in script directory" -ForegroundColor Red
    Write-Host "Expected location: $guiScript" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Launch the GUI
Write-Host "Starting GUI..." -ForegroundColor Green
Write-Host ""
python $guiScript

# If GUI closes with error, pause to show message
if ($LASTEXITCODE -ne 0 -and $null -ne $LASTEXITCODE) {
    Write-Host ""
    Write-Host "GUI closed with an error (exit code: $LASTEXITCODE)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
}
