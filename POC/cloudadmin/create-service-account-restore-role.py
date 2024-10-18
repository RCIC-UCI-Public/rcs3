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

usage="Create role by attaching trust relationship to existing policy."
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
p.add_argument( "purpose",
        help="which trust relationship to apply" )
p.add_argument( "-v", "--verbose", action="store_true",
        help="optional print statements for more detail" )
p.add_argument( "-d", "--templatedir", dest="templatedir",default="templates/self-service",
        help="base directory to load trust/policy templates" )
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
input_template = basedir + "/{}/{}-trust.json".format( args.templatedir, args.purpose )
if not os.path.isfile( input_template ):
    print( "Not found: {}".format( input_template ) )
    sys.exit( -1 )
with open( input_template, "r" ) as fp:
    json_policy = fp.read()

# add sanity checks
# test if bucket exists in case of typo on the command line
# test if user policy exists

# lookup an existing policy
try:
    policy_arn = "arn:aws:iam::{}:policy/{}-{}-{}-policy"\
        .format( aws[ "accountid" ], args.user, args.host, args.purpose )
    role_name = "{}-{}-{}-role".format( args.user, args.host, args.purpose )
    response = iam.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json_policy,
        Description="Allow {} to process requests for {} {}".format( args.purpose, args.user, args.host )
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
