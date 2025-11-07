@echo off
REM SharePoint Online Migration Preflight Scanner - Quick Launch Script
REM This batch file makes it easy to run the scanner with common defaults

setlocal enabledelayedexpansion

echo ================================================================================
echo SharePoint Online Migration Preflight Scanner v2.1.1
echo ================================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.10 or later from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    echo ────────────────────────────────────────────────────────────────────────────
    echo ALTERNATIVE: Use the portable EXE version (no Python needed)
    echo Run: build_portable_exe.bat to create a USB-ready standalone version
    echo ────────────────────────────────────────────────────────────────────────────
    echo.
    pause
    exit /b 1
)

echo Python detected:
python --version
echo.

REM Ask user what type of scan to perform
echo ────────────────────────────────────────────────────────────────────────────
echo Select Scan Mode:
echo ────────────────────────────────────────────────────────────────────────────
echo.
echo  1 = Pre-Flight Check (scan for SharePoint migration issues)
echo  2 = Inventory Only (create complete file/folder list with counts)
echo.
set /p SCAN_MODE="Enter your choice (1 or 2): "
echo.

if "%SCAN_MODE%"=="2" (
    set "MODE_NAME=Inventory"
    set "INVENTORY_FLAG=--inventory-only"
) else (
    set "MODE_NAME=PreFlight"
    set "INVENTORY_FLAG="
)

REM Set default output paths (Desktop - try OneDrive location first, fallback to standard)
if exist "%USERPROFILE%\OneDrive\Desktop" (
    set "OUTPUT_DIR=%USERPROFILE%\OneDrive\Desktop"
) else (
    set "OUTPUT_DIR=%USERPROFILE%\Desktop"
)
set TIMESTAMP=%date:~-4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set "TIMESTAMP=!TIMESTAMP: =0!"

if "%SCAN_MODE%"=="2" (
    set "REPORT_PATH=!OUTPUT_DIR!\SPO_Inventory_!TIMESTAMP!.csv"
) else (
    set "REPORT_PATH=!OUTPUT_DIR!\SPO_PreFlight_!TIMESTAMP!.csv"
)
set "LOG_PATH=!OUTPUT_DIR!\SPO_!MODE_NAME!_Log_!TIMESTAMP!.txt"

echo Report will be saved to: !REPORT_PATH!
echo Log will be saved to:    !LOG_PATH!
echo.

if "%SCAN_MODE%"=="2" (
    echo ────────────────────────────────────────────────────────────────────────────
    echo INVENTORY MODE
    echo ────────────────────────────────────────────────────────────────────────────
    echo This will create a complete inventory of all files and folders.
    echo Perfect for pre/post migration comparison!
    echo.
    
    REM For inventory, only need the scan path
    set /p SCAN_PATH="Enter folder path to inventory: "
    echo.
    echo Starting inventory scan...
    echo ────────────────────────────────────────────────────────────────────────────
    echo.
    
    python "%~dp0spo_preflight.py" --scan-path "!SCAN_PATH!" !INVENTORY_FLAG! --inventory-report "!REPORT_PATH!" --log "!LOG_PATH!"
    
) else (
    echo ────────────────────────────────────────────────────────────────────────────
    echo PRE-FLIGHT CHECK MODE
    echo ────────────────────────────────────────────────────────────────────────────
    echo This will scan for SharePoint migration issues.
    echo.
    echo Starting interactive wizard...
    echo ────────────────────────────────────────────────────────────────────────────
    echo.
    
    REM Run the scanner in interactive mode
    python "%~dp0spo_preflight.py" --interactive --report "!REPORT_PATH!" --log "!LOG_PATH!"
)

set "EXIT_CODE=!ERRORLEVEL!"

echo.
echo ================================================================================
echo Scan Complete
echo ================================================================================

if !EXIT_CODE!==0 (
    if "%SCAN_MODE%"=="2" (
        echo Status: SUCCESS - Inventory created
        echo.
        echo Opening inventory in Excel...
        start "" "!REPORT_PATH!"
    ) else (
        echo Status: SUCCESS - No issues found
    )
) else if !EXIT_CODE!==10 (
    echo Status: ISSUES FOUND - Check the report for details
    echo.
    echo Opening report in Excel...
    start "" "!REPORT_PATH!"
) else (
    echo Status: ERROR - Exit code !EXIT_CODE!
)

echo.
echo Report saved to: !REPORT_PATH!
echo Log saved to:    !LOG_PATH!
echo.
pause
