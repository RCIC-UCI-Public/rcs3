#! /usr/bin/env python3.11

import argparse
import boto3
import os
import sys
import yaml

execdir = os.path.dirname(os.path.abspath(__file__))
basedir = os.path.dirname( execdir )

usage="Remove all lifecycle and inventory configurations for a bucket"
p = argparse.ArgumentParser( description=usage )
p.add_argument( "bucket",
        help="S3 bucket name without s3:// prefix" )
p.add_argument( "-v", "--verbose", action="store_true",
        help="optional print statements for more detail" )
args = p.parse_args()

with open( basedir + "/config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )

# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]


session = boto3.Session( profile_name=aws[ "profile" ] )

s3 = session.client( "s3" )
processData = True
nextKeyMarker = ""
try:
    # ignore response
    s3.delete_bucket_lifecycle(
        Bucket=args.bucket
    )
    while processData:
        response = s3.list_bucket_inventory_configurations(
            Bucket=args.bucket,
            ContinuationToken=nextKeyMarker
        )
        if args.verbose:
            print( response[ "IsTruncated" ] )
        processData = response[ "IsTruncated" ]
        if "ContinuationToken" in response.keys():
            nextKeyMarker = response[ "ContinuationToken" ]
        else:
            nextKeyMarker = ""
        if args.verbose:
            print( nextKeyMarker )
        if "InventoryConfigurationList" in response.keys():
            for ic in response["InventoryConfigurationList"]:
                if args.verbose:
                    print( ic[ "Id" ] )
                # ignore response
                s3.delete_bucket_inventory_configuration(
                    Bucket=args.bucket,
                    Id=ic[ "Id" ]
                )
        else:
            if args.verbose:
                print( "No inventory configuration found." )
except s3.exceptions.NoSuchBucket:
    print( "Bucket does not exist:", args.bucket )
