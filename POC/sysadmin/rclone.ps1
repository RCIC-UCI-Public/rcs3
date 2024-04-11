# Powershell Script that invokes the localized version of rclone with
# The flags of gen-backups 
# 
# Call as
#    rclone.ps1 <arguments> 
#
# example:
#     ./rclone.ps1 listremotes
#     ./rclone.ps1 lsd s3:backup:
#

$CURRENTCMD=$MyInvocation.MyCommand.Path
$CWD=Split-Path -Parent $CURRENTCMD
$RCS3ROOT="$CWD/../.."
$LOCALBIN="$RCS3ROOT/../bin"
$RCLONE="$LOCALBIN/rclone.exe"
$PYTHON="$RCS3ROOT/../python311/python.exe"
$GENBACKUP="$CWD/../sysadmin/gen-backup.py"
$RCLONEARG="--rclonecmd=$RCLONE"

## run Gen-backup with the rclone command to get the full path to rclone and all arguments
## that should be passed to rclone
$rawString = & $PYTHON $GENBACKUP $RCLONEARG rclone 

# Clean up the output string and split it
$cleanString = $rawString -replace "[\\]", "/"
$FULLRCLONE = $cleanString.Split(" ", [StringSplitOptions]::None) | Where-Object { $_ -ne "" } 

# Now invoke rclone with the arguments passed to this scripts
& $FULLRCLONE[0] $($FULLRCLONE[1..$FULLRCLONE.GetUpperBound(0)]) $args 
