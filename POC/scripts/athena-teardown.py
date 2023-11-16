#! /usr/bin/python3

import argparse
import boto3
import os
import sys
import yaml

with open( "config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )


usage="Drop Athena table and database associated with user and host"
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
p.add_argument( "-v", "--verbose", action="store_true",
        help="optional print statements for more detail" )
args = p.parse_args()

# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

# when run from AWS services, profile is not used
if "profile" in aws:
    session = boto3.Session( profile_name=aws[ "profile" ] )
else:
    session = boto3

if "region" in aws:
    athena_client = session.client( "athena", region_name=aws[ "region" ] )
else:
    athena_client = session.client( "athena" )
# drop table
response = athena_client.start_query_execution( 
    QueryString="drop table if exists {}".format( args.host ),
    QueryExecutionContext={
        'Database': args.user
    },
    WorkGroup=args.user
)
if args.verbose:
    print( response[ "QueryExecutionId" ] )

# drop database
response = athena_client.start_query_execution( 
    QueryString="drop database if exists {}".format( args.user ),
    WorkGroup=args.user
)
if args.verbose:
    print( response[ "QueryExecutionId" ] )
