@echo off
REM Build script for creating standalone EXE with PyInstaller

setlocal enabledelayedexpansion

echo ================================================================================
echo SPO Preflight Scanner - EXE Build Script
echo ================================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo PyInstaller is not installed. Installing now...
    echo.
    pip install pyinstaller
    
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
    
    echo.
    echo PyInstaller installed successfully!
    echo.
)

echo PyInstaller is ready.
echo.

REM Clean previous builds
if exist "build" (
    echo Cleaning previous build directory...
    rmdir /s /q "build"
)

if exist "dist" (
    echo Cleaning previous dist directory...
    rmdir /s /q "dist"
)

if exist "*.spec" (
    echo Removing old spec files...
    del /q "spo_preflight.spec" 2>nul
)

echo.
echo Building EXE...
echo ================================================================================
echo.

REM Build the EXE
pyinstaller --onefile ^
    --name SPOMigrationPreflight ^
    --console ^
    --add-data "README.md;." ^
    --add-data "EXAMPLES.md;." ^
    spo_preflight.py

if errorlevel 1 (
    echo.
    echo ================================================================================
    echo ERROR: Build failed
    echo ================================================================================
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo Build Complete!
echo ================================================================================
echo.

REM Check if EXE was created
if exist "dist\SPOMigrationPreflight.exe" (
    echo ✓ EXE created successfully!
    echo.
    echo Location: %cd%\dist\SPOMigrationPreflight.exe
    
    REM Get file size
    for %%A in ("dist\SPOMigrationPreflight.exe") do (
        set size=%%~zA
        set /a size_mb=!size! / 1048576
        echo Size: !size_mb! MB
    )
    
    echo.
    echo You can now:
    echo   1. Copy the EXE to any Windows machine (no Python needed)
    echo   2. Pin it to Start menu or Taskbar
    echo   3. Share it via network drive
    echo.
    echo Test it:
    echo   dist\SPOMigrationPreflight.exe --help
    echo.
) else (
    echo ✗ ERROR: EXE not found in dist folder
    pause
    exit /b 1
)

REM Optional: Test the EXE
set /p TEST="Do you want to test the EXE now? (Y/N): "
if /i "%TEST%"=="Y" (
    echo.
    echo Testing EXE...
    echo.
    dist\SPOMigrationPreflight.exe --help
)

echo.
pause
