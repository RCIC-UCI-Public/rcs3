#! /usr/bin/python3.9

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


session = boto3.Session( profile_name=aws[ "profile" ] )
s3 = session.client( "s3" )
s3.delete_bucket_lifecycle_configuration(
        Bucket="{}-{}-uci-bkup-bucket".format( args.user, args.host )
)

iam = session.client( "iam" )
iam.deattach_user_policy(
    UserName="{}-{}-sa".format( args.user, args, host ),
    PolicyArn="arn:aws:iam::{}:policy/{}-{}-uci-bkup-policy".format( aws[ "accountid" ], args.user, args.host )
)