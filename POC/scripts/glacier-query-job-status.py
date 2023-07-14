#! /usr/bin/python3

import argparse
import boto3
import os
import sys
import yaml

with open( "config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )


usage="Query the S3 Batch job ids and send notification"
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
p.add_argument( "idsfile",
        help="file containing job ids, one per line" )
p.add_argument( "-v", "--verbose", action="store_true",
        help="optional print statements for more detail" )
p.add_argument( "-n", "--notify",
        help="override the default SNS topic" )
args = p.parse_args()


listready = []
listfail = []
listerror = []
listother = []
if args.notify:
    results = args.notify
else:
    results = "arn:aws:sns:us-west-2:{}:{}-{}-uci-notify".format( aws[ "accountid" ], args.user, args.host)
if args.verbose:
    print( "Sending notification to: {}".format( results ) )

# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

session = boto3.Session( profile_name=aws[ "profile" ] )

try:
    with open( args.idsfile ) as fp:
        s3c_client = session.client( "s3control" )
        for rawid in fp:
            jobid = rawid.strip()
            if args.verbose:
                print( jobid )
            try:
                response = s3c_client.describe_job(
                    AccountId=aws[ "accountid" ],
                    JobId=jobid
                )
                jobstate = response[ "Job" ][ "Status" ]
                if args.verbose:
                    print( jobstate )
                if jobstate == "Complete":
                    listready.append( jobid )
                elif jobstate == "Failed":
                	listfail.append( jobid )
                else:
                    listother.append( jobid )
            except athena_client.exceptions.InvalidRequestException:
                listerror.append( jobid )
                print( "Invalid id: {}".format( jobid ) )
except IOError:
    print( "could not read file: {}".format( args.idsfile ) )

# Report completions, failures, errors, and jobs that are not ready
sns_message = ""
send = True
for i in listready:
    print( "Completed: {}".format( i ) )
    sns_message += "Completed: {}\n".format( i )
for i in listfail:
    print( "Job failed: {}".format( i ) )
    sns_message += "Job failed: {}\n".format( i )
for i in listerror:
    print( "Not a valid job id: {}".format( i ) )
for i in listother:
    send = False
    print( "Jobs not completed: {}".format( i ) )

if send:
    sns_client = session.client( "sns" )
    try:
        response = sns_client.publish(
            TopicArn=results,
            Message=sns_message,
            Subject="{} {} restore ready".format( args.user, args.host )
        )
    except sns_client.exception.NotFound:
        print( "No notification sent: {}".format( results ) )

