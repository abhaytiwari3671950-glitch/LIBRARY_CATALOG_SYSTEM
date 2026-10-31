Option Explicit
Dim sh, fs, folder, py, command, candidates, i
Set sh = CreateObject("WScript.Shell")
Set fs = CreateObject("Scripting.FileSystemObject")
folder = fs.GetParentFolderName(WScript.ScriptFullName)
sh.CurrentDirectory = folder
candidates = Array("C:\Program Files\Python314\pythonw.exe", "C:\Program Files\Python313\pythonw.exe", "C:\Program Files\Python312\pythonw.exe", "C:\Program Files\Python311\pythonw.exe")
py = ""
For i = 0 To UBound(candidates)
    If fs.FileExists(candidates(i)) Then
        py = candidates(i)
        Exit For
    End If
Next
If py = "" Then
    MsgBox "pythonw.exe not found. Check your Python installation.", vbExclamation, "LibraryFlow"
    WScript.Quit 1
End If
command = Chr(34) & py & Chr(34) & " " & Chr(34) & fs.BuildPath(folder, "LibraryFlow.pyw") & Chr(34)
sh.Run command, 0, False
