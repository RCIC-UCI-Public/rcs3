#! /usr/bin/python3

import argparse
import boto3
import os
import sys
import yaml

with open( "config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )


usage="Create an SNS topic for email notifications related to a specific S3 bucket. The default action is to add user@uci.edu.  Repeated calls add addresses to the SNS topic.  AWS checks for duplicate addresses.  The subscribed address must confirm by responding to AWS confirmation message."
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
p.add_argument( "-e", "--email", nargs="+",
        help="list of emails to add in addition to the PI" )
p.add_argument( "-x", "--exclude", action="store_true",
        help="do not include the PI email" )
args = p.parse_args()


# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

# create list of emails to subscribe to SNS topic
maillist=[]
if not args.exclude:
    maillist.append( "{}@uci.edu".format( args.user ) )
if args.email:
    maillist += args.email


session = boto3.Session( profile_name=aws[ "profile" ] )

sns_client = session.client( "sns" )

# no error if topic already exists
response = sns_client.create_topic(
    Name="{}-{}-uci-notify".format( args.user, args.host )
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
        