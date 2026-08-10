$DesktopPath = [System.Environment]::GetFolderPath('Desktop')
$ShortcutPath = Join-Path -Path $DesktopPath -ChildPath "Yahoo Nifty50 Screener.lnk"
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "d:\nifty50\Start_Yahoo_Screener.bat"
$Shortcut.WorkingDirectory = "d:\nifty50"
$Shortcut.Description = "Launch Yahoo Nifty50 Stock Screener App"
$Shortcut.IconLocation = "shell32.dll,13"
$Shortcut.Save()
Write-Host "Desktop shortcut successfully created at: $ShortcutPath"
