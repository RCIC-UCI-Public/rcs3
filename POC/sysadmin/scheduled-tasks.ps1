# Powershell Script that Sets Up Scheduled Tasks
# 
$CURRENTCMD=$MyInvocation.MyCommand.Path
$CWD=Split-Path -Parent $CURRENTCMD
$RCS3ROOT="$CWD\..\.."
$LOCALBIN="$RCS3ROOT\..\bin"
$LOCKFILE="$RCS3ROOT\..\gen-backup.lock"
$LOGFILE="$RCS3ROOT\..\gen-backup.log"
$RCLONE="$LOCALBIN\rclone.exe"
$PYTHON="$RCS3ROOT\..\python311\python.exe"
$GENBACKUP="$PYTHON $CWD\..\sysadmin\gen-backup.py"
$COMMONARGS="-WindowStyle Hidden" 
#
# When to weekly sync verse daily top up
$syncDay = 'Sunday'
$topupDays = 'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'

# Backup command with commonly-used flags
$backupCmd = "$GENBACKUP  --parallel=1 --threads=4 --checkers=64 --rclonecmd=$RCLONE --lockfile=$LOCKFILE run" 

# Create the Weekly full sync
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $syncDay -At 12:30am
$action = New-ScheduledTaskAction -WorkingDirectory "$CWD\.." -Execute powershell.exe -Argument "$COMMONARGS -command $backupCmd >> $LOGFILE 2>&1" 
Register-ScheduledTask -TaskName 'Backup Weekly Sync' -Action $action -Trigger $trigger
echo $action

#
# Create the Daily Top (all days except Weekly Day)
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $topupDays -At 12:30am
$topupCmd = $backupCmd + " --top-up=24h"
$action = New-ScheduledTaskAction -WorkingDirectory "$CWD\.." -Execute powershell.exe -Argument "$COMMONARGS -command $topupCmd >> $LOGFILE 2>&1" 
Register-ScheduledTask -TaskName 'Backup Daily Top-up' -Action $action -Trigger $trigger
echo $action
