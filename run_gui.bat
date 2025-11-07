@echo off
REM SharePoint Online Migration Preflight Scanner - GUI Launcher
echo.
echo SharePoint Migration Preflight Scanner v2.1.1
echo.

REM Launch the GUI
python "%~dp0gui_launcher.py"

REM Pause if there's an error
if errorlevel 1 pause
