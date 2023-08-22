#! /bin/bash
# Creates an rclone.conf file on stdout using the same user host pattern as buckets
source  <(./aws-settings-to-bash.py)
MYDIR=$(dirname $(realpath $0))
TEMPLATES_DIR=$MYDIR/../templates

if [ $# -ne 2 ] ; then
    echo $0 user host
    exit 0
fi

user=$1
host=$2
cat $TEMPLATES_DIR/rclone.conf | \
sed s/xxxuserxxx/$user/ | \
sed s/xxxhostxxx/$host/ | \
sed s/xxxbucketxxx/$RCS3_BUCKET_POSTFIX/ | \
sed s/xxxinventoryxxx/$RCS3_INVENTORY_POSTFIX/


