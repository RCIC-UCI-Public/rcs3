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

from rcs3functions import *

usage="Create or update Step Function with access to specific resources determined by purpose."
p = argparse.ArgumentParser( description=usage )
p.add_argument( "owner",
        help="owner" )
p.add_argument( "system",
        help="system" )
p.add_argument( "purpose",
        help="which permissions to apply" )
p.add_argument( "-v", "--verbose", action="store_true",
        help="optional print statements for more detail" )
args = p.parse_args()

aws = read_aws_settings()
# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

## Create boto3Clients. 
b3 = boto3Clients()

# load the step function template
input_template = "sfn-{}.json.jinja".format( args.purpose )
environment = Environment(loader=FileSystemLoader(templatedir))
template = environment.get_template( input_template )
my_vars = {
    "OWNER": args.owner,
    "SYSTEM": args.system,
    "BUCKET_POSTFIX": aws[ "bucket_postfix" ],
    "INVENTORY_POSTFIX": aws[ "inventory_postfix" ],
    "ACCOUNT": aws[ "accountid" ],
    "REGION": aws[ "region" ],
    "OWNER_NOTIFY": aws[ "owner_notify" ]
}
sfnJson = template.render( my_vars )
if args.verbose:
    print( sfnJson )

#sys.exit(0)

# create the step function
sfnName = "{}-{}-sfn-{}".format( args.owner, args.system, args.purpose )
sfnRole = "arn:aws:iam::{}:role/{}-{}-restore-stepfunc-perms-role".format( aws[ "accountid" ], args.owner, args.system)
sfnArn = "arn:aws:states:{}:{}:stateMachine:{}".format( aws[ "region" ], aws[ "accountid" ], sfnName )
try:
    response = b3.SFN.create_state_machine(
        name=sfnName,
        definition=sfnJson,
        roleArn=sfnRole,
        type='STANDARD',
        tags=[
            { 'key': 'rcs3owner', 'value': args.owner },
            { 'key': 'rcs3system', 'value': args.system }
        ],
        publish=True
    )
    if args.verbose:
        print( response )
except b3.SFN.exceptions.StateMachineAlreadyExists:
    print( "Updating existing state machine: {}".format( args.purpose ) )
    response = b3.SFN.update_state_machine(
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
