#! /usr/bin/env python3

import argparse
import boto3
import json
import os
import sys
import yaml

execdir = os.path.dirname(os.path.abspath(__file__))
basedir = os.path.dirname( execdir )

with open( basedir + "/config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )

usage="Permanently delete service account policy"
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
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


# lookup an existing policy
try:
    if args.policy_name is None:
        if args.policy_postfix is None:
            pp = aws[ "policy_postfix" ]
        else:
            pp = args.policy_postfix
        policy_arn = "arn:aws:iam::{}:policy/{}-{}-{}"\
            .format( aws[ "accountid" ], args.user, args.host, pp )
    else:
        policy_arn = "arn:aws:iam::{}:policy/{}"\
            .format( aws[ "accountid" ], args.policy_name )
    response = iam.list_policy_versions( PolicyArn=policy_arn )
    if args.verbose:
        print( response )
    # delete non default policy versions first
    for p in response[ "Versions" ]:
        if not p[ "IsDefaultVersion" ]:
            pvid = p[ "VersionId" ]
            if args.verbose:
                print( "deleting version id {}".format( pvid ) )
            response = iam.delete_policy_version(
                PolicyArn=policy_arn,
                VersionId=pvid
            )
    # delete default policy version
    if args.verbose:
        print( "deleting policy {}".format( policy_arn ) )
    response = iam.delete_policy(
        PolicyArn=policy_arn
    )
except iam.exceptions.NoSuchEntityException:
    print( "Policy not found: {}".format( policy_arn ) )
    sys.exit( 0 )
except Exception as error:
    print( type(error).__name__ )
    print( error )
    sys.exit( -1 )
