#! /usr/bin/python3

import argparse
import boto3
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

# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

session = boto3.Session( profile_name=aws[ "profile" ] )

athena_client = session.client( "athena" )
# drop table
response = athena_client.start_query_execution( 
    QueryString="drop table if exists {}".format( args.host ),
    QueryExecutionContext={
        'Database': args.user
    },
    WorkGroup=args.user
)
print( response[ "QueryExecutionId" ] )

# drop database
response = athena_client.start_query_execution( 
    QueryString="drop database if exists {}".format( args.user ),
    WorkGroup=args.user
)
print( response[ "QueryExecutionId" ] )