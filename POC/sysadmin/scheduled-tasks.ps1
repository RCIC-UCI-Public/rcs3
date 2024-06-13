# Powershell Script that Sets Up Scheduled Tasks
# 
# Call as
#    scheduled-tasks.ps1 
# This will create  daily and weekly backup tasks that were built when localize.py was run
#   config/weekly-backup.ps1
#   config/daily-backup.ps1 
#

$CURRENTCMD=$MyInvocation.MyCommand.Path
$CWD=Split-Path -Parent $CURRENTCMD
$RCS3ROOT="$CWD\..\.."
$CONFIGDIR="$CWD\..\config"
$COMMONARGS="-WindowStyle Hidden" 
#
# When to weekly sync verse daily top up
$syncDay = 'Sunday'
$topupDays = 'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'

# Backup command with commonly-used flags
$backupCmd = "$CONFIGDIR\weekly-backup.ps1"

# Find the principal and 
$principal = New-ScheduledTaskPrincipal -UserId "NT AUTHORITY\SYSTEM" -LogonType ServiceAccount -RunLevel Highest
# Create the Weekly full sync
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $syncDay -At 12:30am
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable
$action = New-ScheduledTaskAction -WorkingDirectory "$CWD\.." -Execute powershell.exe -Argument "$COMMONARGS -command $backupCmd"
Register-ScheduledTask -TaskName 'Backup Weekly Sync' -Principal $principal -Action $action -Trigger $trigger -Settings $settings
echo $action

#
# Create the Daily Top (all days except Weekly Day)
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $topupDays -At 12:30am
$topupCmd = "$CONFIGDIR\daily-backup.ps1" 
$action = New-ScheduledTaskAction -WorkingDirectory "$CWD\.." -Execute powershell.exe -Argument "$COMMONARGS -command $topupCmd"
Register-ScheduledTask -TaskName 'Backup Daily Top-up' -Principal $principal -Action $action -Trigger $trigger
echo $action
