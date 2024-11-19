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

usage="Create or update IAM policy with access to specific resources determined by purpose."
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
    iam = session.client( "iam", region_name=aws[ "region" ] )
else:
    iam = session.client( "iam" )

# load the template which allows launching EC2 instance
input_template = basedir + "/templates/self-service/{}-policy.json".format( args.purpose )
if not os.path.isfile( input_template ):
    print( "Not found: {}".format( input_template ) )
    sys.exit( -1 )
my_vars = {
    "xxxuserxxx": args.user,
    "xxxhostxxx": args.host,
    "xxxbucketxxx": aws[ "bucket_postfix" ],
    "xxxinventoryxxx": aws[ "inventory_postfix" ],
    "xxxaccountidxxx": aws[ "accountid" ],
    "xxxregionxxx": aws[ "region" ],
    "xxxiprestrictionsxxx": transform.createPolicyIpCondition( aws[ "iprestrictions" ] )
}
json_policy = transform.template_to_string( input_template, my_vars )


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
        Tags=[ { 'rcs3user': args.user }, { 'rcs3host': args.host } ]
    )
except Exception as error:
    print( type(error).__name__ )
    print( error )
    sys.exit( -1 )
if args.verbose:
    print( response )
