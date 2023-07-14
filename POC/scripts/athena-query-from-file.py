#! /usr/bin/python3

import argparse
import boto3
import os
import sys
import yaml

with open( "config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )


usage="Execute an Athena query for each line in the query file associated with user and host"
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
p.add_argument( "queryfile",
        help="file containing strings to query" )
p.add_argument( "-v", "--verbose", action="store_true",
        help="optional print statements for more detail" )
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

# when run from AWS services, profile is not used
if "profile" in aws:
    session = boto3.Session( profile_name=aws[ "profile" ] )
else:
    session = boto3

try:
    with open( args.queryfile ) as fp:
        athena = session.client( "athena" )
        bucket = "{}-{}-uci-bkup-bucket".format( args.user, args.host )
        for filename in fp:
            query = "select bucketname as \"{}\", filename, version_id from {} where filename like '{}' and storage_class like 'GLACIER'{};"\
                .format( bucket, args.host, filename.strip(), limits )
            if args.verbose:
                print( query )
            response = athena.start_query_execution(
                QueryString=query,
                QueryExecutionContext={
                    'Database': args.user
                },
                WorkGroup=args.user
            )
            print( response[ "QueryExecutionId" ] )
except IOError:
    print( "could not read file: {}".format( args.queryfile ) )
