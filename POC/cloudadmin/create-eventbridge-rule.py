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

with open( os.path.join( basedir, "config", "aws-settings.yaml" ), "r" ) as f:
    aws = yaml.safe_load( f )

usage="Create Eventbridge rule"
p = argparse.ArgumentParser( description=usage )
p.add_argument( "target",
        help="lambda function to use as rule target" )
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

ruleName = "rcs3-object-restore-completed"
ruleDesc = "capture S3 object restore completed events, Glacier to Standard transitions"
eventPattern = "{ \"detail-type\": [ \"Object Restore Completed\" ], \"source\": [ \"aws.s3\" ] }"
targetArn="arn:aws:lambda:{}:{}:function:{}".format( aws[ "region" ], aws[ "accountid" ], args.target )
try:
    # create rule, updates if already exists
    response = eventbridge.put_rule(
        Name=ruleName,
        EventPattern=eventPattern,
        State='ENABLED',
        Description=ruleDesc,
        EventBusName='default',
        Tags=[ { "Key": "RCS3", "Value": "restore" } ]
    )
    if args.verbose:
        print( response[ "RuleArn" ] )
    # add target to rule, updates if already exists
    response = eventbridge.put_targets(
        Rule=ruleName,
        EventBusName='default',
        Targets=[
            {
                'Id': args.target,
                'Arn': targetArn
            }
        ]
    )
    if args.verbose or response[ "FailedEntryCount" ] != 0:
        print( response )
except Exception as error:
    print( type(error).__name__ )
    print( error )
    sys.exit( -1 )
