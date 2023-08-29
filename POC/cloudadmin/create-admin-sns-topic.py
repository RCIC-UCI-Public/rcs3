#! /usr/bin/python3
import argparse
import boto3
import os
import sys
import yaml
scriptdir=os.path.realpath(os.path.dirname(__file__))
sys.path.append(os.path.join(scriptdir,"..","common"))
import rcs3functions as rcs3

aws=rcs3.read_aws_settings()

usage="""Create the admin SNS topic for email notifications related to an RCS3 admin account. 
Repeated calls add addresses to the SNS topic.  AWS checks for duplicate addresses.  
The subscribed address must confirm by responding to AWS confirmation message."""
p = argparse.ArgumentParser( description=usage )
p.add_argument( "-e", "--email", nargs="+",
        help="list of emails to add" )
args = p.parse_args()

# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

session = boto3.Session( profile_name=aws[ "profile" ] )

# create list of emails to subscribe to SNS topic
maillist=[]
if args.email:
    maillist += args.email


sns_client = session.client( "sns" )

# no error if topic already exists
response = sns_client.create_topic(
    Name="{}".format(aws['admin_notify'] )
)

for m in maillist:
    try:
        sns_client.subscribe(
            TopicArn=response[ "TopicArn" ],
            Protocol="email",
            Endpoint=m
        )
    except sns_client.exceptions.InvalidParameterException:
        print( "Invalid parameter, skipping: {}".format( m ) )
        
