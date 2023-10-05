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

usage="Create and attach a policy to the service account to allow the launch of EC2 instances based on a pre-defined policy template."
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
p.add_argument( "-v", "--verbose", action="store_true",
        help="optional print statements for more detail" )
p.add_argument( "-u", "--useexisting", action="store_true",
        help="use existing policy, otherwise error if already exists" )
args = p.parse_args()

# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

# when run from AWS services, profile is not used
if "profile" in aws:
    session = boto3.Session( profile_name=aws[ "profile" ] )
else:
    session = boto3

iam = session.client( "iam" )

# load the template which allows launching EC2 instance
input_template = basedir + "/templates/template-enduser-restore-ec2-launch.json"
if not os.path.isfile( input_template ):
    print( "Not found: {}".format( input_template ) )
    sys.exit( -1 )
my_vars = {
    "xxxaccountidxxx": aws[ "accountid" ],
    "xxxregionxxx": aws[ "region" ]
}
json_policy = transform.template_to_string( input_template, my_vars )


# create the EC2 policy or lookup an existing policy
try:
    if args.useexisting:
        policy_arn = "arn:aws:iam::{}:policy/{}-{}-ec2-launch-policy"\
            .format( aws[ "accountid" ], args.user, args.host )
        response = iam.get_policy( PolicyArn=policy_arn )
    else:
        response = iam.create_policy(
            PolicyName="{}-{}-ec2-launch-policy".format( args.user, args.host ),
            PolicyDocument=json_policy,
            Description="Allow service account to launch EC2 instance for self-restore"
        )
        policy_arn = response[ "Policy" ][ "Arn" ]
except iam.exceptions.EntityAlreadyExistsException:
    print( "Policy already exists. Either delete or re-run with \"-u\"" )
    sys.exit( -1 )
except Exception as error:
    print( type(error).__name__ )
    print( error )
    sys.exit( -1 )
if args.verbose:
    print( response )


# attach the EC2 policy to the service account
response = iam.attach_user_policy(
    UserName="{}-{}-sa".format( args.user, args.host ),
    PolicyArn=policy_arn
)
if args.verbose:
    print( response )
