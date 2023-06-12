#! /usr/bin/python3

import argparse
import boto3
import os
import sys
import yaml

#sys.path.append( "scripts" )
#from commonfunctions import delete_user_keys


usage="Delete S3 bucket and IAM user, detach policies, delete access keys"
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
args = p.parse_args()

with open( "config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )

# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

#print( args.user, args.host )
acctname = args.user +  "-" + args.host + "-sa"
primarybucket = args.user + "-" + args.host + "-uci-bkup-bucket"
inventorybucket = args.user + "-" + args.host + "-uci-inventory"
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

man_dict = {
    "Spec": {
        "Format": "S3BatchOperations_CSV_20180820",
        "Fields": [ "Bucket", "Key" ]
    },
    "Location": {
        "ObjectArn": "arn:aws:s3:::" + inventorybucket + "/myrestore.csv",
        "ETag": "7d815a1cad7c4496122b7c02eff7a1ae"
    }
}
print( man_dict )

session = boto3.Session( profile_name=aws[ "profile" ] )

s3c = session.client( "s3control" )

response = s3c.create_job( 
    AccountId="774954368688",
    Operation=op_dict,
    Report=rep_dict,
    Manifest=man_dict,
    Description="restore from glacier job",
    Priority=0,
    RoleArn="arn:aws:iam::774954368688:role/read-restore-all-buckets-role"
)

print( response )