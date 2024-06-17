#! /usr/bin/env python3

import argparse
import boto3
import json
import os
import sys
import yaml

execdir = os.path.dirname( os.path.abspath( __file__ ))
basedir = os.path.dirname( execdir )
sys.path.append( os.path.join( basedir, "common" ))

import transform

with open( os.path.join( basedir, "config", "aws-settings.yaml" ), "r" ) as f:
    aws = yaml.safe_load( f )

usage="Enable/disable S3 bucket sending notifications to EventBridge"
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
p.add_argument( "state",
        help="enable or disable" )
p.add_argument( "-v", "--verbose", action="store_true",
        help="optional print statements for more detail" )
args = p.parse_args()

if not aws[ "state" ] in [ "enable", "disable" ]:
    print( "Unknown state: %s".format( aws[ "state" ] ) )
    sys.exit(0)

# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

# when run from AWS services, profile is not used
if "profile" in aws:
    session = boto3.Session( profile_name=aws[ "profile" ] )
else:
    session = boto3

if "region" in aws:
    s3 = session.client( "s3", region_name=aws[ "region" ] )
else:
    s3 = session.client( "s3" )

bucketname = "{}-{}-{}".format( args.user, args.host, aws[ "bucket_postfix" ] )
if aws[ "state" ] is "enable":
    response = s3.put_bucket_notification_configuration(
        Bucket = bucketname,
        NotificationConfiguration = {
            "EventBridgeConfiguration": {}
        }

# assumes previous state was completely empty, otherwise need to save and restore prior state
if aws[ "state" ] is "disable":
    response = s3.put_bucket_notification_configuration(
        Bucket = bucketname,
        NotificationConfiguration = {}
