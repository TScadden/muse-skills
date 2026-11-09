# One-time setup, run by the user in their own session on the always-on
# computer: registers the AgyBridge scheduled task so it runs inside the
# interactive (logged-in) session, where the Antigravity sign-in works.
# Copy run.ps1 into a bridge folder first (default: %USERPROFILE%\agy-bridge)
# and run this script from that same folder.
$run = Join-Path $PSScriptRoot 'run.ps1'
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$run`""
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName 'AgyBridge' -Action $action -Principal $principal -Force | Out-Null
'registered'
