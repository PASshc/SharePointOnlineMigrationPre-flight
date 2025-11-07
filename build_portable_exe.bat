@echo off
REM Build Portable EXE Package

setlocal enabledelayedexpansion

echo ================================================================================
echo SPO Preflight Scanner - PORTABLE USB BUILD
echo ================================================================================
echo.
echo This creates a portable package that runs from USB on any Windows PC
echo with NO Python or dependencies required!
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
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo Building GUI EXE...
echo.

REM Clean previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q *.spec 2>nul

REM Build the GUI EXE
pyinstaller --onefile --name SPOMigrationPreflight_GUI --windowed --add-data "images;images" gui_launcher.py

if errorlevel 1 (
    echo ERROR: GUI build failed
    pause
    exit /b 1
)

REM Build the CLI EXE
echo Building CLI EXE...
pyinstaller --onefile --name SPOMigrationPreflight_CLI --console spo_preflight.py

if errorlevel 1 (
    echo ERROR: CLI build failed
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo Creating Portable Package...
echo ================================================================================
echo.

REM Create package folder
set PACKAGE_DIR=SPO_Preflight_Portable
if exist "%%PACKAGE_DIR%%" rmdir /s /q "%%PACKAGE_DIR%%"
mkdir "%%PACKAGE_DIR%%"

REM Copy executables
echo Copying executables...
copy "dist\SPOMigrationPreflight_CLI.exe" "%%PACKAGE_DIR%%\" >nul
copy "dist\SPOMigrationPreflight_GUI.exe" "%%PACKAGE_DIR%%\" >nul

REM Copy documentation
echo Copying documentation...
copy "README.md" "%%PACKAGE_DIR%%\" >nul 2>&1
copy "INVENTORY_MODE.md" "%%PACKAGE_DIR%%\" >nul 2>&1

REM Copy images
if exist "images" xcopy "images" "%%PACKAGE_DIR%%\images\" /E /I /Y >nul

REM Create GUI launcher
echo @echo off > "%%PACKAGE_DIR%%\Launch_GUI.bat"
echo echo Starting SharePoint Migration Preflight Scanner GUI... >> "%%PACKAGE_DIR%%\Launch_GUI.bat"
echo "%%~dp0SPOMigrationPreflight_GUI.exe" >> "%%PACKAGE_DIR%%\Launch_GUI.bat"
echo if errorlevel 1 pause >> "%%PACKAGE_DIR%%\Launch_GUI.bat"

REM Create CLI help
echo @echo off > "%%PACKAGE_DIR%%\Show_CLI_Help.bat"
echo "%%~dp0SPOMigrationPreflight_CLI.exe" --help >> "%%PACKAGE_DIR%%\Show_CLI_Help.bat"
echo pause >> "%%PACKAGE_DIR%%\Show_CLI_Help.bat"

echo.
echo ================================================================================
echo BUILD COMPLETE!
echo ================================================================================
echo.
echo Portable package created in: %D:\devSHC\_SPOMigrationPre-Flight_v2%\%%PACKAGE_DIR%%
echo.
echo Copy the entire folder to USB and run Launch_GUI.bat on any Windows PC!
echo.
pause
