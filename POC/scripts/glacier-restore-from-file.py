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


usage="Initiate a S3 Batch restore from Glacier for each line in the local file; each line should be an object in S3 in CVS format containing at minimum bucket, filename, and version id information for objects in Glacier"
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
        "ExpirationInDays": 7,
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

# when run from AWS services, profile is not used
if "profile" in aws:
    session = boto3.Session( profile_name=aws[ "profile" ] )
else:
    session = boto3

try:
    with open( args.objfile ) as fp:
        if "region" in aws:
            s3 = session.client( "s3", region_name=aws[ "region" ] )
            s3c = session.client( "s3control", region_name=aws[ "region" ] )
        else:
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
                print( obj_key_pair[0] )
                print( obj_key_pair[1] )
                # get ETag for object which is required for S3 Batch job
                response = s3.head_object( Bucket=obj_key_pair[0], Key=obj_key_pair[1] )
                # add ETag to manifest
                man_dict = {
                    "Spec": {
                        "Format": "S3BatchOperations_CSV_20180820",
                        "Fields": [
                            "Bucket", "Key", "VersionId"
                        ]
                    },
                    "Location": {
                        "ObjectArn": re.sub( "s3://", arnprefix, obj ),
                        "ETag": response[ "ETag" ].strip( '\"' )
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
                    Priority=10,
                    RoleArn="arn:aws:iam::{}:role/{}-{}-restore-s3batch-perms-role".format( aws[ "accountid" ], args.user, args.host )
                )
                if args.verbose:
                    print( response[ "JobId" ] )
                listjobs.append( response[ "JobId" ] )
    with open( results, "w" ) as f:
        for jobid in listjobs:
            f.write( "{}\n".format( jobid ) )
        print( "S3 Batch job ids saved to: {}".format( results ) )
except IOError:
    print( "could not read file: {}".format( args.objfile ) )
