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
sys.path.append( basedir  + "/common" )

with open( basedir + "/config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )

usage="Create or update default IAM policy for service account"
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
p.add_argument( "-i", "--iprestrictions", nargs="*",
        help="override iprestrictions list in config file" )
p.add_argument( "-t", "--policy_template",
        help="override policy_template in config file" )
p.add_argument( "-v", "--verbose", action="store_true",
        help="optional print statements for more detail" )
g = p.add_mutually_exclusive_group()
g.add_argument( "-p", "--policy_postfix",
        help="override policy_postfix in config file" )
g.add_argument( "-n", "--policy_name",
        help="override policy name, ignoring user and host args" )
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

# load the policy template
if args.policy_template is None:
    input_template = aws[ "policy_template" ]
else:
    input_template = args.policy_template
environment = Environment(loader=FileSystemLoader(basedir + "/templates/"))
template = environment.get_template( input_template )

my_vars = {
    "user": args.user,
    "host": args.host,
    "bucket": aws[ "bucket_postfix" ],
    "inventory": aws[ "inventory_postfix" ],
    "accountid": aws[ "accountid" ],
    "region": aws[ "region" ],
    "ownernotify": aws[ "owner_notify" ],
    "adminnotify": aws[ "admin_notify" ]
}

if args.iprestrictions is None:
    if "iprestrictions" in aws.keys():
        my_vars[ "iprestrictions" ] = aws[ "iprestrictions" ]
else:
    my_vars[ "iprestrictions" ] = args.iprestrictions

json_policy = template.render( my_vars )
print( json_policy )

sys.exit(0)

# create the EC2 policy or lookup an existing policy
try:
    if args.policy_name is None:
        if args.policy_postfix is None:
            pp = aws[ "policy_postfix" ]
        else:
            pp = args.policy_postfix
        policy_name = "{}-{}-{}".format( args.user, args.host, pp )
    else:
    	policy_name = args.policy_name
    policy_arn = "arn:aws:iam::{}:policy/{}"\
        .format( aws[ "accountid" ], policy_name )
    response = iam.list_policy_versions( PolicyArn=policy_arn )
    if args.verbose:
        print( response )
    if len( response[ "Versions" ] ) > 4:
        vid = response[ "Versions" ][ 4 ][ "VersionId" ]
        response = iam.delete_policy_version( PolicyArn=policy_arn, VersionId=vid )
    response = iam.create_policy_version(
        PolicyArn=policy_arn,
        PolicyDocument=json_policy,
        SetAsDefault=True
    )
except iam.exceptions.NoSuchEntityException:
    print( "Creating policy: {}".format( policy_arn ) )
    response = iam.create_policy(
        PolicyName=policy_name,
        PolicyDocument=json_policy,
        Description="Allow service account access to {}-{}-{}".format( args.user, args.host, aws[ "bucket_postfix" ] ),
        Tags=[ { 'rcs3user': args.user }, { 'rcs3host': args.host } ]
    )
except Exception as error:
    print( type(error).__name__ )
    print( error )
    sys.exit( -1 )
if args.verbose:
    print( response )
