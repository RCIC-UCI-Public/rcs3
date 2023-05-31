#! /bin/sh

if [ $# -ne 2 ] ; then
    echo $u user-host json-file
    exit 0
fi

if [ ! -f $2 ] ; then
    echo $2 must be a file
    exit 0
fi
awsprofile=774954368688_AWSAdministratorAccess

bucketname=${1}-uci-bkup-bucket
aws --profile $awsprofile s3api delete-objects --bucket $bucketname \
    --no-cli-pager --delete file://$2
