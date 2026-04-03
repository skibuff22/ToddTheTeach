$TaskName = "ToddTheTeach_Calyx_Progress_Updater"
$ScriptPath = "C:\Users\tdoan\OneDrive\Documents\GitHub\ToddTheTeach\executions\update_calyx_progress.py"
$PythonExe = "py" # assuming py is in PATH on Windows

# Delete if exists to recreate
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# The action to run Python script
$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument $ScriptPath -WorkingDirectory "C:\Users\tdoan\OneDrive\Documents\GitHub\ToddTheTeach\"

# Run every day at 12:00 PM
$Trigger = New-ScheduledTaskTrigger -Daily -At "12:00 PM"

# Run whether user is logged on or not, if possible, but simplest is Interactive so it doesn't need passwords
$Principal = New-ScheduledTaskPrincipal -UserId (Get-CimInstance Win32_ComputerSystem | Select-Object -ExpandProperty UserName) -LogonType Interactive

$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Description "Automatically pulls Calyx AI progress from Excel and deploys to ToddTheTeach."

Write-Host "Scheduled task '$TaskName' has been set up successfully to run daily at 12:00 PM."
