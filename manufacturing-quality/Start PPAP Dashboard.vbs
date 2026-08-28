Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
folder = fso.GetParentFolderName(WScript.ScriptFullName)
bat = folder & "\run-dashboard.bat"
If Not fso.FileExists(bat) Then
  MsgBox "run-dashboard.bat not found in:" & vbCrLf & folder, vbCritical, "PPAP Dashboard"
  WScript.Quit 1
End If
shell.CurrentDirectory = folder
shell.Run "cmd /k """ & bat & """", 1, False
