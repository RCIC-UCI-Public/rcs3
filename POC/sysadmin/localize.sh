#! /bin/sh
# localizes rclone.conf and credentials to server
# call as: ./localize.sh <user> <host> 
MYDIR=$(dirname $(realpath $0))
TEMPLATES_DIR=$MYDIR/../templates
CONFIG_DIR=$MYDIR/../config
if [ $# -ne 2 ] ; then
    echo $0 user host
    exit 0
fi

user=$1
host=$2

echo "Localizing configuration for user $user on host $host"
if [ ! -f $CONFIG_DIR/rclone.conf ]; then
     echo "writing rclone.conf"
     $MYDIR/create-rclone-conf.sh $user $host > $CONFIG_DIR/rclone.conf
     chmod 600 $CONFIG_DIR/rclone.conf
fi
if [ ! -f $CONFIG_DIR/credentials ]; then
    echo "writing credentials"
    $MYDIR/create-credentials.sh > $CONFIG_DIR/credentials
    chmod 600 $CONFIG_DIR/credentials
fi
