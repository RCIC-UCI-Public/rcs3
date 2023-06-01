#!/bin/bash
# Don't to glob expansion, want the --filter file to interpret
set -o noglob
# What to backup - change these for each backup set
SRCPATH=/pub/ppapadop
## An array of FILES relative to the top-level SRCPATH
SRC_FILES=(/*)
## and Array of DIRECTORIES relative to the top-level SRCPATH
SRC_FOLDERS=(phylo tdlong-test)

## Should be unique among backup jobs on this host
BACKUP_NAME=backup-1

# Where to back it up
ENDPOINT=s3-backup
DESTPATH=${BACKUP_NAME}${SRCPATH}

MYDIR=$(dirname $(realpath $0))
CONFIGDIR=$MYDIR/../config
EXCLUSIONS=$CONFIGDIR/exclusions-global
RC_CONFIG_FILE=$HOME/.config/rclone/rclone.conf

# Create a filter file to include the subfolders above
INCTMP=$(mktemp --suffix=rc-include)
for x in ${SRC_FILES[*]}; do
    echo "+ $x" >> $INCTMP
done
for x in ${SRC_FOLDERS[*]}; do
    echo "+ $x/**" >> $INCTMP
done
# catchall to exclude everything else
echo "- **" >> $INCTMP
# Create a logfile
LOGTMP=$(mktemp /tmp/$BACKUP_NAME-XXX.log)
## Global rclone flags
RC_FLAGS_GLOBAL="--metadata --links --config $RC_CONFIG_FILE"
RC_INCLUDE="--filter-from $INCTMP"

echo rclone $DRYRUN sync --log-file $LOGTMP  $RC_FLAGS_GLOBAL $RC_INCLUDE $SRCPATH $ENDPOINT:$DESTPATH
echo "=== RCLONE START: $(date)" > $LOGTMP 
rclone $DRYRUN sync --log-file $LOGTMP  --log-level INFO $RC_FLAGS_GLOBAL $RC_INCLUDE $SRCPATH $ENDPOINT:$DESTPATH
# Remove the temporary file
/bin/rm $INCTMP
echo "=== RCLONE END: $(date)" >> $LOGTMP 


