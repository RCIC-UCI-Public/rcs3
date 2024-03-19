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


usage="""Post a message to SNS in regards to a specific S3 bucket.""" 
p = argparse.ArgumentParser( description=usage )
p.add_argument( "owner",
        help="user ID of ownser" )
p.add_argument( "host",
        help="hostname" )
p.add_argument( "-m", "--message", dest="message", default="default SNS message",
        help="message to send" )
p.add_argument( "-s", "--subject", dest="subject", default="RCS3 Host Message",
        help="message to send" )
args = p.parse_args()


# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

session = boto3.Session( profile_name=aws[ "profile" ] )

# create list of emails to subscribe to SNS topic

sns_client = session.client( "sns" )
topic="{}-{}-{}".format( args.owner, args.host,aws['owner_notify'] )

try:
    mytopics = list(filter(lambda x: x['TopicArn'].endswith(topic), sns_client.list_topics()['Topics']))
    myArn = mytopics[0]['TopicArn']
    response = sns_client.publish( TopicArn=myArn, Message=args.message, Subject=args.subject )
except sns_client.exceptions.InvalidParameterException:
    print( "Invalid parameter, skipping: {}".format( m ) )
        
