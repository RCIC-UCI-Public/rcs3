#! /usr/bin/python3.9

import argparse
import boto3
import os
import sys
import yaml

with open( "config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )


usage="Query the Athena job ids and write location of S3 results"
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
p.add_argument( "idsfile",
        help="file containing job ids, one per line" )
p.add_argument( "-v", "--verbose", action="store_true",
        help="optional print statements for more detail" )
p.add_argument( "-o", "--output",
        help="override output file" )
args = p.parse_args()


listready = []
listempty = []
listerror = []
listother = []
if args.output:
    results = args.output
else:
    results = "{}/{}-{}-athena-results.txt".format( aws[ "outputdir"], args.user, args.host )
if args.verbose:
    print( "Saving output to: {}".format( results ) )

# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

session = boto3.Session( profile_name=aws[ "profile" ] )

try:
    with open( args.idsfile ) as fp:
        athena_client = session.client( "athena" )
        for rawid in fp:
            jobid = rawid.strip()
            if args.verbose:
                print( jobid )
            try:
                response = athena_client.get_query_runtime_statistics(
                    QueryExecutionId=jobid
                )
                joboutput = response[ "QueryRuntimeStatistics" ][ "OutputStage" ]
                jobstate = joboutput[ "State" ]
                jobsize = joboutput[ "OutputBytes" ]
                if args.verbose:
                    print( jobstate, jobsize )
                if jobstate == "FINISHED":
                    if jobsize > 0:
                        listready.append( jobid )
                    else:
                        listempty.append( jobid )
                else:
                    listother.append( jobid )
            except athena_client.exceptions.InvalidRequestException:
                listerror.append( jobid )
                print( "Invalid id: {}".format( jobid ) )
except IOError:
    print( "could not read file: {}".format( args.idsfile ) )

# Save the S3 locations of the results that have finished
with open( results, "w" ) as f:
    for jobid in listready:
        response = athena_client.get_query_execution(
            QueryExecutionId=jobid
        )
    f.write( response[ "QueryExecution" ][ "ResultConfiguration" ][ "OutputLocation" ] )
    f.write( "\n" )

# Report empty results, errors, and jobs that are not ready
for i in listempty:
    print( "No results, skipping: {}".format( i ) )
for i in listerror:
    print( "Not a valid job id: {}".format( i ) )
for i in listother:
    print( "Jobs not completed: {}".format( i ) )