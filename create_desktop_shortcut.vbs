' SharePoint Migration Preflight Scanner - Desktop Shortcut Creator
' Double-click this file to create a desktop shortcut to the GUI

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get the script's directory
strScriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Find Python executable
strPython = objShell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Programs\Python\Python312\pythonw.exe"
If Not objFSO.FileExists(strPython) Then
    ' Try alternative Python location
    strPython = objShell.ExpandEnvironmentStrings("%PROGRAMFILES%") & "\Python312\pythonw.exe"
End If
If Not objFSO.FileExists(strPython) Then
    ' Fallback to PATH python
    strPython = "pythonw.exe"
End If

' Get Desktop path
strDesktop = objShell.SpecialFolders("Desktop")

' Create shortcut
Set objShortcut = objShell.CreateShortcut(strDesktop & "\SPO Scanner.lnk")
objShortcut.TargetPath = strScriptPath & "\run_gui.bat"
objShortcut.WorkingDirectory = strScriptPath
objShortcut.Description = "SharePoint Migration Preflight Scanner - GUI"
objShortcut.IconLocation = strPython & ",0"
objShortcut.Save

' Show success message
MsgBox "Desktop shortcut created successfully!" & vbCrLf & vbCrLf & _
       "Look for 'SPO Scanner' on your desktop.", _
       vbInformation + vbOKOnly, "Shortcut Created"

Set objShortcut = Nothing
Set objFSO = Nothing
Set objShell = Nothing
