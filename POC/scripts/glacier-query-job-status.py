#! /usr/bin/python3

import argparse
import boto3
import os
import sys
import time
import yaml

with open( "config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )


usage="Query the S3 Batch job ids until completion and send notification."
# S3 Batch bulk retrieval should complete in 12 hours; exit if not completed in 12 hours.
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
p.add_argument( "-s", "--sleepinterval", type=int, default=3600,
        help="override the default number of seconds to sleep" )
p.add_argument( "-t", "--timeoutinterval", type=int, default=12,
        help="number of checks until exiting, uses sleepinterval" )
args = p.parse_args()


listrunning = []
listready = []
listfail = []
listerror = []
listrecheck = []
sleepcount = 0
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

if "region" in aws:
    s3c = session.client( "s3control", region_name=aws[ "region" ] )
else:
    s3c = session.client( "s3control" )
while len( listrunning ) > 0:
    for jobid in listrunning:
        if args.verbose:
            print( "JobId: {}".format( jobid ) )
        try:
            response = s3c.describe_job(
                AccountId=aws[ "accountid" ],
                JobId=jobid
            )
            jobstate = response[ "Job" ][ "Status" ]
            if args.verbose:
                print( "State: {}".format( jobstate ) )
            if jobstate == "Complete":
                listready.append( jobid )
            elif jobstate == "Failed":
                listfail.append( jobid )
            elif jobstate == "Cancelled":
                listfail.append( jobid )
            else:
                listrecheck.append( jobid )
        except s3c.exceptions.InvalidRequestException:
            listerror.append( jobid )
            print( "Invalid id: {}".format( jobid ) )
    if args.runonce:
        listrunning = listrecheck
        break
    if len( listrecheck ) > 0:
        if sleepcount >= args.timeoutinterval:
            break
        if args.verbose:
            print( "Sleeping {} seconds".format( args.sleepinterval ) )
        time.sleep( args.sleepinterval )
        sleepcount += 1
    listrunning = listrecheck
    listrecheck = []

# Report completions, failures, errors, and jobs that are not ready
sns_message = ""
send = True
if sleepcount >= args.timeoutinterval:
    sns_message += "Monitoring exceeds timeout interval; job no longer being monitored.\n\n"
for i in listready:
    sns_message += "Completed: {}\n".format( i )
for i in listfail:
    sns_message += "Job failed: {}\n".format( i )
for i in listerror:
    sns_message += "Invalid job id: {}\n".format( i )
for i in listrunning:
    sns_message += "Job not completed: {}\n".format( i )
if args.verbose:
    print( sns_message )

if send:
    if "region" in aws:
        sns = session.client( "sns", region_name=aws[ "region" ] )
    else:
        sns = session.client( "sns" )
    try:
        response = sns.publish(
            TopicArn=results,
            Message=sns_message,
            Subject="{} {} restore ready".format( args.user, args.host )
        )
    except sns.exception.NotFound:
        print( "No notification sent: {}".format( results ) )

