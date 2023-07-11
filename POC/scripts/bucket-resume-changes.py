#! /usr/bin/python3.9

import argparse
import boto3
import os
import re
import sys
import yaml
import json


with open( "config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )


usage=""
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
p.add_argument( "-v", "--verbose", action="store_true",
        help="optional print statements for more detail" )
p.add_argument( "-l", "--lifecycle",
        help="override default lifecycle policy, json format expected" )
p.add_argument( "-w", "--writearn",
        help="override default IAM write ARN for bucket" )
args = p.parse_args()


# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

if args.lifecycle:
    policyfile = args.lifecycle
else:
    policyfile = aws[ "lifecyclejson" ]
if args.verbose:
    print( "Using json file: {}".format( policyfile ) )

if args.writearn:
    iamarn = args.writearn
else:
    iamarn = "arn:aws:iam::{}:policy/{}-{}-uci-bkup-policy".format( aws[ "accountid" ], args.user, args.host )
if args.verbose:
    print( "Using IAM ARN: {}".format( iamarn ) )

with open( policyfile, "r" ) as fp:
    life_dict = json.load( fp )
    if args.verbose:
        print( json.dumps( life_dict, indent=2 ) )
    session = boto3.Session( profile_name=aws[ "profile" ] )
    s3 = session.client( "s3" )
    s3.put_bucket_lifecycle_configuration(
        Bucket="{}-{}-uci-bkup-bucket".format( args.user, args.host ),
        LifecycleConfiguration=life_dict
    )

iam = session.client( "iam" )
iam.attach_user_policy(
    UserName="{}-{}-sa".format( args.user, args, host ),
    PolicyArn=iamarn
)