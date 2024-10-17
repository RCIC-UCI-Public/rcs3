#! /usr/bin/env python3

import argparse
import boto3
import botocore
import os
import sys
import yaml
import json

scriptdir=os.path.realpath(os.path.dirname(__file__))
sys.path.append(os.path.join(scriptdir,"..","common"))
import rcs3functions as rcs3

SCHEDNAME="keyAgeMetric-cron"

def createSchedule(sched_client,region,account):
   """ Create the scheduler instance in aws """
   sched_client.create_schedule(
       Description = "Cron-like job to populate the IAM users key age metric",
       FlexibleTimeWindow = {
           "MaximumWindowInMinutes": 5,
           "Mode": "FLEXIBLE"
       },
       GroupName =  "default",
       Name =  SCHEDNAME,
       ScheduleExpression = "rate(1 hours)",
       ScheduleExpressionTimezone = "America/Los_Angeles",
       State = "ENABLED",
       Target = {
           'Arn' : f"arn:aws:lambda:{region}:{account}:function:keyAgeMetric",
           'RetryPolicy' : {
               "MaximumEventAgeInSeconds": 86400,
               "MaximumRetryAttempts": 185
           },
           'RoleArn' : f"arn:aws:iam::{account}:role/keyAgeMetric-scheduler-invoke-role"
       }
   )

def deleteSchedule(sched_client):
   """ delete the scheduler instance in aws """
   sched_client.delete_schedule(Name = SCHEDNAME)

def main(argv):
    scriptdir=os.path.realpath(os.path.dirname(__file__))
    configdir=os.path.normpath(os.path.join(scriptdir, "..","config"))
    templatedir=os.path.normpath(os.path.join(scriptdir, "..","templates","dashboards"))

    aws=rcs3.read_aws_settings()
    
    usage="Create keyAgeMetric-cron"
    p = argparse.ArgumentParser( description=usage )
    args = p.parse_args()
    
    # override location of .aws/config
    if "configfile" in aws:
        os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]
    
    session = boto3.Session( profile_name=aws[ "profile" ] )
    
    # build the notification list, adding PI if found
    region=aws["region"]
    account=aws["accountid"]

# Create an scheduler client
    sched_client = session.client( "scheduler", region_name=aws[ "region" ] )

# Create the keyAgeMetric schedule
    try:
        createSchedule(sched_client,region,account)        
    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] == 'ConflictException':
            deleteSchedule(sched_client)
            createSchedule(sched_client,region,account)        
        else:
            print(error)
         
if __name__ == "__main__":
    main(sys.argv[1:])

