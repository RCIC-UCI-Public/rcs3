#! /usr/bin/python3

import argparse
import boto3
import os
import sys
import time
import yaml

with open( "config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )


usage="Query the S3 Batch job ids until completion and send notification"
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
p.add_argument( "idsfile",
        help="file containing job ids, one per line" )
p.add_argument( "-v", "--verbose", action="store_true",
        help="optional print statements for more detail" )
p.add_argument( "-r", "--runonce", action="store_true", default=False,
        help="do not loop, run once and exit" )
p.add_argument( "-n", "--notify",
        help="override the default SNS topic" )
p.add_argument( "-s", "--sleepinterval", type=int, default=3600
        help="override the default number of seconds to sleep" )
args = p.parse_args()


listrunning = []
listready = []
listfail = []
listerror = []
if args.notify:
    results = args.notify
else:
    results = "arn:aws:sns:us-west-2:{}:{}-{}-uci-notify".format( aws[ "accountid" ], args.user, args.host)
if args.verbose:
    print( "Sending notification to: {}".format( results ) )

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

s3c = session.client( "s3control" )
while len( listrunning ) > 0:
    for jobid in listrunning:
        try:
            response = s3c.describe_job(
                AccountId=aws[ "accountid" ],
                JobId=jobid
            )
            jobstate = response[ "Job" ][ "Status" ]
            if args.verbose:
                print( "Checking: {}".format( jobstate ) )
            if jobstate == "Complete":
                listready.append( jobid )
                listrunning.remove( jobid )
            elif jobstate == "Failed":
                listfail.append( jobid )
                listrunning.remove( jobid )
            else:
                pass
        except s3c.exceptions.InvalidRequestException:
                listerror.append( jobid )
                listrunning.remove( jobid )
                print( "Invalid id: {}".format( jobid ) )
    if runonce:
        break
    time.sleep( args.sleepinterval )

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
for i in listrunning:
    send = False
    print( "Jobs not completed: {}".format( i ) )

if send:
    sns = session.client( "sns" )
    try:
        response = sns.publish(
            TopicArn=results,
            Message=sns_message,
            Subject="{} {} restore ready".format( args.user, args.host )
        )
    except sns.exception.NotFound:
        print( "No notification sent: {}".format( results ) )

