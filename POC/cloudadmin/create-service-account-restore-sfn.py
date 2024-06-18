#! /usr/bin/env python3

import argparse
import boto3
import json
import os
import sys
import yaml

execdir = os.path.dirname(os.path.abspath(__file__))
basedir = os.path.dirname( execdir )
sys.path.append( basedir  + "/common" )
import transform

with open( basedir + "/config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )

usage="Create or update Step Function with access to specific resources determined by purpose."
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
p.add_argument( "purpose",
        help="which permissions to apply" )
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
    sfn = session.client( "stepfunctions", region_name=aws[ "region" ] )
else:
    sfn = session.client( "stepfunctions" )

# load the template which allows launching EC2 instance
input_template = basedir + "/templates/self-service/sfn-{}.json".format( args.purpose )
if not os.path.isfile( input_template ):
    print( "Not found: {}".format( input_template ) )
    sys.exit( -1 )
my_vars = {
    "xxxuserxxx": args.user,
    "xxxhostxxx": args.host,
    "xxxbucketxxx": aws[ "bucket_postfix" ],
    "xxxinventoryxxx": aws[ "inventory_postfix" ],
    "xxxreportsxxx": aws[ "reports" ].removeprefix( "s3://"),
    "xxxaccountidxxx": aws[ "accountid" ],
    "xxxregionxxx": aws[ "region" ],
    "xxxowner_notifyxxx": aws[ "owner_notify" ]
}
sfnJson = transform.template_to_string( input_template, my_vars )
if args.verbose:
    print( sfnJson )

# create the step function
sfnName = "{}-{}-sfn-{}".format( args.user, args.host, args.purpose )
sfnRole = "arn:aws:iam::{}:role/{}-{}-restore-stepfunc-perms-role".format( aws[ "accountid" ], args.user, args.host)
sfnArn = "arn:aws:states:{}:{}:stateMachine:{}".format( aws[ "region" ], aws[ "accountid" ], sfnName )
try:
    response = sfn.create_state_machine(
        name=sfnName,
        definition=sfnJson,
        roleArn=sfnRole,
        type='STANDARD',
        publish=True
    )
    if args.verbose:
        print( response )
except sfn.exceptions.StateMachineAlreadyExists:
    print( "Updating existing state machine: {}".format( args.purpose ) )
    response = sfn.update_state_machine(
        stateMachineArn=sfnArn,
        definition=sfnJson,
        roleArn=sfnRole,
        publish=True
    )
    if args.verbose:
        print( response )
except Exception as error:
    print( type(error).__name__ )
    print( error )
    sys.exit( -1 )
