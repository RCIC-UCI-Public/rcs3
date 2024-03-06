#! /usr/bin/env python3

import argparse
import boto3
import botocore
import os
import sys
import yaml

execdir = os.path.dirname(os.path.abspath(__file__))
basedir = os.path.dirname( execdir )
sys.path.append( basedir  + "/common" )
from rcs3functions import delete_user_keys


usage="Delete S3 bucket and IAM user, detach policies, delete access keys"
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
p.add_argument( "-v", "--verbose", action="store_true",
        help="optional print statements for more detail" )
args = p.parse_args()

with open( basedir + "/config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )

# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

#print( args.user, args.host )
acctname = args.user +  "-" + args.host + "-sa"
primarybucket = args.user + "-" + args.host + "-" + aws[ "bucket_postfix" ]
inventorybucket = args.user + "-" + args.host + "-" + aws[ "inventory_postfix" ]
session = boto3.Session( profile_name=aws[ "profile" ] )

# s3 bucket cleanup
s3_client = session.client( "s3" )
for b in [ primarybucket, inventorybucket ]:
    try:
        s3_client.delete_bucket( Bucket=b )
    except s3_client.exceptions.NoSuchBucket:
        print( "Bucket does not exist:", b )
    except botocore.exceptions.ClientError as error:
        print( "Skipping:", b )
        print( error )

# user account cleanup
iam_client = session.client( "iam" )
try:
    userpolicies = iam_client.list_attached_user_policies( UserName=acctname )
    if args.verbose:
        print( userpolicies )
    userkeys = iam_client.list_access_keys( UserName=acctname )
    if args.verbose:
        print( userkeys )
    for policies in userpolicies[ "AttachedPolicies" ]:
        policyarn = policies[ "PolicyArn" ]
        if args.verbose:
            print( policyarn )
        iam_client.detach_user_policy( UserName=acctname, PolicyArn=policyarn )
        # need to handle policy versions, so disable policy deletion for now
        #iam_client.delete_policy( PolicyArn=policyarn )
    
    delete_user_keys( iam_client, acctname )
    
    iam_client.delete_user( UserName=acctname )
except iam_client.exceptions.NoSuchEntityException:
    print( "Service account does not exist:", acctname )
