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

with open( "config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )

usage="Create and attach a policy to an EC2 instance with access to specific resources."
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
    iam = session.client( "iam", region_name=aws[ "region" ] )
else:
    iam = session.client( "iam" )

# load the template which allows launching EC2 instance
input_template = basedir + "/templates/template-enduser-restore-trust.json"
if not os.path.isfile( input_template ):
    print( "Not found: {}".format( input_template ) )
    sys.exit( -1 )
with open( input_template, "r" ) as fp:
    json_policy = fp.read()

# add sanity checks
# test if bucket exists in case of typo on the command line
# test if user policy exists

# create the EC2 policy or lookup an existing policy
try:
    policy_arn = "arn:aws:iam::{}:policy/{}-{}-policy"\
        .format( aws[ "accountid" ], args.user, args.host )
    role_name = "{}-{}-restore".format( args.user, args.host )
    response = iam.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json_policy,
        Description="Allow EC2 instance to process Glacier restore requests for {} {}".format( args.user, args.host )
    )
    if args.verbose:
        print( response )
    response = iam.attach_role_policy(
        RoleName=role_name,
        PolicyArn=policy_arn
    )
    if args.verbose:
        print( response )
except Exception as error:
    print( type(error).__name__ )
    print( error )
    sys.exit( -1 )
