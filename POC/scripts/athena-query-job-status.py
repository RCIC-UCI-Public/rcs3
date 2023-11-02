#! /usr/bin/env python3

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
p.add_argument( "-r", "--runonce", action="store_true", default=False,
        help="do not loop, run once and exit" )
p.add_argument( "-s", "--sleepinterval", type=int, default=600,
        help="override the default number of seconds to sleep" )
args = p.parse_args()


listrunning = []
listready = []
listempty = []
listerror = []
listrecheck = []
if args.output:
    results = args.output
else:
    results = "{}/{}-{}-athena-results.txt".format( aws[ "outputdir"], args.user, args.host )
if args.verbose:
    print( "Saving output to: {}".format( results ) )

# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

# when run from AWS services, profile is not used
if "profile" in aws:
    session = boto3.Session( profile_name=aws[ "profile" ] )
else:
    session = boto3

# read in the list of job ids
try:
    with open( args.idsfile ) as fp:
        for rawid in fp:
            listrunning.append( rawid.strip() )
        if args.verbose:
            print( listrunning )
except IOError:
    print( "could not read file: {}".format( args.idsfile ) )
    sys.exit(-1)

if "region" in aws:
    athena_client = session.client( "athena", region_name=aws[ "region" ] )
else:
    athena_client = session.client( "athena" )
while len( listrunning ) > 0:
    for jobid in listrunning:
        if args.verbose:
            print( "JobId: {}".format( jobid ) )
        try:
            response = athena_client.get_query_execution(
                QueryExecutionId=jobid
            )
            jobstate = response[ "QueryExecution" ][ "Status" ][ "State" ]
            if args.verbose:
                print( jobstate )
            if jobstate == "SUCCEEDED":
                listready.append( jobid )
            elif jobstate == "FAILED" or jobstate == "CANCELLED":
                listerror.append( jobid )
            else:
                # in QUEUED or RUNNING state
                listrecheck.append( jobid )
        except athena_client.exceptions.InvalidRequestException:
            listerror.append( jobid )
            print( "Invalid id: {}".format( jobid ) )
        if args.runonce:
            break
        if len( listrecheck ) > 0:
            if args.verbose:
                print( "Sleeping {} seconds".format( args.sleepinterval ) )
            time.sleep( args.sleepinterval )
        listrunning = listrecheck

# Save the S3 locations of the results that have finished
with open( results, "w" ) as f:
    for jobid in listready:
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
                response = athena_client.get_query_execution(
                    QueryExecutionId=jobid
                )
                f.write( response[ "QueryExecution" ][ "ResultConfiguration" ][ "OutputLocation" ] )
                f.write( "\n" )
            else:
                listempty.append( jobid )

# Report empty results, errors, and jobs that are not ready
for i in listempty:
    print( "No results, skipping: {}".format( i ) )
for i in listerror:
    print( "Problem with job id: {}".format( i ) )
for i in listrecheck:
    print( "Jobs not completed: {}".format( i ) )
