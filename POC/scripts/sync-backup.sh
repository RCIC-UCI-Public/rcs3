#!/bin/bash
# What to backup - change these for each backup set
SRCPATH=/pub/ppapadop
SRC_FOLDERS=(phylo tdlong-test)
BACKUP_NAME=backup-1

# Where to back it up
ENDPOINT=s3-tmpstore1
DESTPATH=${BACKUP_NAME}${SRCPATH}

MYDIR=$(dirname $(realpath $0))
CONFIGDIR=$MYDIR/../config
EXCLUSIONS=$CONFIGDIR/exclusions-global
RC_CONFIG_FILE=$HOME/.config/rclone/rclone.conf

# Create a filter file to include the subfolders above
INCTMP=$(mktemp --suffix=rc-include)
for x in ${SRC_FOLDERS[*]}; do
    echo "+ $x/**" >> $INCTMP
done
echo "- **" >> $INCTMP
## Global rclone flags
RC_FLAGS_GLOBAL="--metadata --links --config $RC_CONFIG_FILE"
RC_INCLUDE="--filter-from $INCTMP"

echo rclone sync --progress $RC_FLAGS_GLOBAL $RC_INCLUDE $SRCPATH $ENDPOINT:$DESTPATH
rclone sync --progress $RC_FLAGS_GLOBAL $RC_INCLUDE $SRCPATH $ENDPOINT:$DESTPATH

# Remove the temporary file
/bin/rm $INCTMP

