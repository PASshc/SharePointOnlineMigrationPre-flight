@echo off
REM SharePoint Online Migration Preflight Scanner - GUI Launcher
REM Double-click this file to launch the graphical interface

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

REM Launch the GUI
echo Starting SharePoint Migration Preflight Scanner GUI...
echo.
python "%~dp0gui_launcher.py"

REM If GUI closes with error, pause to show message
if errorlevel 1 (
    echo.
    echo GUI closed with an error.
    pause
)
