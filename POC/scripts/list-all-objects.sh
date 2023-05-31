#! /bin/sh

awsprofile=774954368688_AWSAdministratorAccess

if [ $# -eq 2 ] ; then
    folder="--prefix $2"
else
    folder=""
fi

bucketname=${1}-uci-bkup-bucket
aws --profile $awsprofile s3api list-object-versions --bucket $bucketname  $folder --no-cli-pager

