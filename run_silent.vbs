' VIRTUAL DRIVE — Silent Windows Launcher
' Launches Virtual Drive without displaying a command prompt console.
Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
currentDir = fso.GetParentFolderName(WScript.ScriptFullName)

WshShell.CurrentDirectory = currentDir
WshShell.Run "pythonw main.py", 0, False
