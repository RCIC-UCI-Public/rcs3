#! /usr/bin/env python3

import argparse
import boto3
import os
import sys
import json
import yaml


execdir = os.path.dirname(os.path.abspath(__file__))
basedir = os.path.dirname( execdir )

usage="List all objects, including delete markers, in a specific S3 bucket"
p = argparse.ArgumentParser( description=usage )
p.add_argument( "bucket",
        help="S3 bucket name without s3:// prefix" )
p.add_argument( "-f", "--folderprefix", default="",
        help="limit results to matching folder prefix" )
p.add_argument( "-m", "--maxkeys", type=int, default=1000,
        help="maximum number of objects to include per file" )
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
    while processData:
        response = s3.list_object_versions(
            Bucket=args.bucket,
            Prefix=args.folderprefix,
            KeyMarker=nextKeyMarker,
            MaxKeys=args.maxkeys
        )
        if args.verbose:
            print( response[ "IsTruncated" ] )
        processData = response[ "IsTruncated" ]
        if "NextKeyMarker" in response.keys():
            nextKeyMarker = response[ "NextKeyMarker" ]
            if args.verbose:
                print( nextKeyMarker )
        else:
            nextKeyMarker = ""
        objs = []
        for rkey in [ "Versions", "DeleteMarkers" ]:
            if rkey in response.keys():
                if args.verbose:
                    print( len( response[ rkey ] ) )
                # only save the key and versionid since the next step is deletion
                for i in response[ rkey ]:
                    o = {}
                    o[ "Key" ] = i[ "Key" ]
                    o[ "VersionId" ] = i[ "VersionId" ]
                    objs.append( o )
        object_count = len( objs )
        if args.verbose:
            print( "deleting {} objects".format( object_count ) )
        if object_count > 0:
            wrapper = {}
            wrapper[ "Objects" ] = objs
            wrapper[ "Quiet" ] = True
            deleteresponse = s3.delete_objects(
                Bucket=args.bucket,
                Delete=wrapper
            )
            if "Errors" in deleteresponse.keys():
                print( deleteresponse[ "Errors" ] )
except s3.exceptions.NoSuchBucket:
    print( "Bucket does not exist:", args.bucket )
