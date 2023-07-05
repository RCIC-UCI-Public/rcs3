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
p.add_argument( "queryfile",
        help="file containing strings to query" )
p.add_argument( "-l", "--limit", type=int,
        help="set a limit on return results" )
args = p.parse_args()

if args.limit:
    limits = " limit {}".format( args.limit )
else:
    limits = ""
# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

session = boto3.Session( profile_name=aws[ "profile" ] )

try:
    with open( args.queryfile ) as fp:
        athena_client = session.client( "athena" )
        for filename in fp:
            query = "select * from {} where filename like '{}' and storage_class like 'GLACIER'{};"\
                .format( args.host, filename.strip(), limits )
            print( query )
            response = athena_client.start_query_execution(
                QueryString=query,
                QueryExecutionContext={
                    'Database': args.user
                },
                WorkGroup=args.user
            )
            print( response[ "QueryExecutionId" ] )
except IOError:
    print( "could not read file: {}".format( args.queryfile ) )
