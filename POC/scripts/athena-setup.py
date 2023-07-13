#! /usr/bin/python3

import argparse
import boto3
import datetime
import os
import sys
import yaml

with open( "config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )


usage=""
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
args = p.parse_args()

if not "schemafile" in aws:
    print( "Missing schema file in configuation settings" )
    sys.exit(1)

# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

# when run from AWS services, profile is not used
if "profile" in aws:
    session = boto3.Session( profile_name=aws[ "profile" ] )
else:
    session = boto3

s3 = session.client( "s3" )
# verify that bucket exists, ignore response, catch exception
bucketname="{}-{}-uci-inventory".format( args.user, args.host )
try:
    s3.head_bucket( Bucket=bucketname )
except s3.exceptions.ClientError:
    print( "No S3 bucket: {}".format( bucketname ) )
    sys.exit(1)
# verify that hive object exists, ignore response, catch exception
hivedir = "{1}-{2}-uci-bkup-bucket/{1}-{2}-daily/hive/dt={3}-01-00/".format( args.user, args.host, str(datetime.date.today()) )
hivesym = "{}symlink.txt".format( hivedir )
try:
    s3.head_object(
        Bucket=bucketname,
        Key=hivesym
    )
except s3.exceptions.NoSuchKey:
    print( "No key: {}".format( hivesym ) )
    sys.exit(1)

athena = session.client( "athena" )
# create the work group, okay if already exists
try:
    response = athena.create_work_group(
        Name=args.user,
        Configuration={
            'ResultConfiguration': {
                'OutputLocation': "{}/{}".format( aws[ "reports" ], args.user )
            },
            'EnforceWorkGroupConfiguration': False,
            'PublishCloudWatchMetricsEnabled': True
        }
    )
except athena.exceptions.InvalidRequestException:
    pass

# create database in default collection
response = athena.start_query_execution( 
    QueryString="create database if not exists {}".format( args.user ),
    WorkGroup=args.user
)

# load hive schema into table
with open( aws[ "schemafile" ], "r" ) as fp:
    loadschema = fp.read()
    response = athena.start_query_execution(
        QueryString=loadschema.format( "lopez", "mybucket", "keylocation" ),
        QueryExecutionContext={
            'Database': args.user
        },
        WorkGroup=args.user
    )
    print( response[ "QueryExecutionId" ] )