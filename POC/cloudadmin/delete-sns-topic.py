#! /usr/bin/env python3

import argparse
import boto3
import os
import sys
import yaml

scriptdir=os.path.realpath(os.path.dirname(__file__))
sys.path.append(os.path.join(scriptdir,"..","common"))
import rcs3functions as rcs3

configdir=os.path.normpath(os.path.join(scriptdir, "..","config"))
templatedir=os.path.normpath(os.path.join(scriptdir, "..","templates","alarms-bucket"))

aws=rcs3.read_aws_settings()


usage="""Delete an SNS topic for email notifications related to a specific S3 bucket."""
p = argparse.ArgumentParser( description=usage )
p.add_argument( "owner",
        help="user ID of owner" )
p.add_argument( "host",
        help="hostname" )
args = p.parse_args()


# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

# when run from AWS services, profile is not used
if "profile" in aws:
    session = boto3.Session( profile_name=aws[ "profile" ] )
else:
    session = boto3

if "region" in aws:
    sns_client = session.client( "sns", region_name=aws[ "region" ] )
else:
    sns_client = session.client( "sns" )


topic_arn=f"arn:aws:sns:{region}:{account_id}:{args.host}-{args.host}-{aws['owner_notify']}"
try:
    response = sns_client.delete_topic(
        TopicArn=topic_arn
    )
except:
    print( f"Topic not deleted: {topic_arn}" )
        
