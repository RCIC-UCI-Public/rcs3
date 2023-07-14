#! /usr/bin/python3

import argparse
import boto3
import os
import re
import sys
import yaml


def extract_bucket_and_key_from_url( s ):
    # expected format s3://bucketname/path-to-object/object
    p = re.compile( '^s3://([^/]+)/(.+)' )
    m = p.match( s )
    if m:
        return m.groups()
    else:
        return m


with open( "config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )


usage=""
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
p.add_argument( "objfile",
        help="file containing S3 objects, one per line" )
p.add_argument( "-v", "--verbose", action="store_true",
        help="optional print statements for more detail" )
p.add_argument( "-o", "--output",
        help="override output file" )
args = p.parse_args()


listjobs = []
if args.output:
    results = args.output
else:
    results = "{}/{}-{}-glacier-jobids.txt".format( aws[ "outputdir"], args.user, args.host )
if args.verbose:
    print( "Saving output to: {}".format( results ) )


arnprefix = "arn:aws:s3:::"
op_dict = {
    "S3InitiateRestoreObject": {
        "ExpirationInDays": 1,
        "GlacierJobTier": "BULK"
    }
}
rep_dict = {
    "Bucket": re.sub( "s3://", arnprefix, aws[ "reports" ] ),
    "Prefix": "{}/{}".format( args.user, args.host ),
    "Format": "Report_CSV_20180820",
    "Enabled": True,
    "ReportScope": "FailedTasksOnly"
}
tag_list = [
    { "Key": "User", "Value": args.user },
    { "Key": "Host", "Value": args.host }
]
if args.verbose:
    print( op_dict )
    print( rep_dict )


# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

try:
    with open( args.objfile ) as fp:
        session = boto3.Session( profile_name=aws[ "profile" ] )
        s3 = session.client( "s3" )
        s3c = session.client( "s3control" )
        for rawobj in fp:
            obj = rawobj.strip()
            if args.verbose:
                print( obj )
            # retrieve ETag
            obj_key_pair = extract_bucket_and_key_from_url( obj )
            if not obj_key_pair:
                print( "skipping, could not parse: {}".format( obj ) )
            else:
                # get ETag for object which is required for S3 Batch job
                response = s3.head_object( Bucket=obj_key_pair[0], Key=obj_key_pair[1] )
                # add ETag to manifest
                man_dict = {
                    "Spec": {
                        "Format": "S3InventoryReport_CSV_20161130"
                    },
                    "Location": {
                        "ObjectArn": re.sub( "s3://", arnprefix, obj ),
                        "ETag": response[ "ETag" ]
                    }
                }
                if args.verbose:
                    print( man_dict )
                response = s3c.create_job( 
                    AccountId=aws[ "accountid" ],
                    Operation=op_dict,
                    Report=rep_dict,
                    Manifest=man_dict,
                    Description="restore from glacier for {} {}".format( args.user, args.host ),
                    Priority=0,
                    RoleArn="arn:aws:iam::774954368688:role/read-restore-all-buckets-role",
                    Tags=tag_list
                )
                if args.verbose:
                    print( response[ "JobId" ] )
                listjobs.append( response[ "JobId" ] )
    with open( results, "w" ) as f:
        for jobid in listjobs:
            f.write( "{}\n".format( jobid ) )
except IOError:
    print( "could not read file: {}".format( args.objfile ) )
