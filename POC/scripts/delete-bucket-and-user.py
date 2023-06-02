#! /usr/bin/python3

import argparse
import boto3


usage="Delete S3 bucket and IAM user, detach policies delete access keys"
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
args = p.parse_args()

#print( args.user, args.host )
acctname = args.user +  "-" + args.host + "-sa"
primarybucket = args.user + "-" + args.host + "-uci-bkup-bucket"
inventorybucket = args.user + "-" + args.host + "-uci-inventory"
profile="774954368688_AWSAdministratorAccess"
session = boto3.Session( profile_name=profile )

# s3 bucket cleanup
s3_client = session.client( "s3" )
try:
    s3_client.delete_bucket( Bucket=primarybucket )
except s3_client.exceptions.NoSuchBucket:
    print( "Bucket does not exist:", primarybucket )
try:
    s3_client.delete_bucket( Bucket=inventorybucket )
except s3_client.exceptions.NoSuchBucket:
    print( "Bucket does not exist:", inventorybucket )

# user account cleanup
iam_client = session.client( "iam" )
try:
    userpolicies = iam_client.list_attached_user_policies( UserName=acctname )
    #print( userpolicies )
    userkeys = iam_client.list_access_keys( UserName=acctname )
    #print( userkeys )
    for policies in userpolicies[ "AttachedPolicies" ]:
        policyarn = policies[ "PolicyArn" ]
        #print( policyarn )
        iam_client.detach_user_policy( UserName=acctname, PolicyArn=policyarn )
        iam_client.delete_policy( PolicyArn=policyarn )
    
    for keys in userkeys[ "AccessKeyMetadata" ]:
        #print( keys[ "AccessKeyId" ] )
        iam_client.delete_access_key( UserName=acctname, AccessKeyId=keys[ "AccessKeyId" ] )
    
    iam_client.delete_user( UserName=acctname )
except iam_client.exceptions.NoSuchEntityException:
    print( "Service account does not exist:", acctname )
