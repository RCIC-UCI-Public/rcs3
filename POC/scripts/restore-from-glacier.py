#! /usr/bin/python3

import argparse
import boto3
import os
import sys
import yaml


usage="Submit S3 batch operation to restore objects from Glacier"
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
p.add_argument( "csv",
        help="csv object in related S3 report bucket" )
p.add_argument( "--bucket",
        help="override default bucket ARN" )
p.add_argument( "--useversionid", action="store_true",
        help="versionid in csv file, not implemented" )
p.add_argument( "--useinventorymanifest", action="store_true",
        help="use AWS S3 generated inventory manifest, not implemented" )
args = p.parse_args()

with open( "config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )

# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

# bucket to read csv file from and write report output to
reportbucket = args.user + "-" + args.host + "-uci-report"

op_dict = {
    "S3InitiateRestoreObject": {
        "ExpirationInDays": 1,
        "GlacierJobTier": "BULK"
    }
}
print( op_dict )

rep_dict = {
    "Bucket": "arn:aws:s3:::" + reportbucket,
    "Prefix": "batch-op-restore-job",
    "Format": "Report_CSV_20180820",
    "Enabled": True,
    "ReportScope": "FailedTasksOnly"
}
print( rep_dict )

s3 = session.client( "s3" )
# retrieve ETag
if "bucket" in args:
    bucketarn = args[ "bucket" ]
else:
    bucketarn = "arn:aws:s3:::" + reportbucket
response = s3.head_object( Bucket=bucketarn, Key=aws[ "csv" ] )
man_dict = {
    "Spec": {
        "Format": "S3BatchOperations_CSV_20180820",
        "Fields": [ "Bucket", "Key" ]
    },
    "Location": {
        "ObjectArn": bucketarn + aws[ "csv" ],
        "ETag": response[ "ETag" ]
    }
}
print( man_dict )

session = boto3.Session( profile_name=aws[ "profile" ] )

s3c = session.client( "s3control" )

response = s3c.create_job( 
    AccountId=aws[ "accountid" ],
    Operation=op_dict,
    Report=rep_dict,
    Manifest=man_dict,
    Description="restore from glacier job",
    Priority=0,
    RoleArn="arn:aws:iam::774954368688:role/read-restore-all-buckets-role"
)

print( response )