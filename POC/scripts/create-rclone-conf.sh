#! /bin/sh
# Creates an rclone.conf file on stdout using the same user host pattern as buckets
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
sed s/xxxhostxxx/$host/ 
