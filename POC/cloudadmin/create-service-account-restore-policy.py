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
templatedir = os.path.join( basedir, "templates" )
sys.path.append( libdir )

with open( os.path.join( basedir, "config", "aws-settings.yaml" ), "r" ) as f:
    aws = yaml.safe_load( f )

usage="Create or update IAM policy with access to specific resources determined by purpose."
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
p.add_argument( "purpose",
        help="which permissions to apply" )
p.add_argument( "-i", "--iprestrictions", action="append",
        help="override iprestrictions list in config file" )
p.add_argument( "-t", "--template", dest="policy_template", default=None,
        help="specify a non-default policy  template file" )
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

# load the policy template
if args.policy_template is None:
    input_template = aws[ "policy_template" ]
else:
    input_template = args.policy_template
environment = Environment(loader=FileSystemLoader(templatedir))
template = environment.get_template( input_template )

my_vars = {
    "OWNER": args.user,
    "SYSTEM": args.host,
    "BUCKET_POSTFIX": aws[ "bucket_postfix" ],
    "INVENTORY_POSTFIX": aws[ "inventory_postfix" ],
    "ACCOUNT": aws[ "accountid" ],
    "REGION": aws[ "region" ]
}

if args.iprestrictions is None:
    if "iprestrictions" in aws.keys():
        my_vars[ "iprestrictions" ] = aws[ "iprestrictions" ]
else:
    my_vars[ "iprestrictions" ] = args.iprestrictions

json_policy = template.render( my_vars )
if args.verbose:
    print( json_policy )


# create the EC2 policy or lookup an existing policy
try:
    policy_arn = "arn:aws:iam::{}:policy/{}-{}-{}-policy"\
        .format( aws[ "accountid" ], args.user, args.host, args.purpose )
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
        PolicyName="{}-{}-{}-policy".format( args.user, args.host, args.purpose ),
        PolicyDocument=json_policy,
        Description="Allow {} access to {}-{}-{}".format( args.purpose, args.user, args.host, aws[ "bucket_postfix" ] ),
        Tags=[ { 'Key':'rcs3user','Value':args.user }, { 'Key':'rcs3host', 'Value':args.host } ]
    )
except Exception as error:
    print( type(error).__name__ )
    print( error )
    sys.exit( -1 )
if args.verbose:
    print( response )
