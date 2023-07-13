#! /usr/bin/python3

import argparse
import boto3
import os
import re
import sys
import yaml
import json


with open( "config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )


usage=""
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
p.add_argument( "-v", "--verbose", action="store_true",
        help="optional print statements for more detail" )
args = p.parse_args()


# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

if "profile" in aws:
    session = boto3.Session( profile_name=aws[ "profile" ] )
else:
    session = boto3
s3 = session.client( "s3" )
bucketname = "{}-{}-uci-bkup-bucket".format( args.user, args.host )
# verify that bucket exists, ignore response, catch exception
try:
    s3.head_bucket( Bucket=bucketname )
except s3.exceptions.ClientError:
    print( "No S3 bucket: {}".format( bucketname ) )
    sys.exit(1)
# try to remove lifecycle policy, okay if not present
try:
    s3.delete_bucket_lifecycle_configuration(
        Bucket=bucketname
    )
except AttributeError:
    print( "No lifecycle present on: {}".format( bucketname ) )

iam = session.client( "iam" )
username = "{}-{}-sa".format( args.user, args.host )
# verify that user exists, ignore response, catch exception
try:
    iam.get_user(
        UserName=username
    )
except iam.exceptions.NoSuchEntityException:
    print( "Account not found: {}".format( username ) )
    sys.exit(1)
policyarn = "arn:aws:iam::{}:policy/{}-{}-uci-bkup-policy".format( aws[ "accountid" ], args.user, args.host )
# try to detach user policy, okay if not attached
try:
    iam.detach_user_policy(
        UserName=username,
        PolicyArn=policyarn
    )
except iam.exceptions.NoSuchEntityException:
    print( "Policy: {}".format( policyarn ) )
    print( "not attached to: {}".format( username ) )
