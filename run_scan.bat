@echo off
REM SharePoint Online Migration Preflight Scanner - Quick Launch Script
REM This batch file makes it easy to run the scanner with common defaults

setlocal enabledelayedexpansion

echo ================================================================================
echo SharePoint Online Migration Preflight Scanner
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
    pause
    exit /b 1
)

echo Python detected:
python --version
echo.

REM Set default output paths (Desktop - try OneDrive location first, fallback to standard)
if exist "%USERPROFILE%\OneDrive\Desktop" (
    set "OUTPUT_DIR=%USERPROFILE%\OneDrive\Desktop"
) else (
    set "OUTPUT_DIR=%USERPROFILE%\Desktop"
)
set TIMESTAMP=%date:~-4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set "TIMESTAMP=!TIMESTAMP: =0!"
set "REPORT_PATH=!OUTPUT_DIR!\SPOMigrationReport_!TIMESTAMP!.csv"
set "LOG_PATH=!OUTPUT_DIR!\SPOMigrationLog_!TIMESTAMP!.txt"

echo Report will be saved to: !REPORT_PATH!
echo Log will be saved to:    !LOG_PATH!
echo.
echo Starting interactive wizard...
echo ================================================================================
echo.

REM Run the scanner in interactive mode
python "%~dp0spo_preflight.py" --interactive --report "!REPORT_PATH!" --log "!LOG_PATH!"

set "EXIT_CODE=!ERRORLEVEL!"

echo.
echo ================================================================================
echo Scan Complete
echo ================================================================================

if !EXIT_CODE!==0 (
    echo Status: SUCCESS - No issues found
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
