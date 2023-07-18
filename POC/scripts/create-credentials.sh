#! /bin/sh
# Creates the credentials file on stdout. Prompts for aws access and secret key
MYDIR=$(dirname $(realpath $0))
TEMPLATES_DIR=$MYDIR/../templates
if [ $# -ne 0 ] ; then
    echo $0 
    exit 0
fi

read -p "Enter AWS Access Key: " access_key 
read -p "Enter AWS Secret Accesss Key: " secret_access_key
cat $TEMPLATES_DIR/credentials.in | \
sed "/^aws_access_key/ c aws_access_key_id = $access_key" | \
sed "/^aws_secret_access_key/ c aws_secret_access_key = $secret_access_key"
