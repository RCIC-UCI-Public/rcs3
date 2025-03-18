#! /usr/bin/env python3

import argparse
import boto3
import json
import os
import sys
import yaml
from jinja2 import Environment, FileSystemLoader

execdir = os.path.dirname(os.path.abspath(__file__))
basedir = os.path.dirname( execdir )
libdir = os.path.join( basedir, "common" )
templatedir = os.path.join( basedir, "templates", "self-service" )
sys.path.append( libdir )

aws_settings = os.path.join( basedir, "config", "aws-settings.yaml" )
with open( aws_settings, "r" ) as f:
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

# load the step function template
input_template = "sfn-{}.json.jinja".format( args.purpose )
environment = Environment(loader=FileSystemLoader(templatedir))
template = environment.get_template( input_template )
my_vars = {
    "user": args.user,
    "host": args.host,
    "bucket": aws[ "bucket_postfix" ],
    "inventory": aws[ "inventory_postfix" ],
    "accountid": aws[ "accountid" ],
    "region": aws[ "region" ],
    "owner_notify": aws[ "owner_notify" ]
}
sfnJson = template.render( my_vars )
if args.verbose:
    print( sfnJson )

sys.exit(0)

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
        tags=[
            { 'key': 'rcs3user', 'value': args.user },
            { 'key': 'rcs3host', 'value': args.host }
        ],
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
