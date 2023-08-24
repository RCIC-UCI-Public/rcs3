#! /bin/bash
# Creates an rclone.conf file on stdout using the same user host pattern as buckets
MYDIR=$(dirname $(realpath $0))
TEMPLATES_DIR=$MYDIR/../templates
COMMON_DIR=$MYDIR/../common
source  <($COMMON_DIR/aws-settings-to-bash.py)

if [ $# -ne 2 ] ; then
    echo $0 user host
    exit 0
fi

user=$1
host=$2
cat $TEMPLATES_DIR/rclone.conf | \
sed s/xxxuserxxx/$user/ | \
sed s/xxxhostxxx/$host/ | \
sed s/xxxregionxxx/$RCS3_REGION/ | \
sed s/xxxbucketxxx/$RCS3_BUCKET_POSTFIX/ | \
sed s/xxxinventoryxxx/$RCS3_INVENTORY_POSTFIX/


