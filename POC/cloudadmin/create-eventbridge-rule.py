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

usage="Create Eventbridge rule"
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

# when run from AWS services, profile is not used
if "profile" in aws:
    session = boto3.Session( profile_name=aws[ "profile" ] )
else:
    session = boto3

if "region" in aws:
    eventbridge = session.client( "events", region_name=aws[ "region" ] )
else:
    eventbridge = session.client( "events" )

ruleName = "{}-{}-rule".format( args.user, args.host)
eventPattern = "{ \"detail-type\": [ \"Object Restore Completed\" ], \"source\": [ \"aws.s3\" ], \"requester\": [ \"s3.amazonaws.com\" ] }"
try:
    response = eventbridge.put_rule(
        Name=ruleName,
        EventPattern=eventPattern,
        State='DISABLED',
        Description=ruleName,
        EventBusName='default'
    )
    if args.verbose:
        print( response[ "RuleArn" ] )
except Exception as error:
    print( type(error).__name__ )
    print( error )
    sys.exit( -1 )


#response = client.put_targets(
#    Rule='string',
#    EventBusName='string',
#    Targets=[
#        {
#            'Id': 'string',
#            'Arn': 'string',
#            'RoleArn': 'string',
#        },
#    ]
#)