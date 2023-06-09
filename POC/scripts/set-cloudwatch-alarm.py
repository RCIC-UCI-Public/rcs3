#! /usr/bin/python3

import argparse
import boto3
import os
import sys
import yaml

with open( "config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )


usage="Add a notification when the total storage of a specific S3 bucket exceeds the given size threshold"
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
p.add_argument( "limit", type=int,
        help="Size limit in TB" )
p.add_argument( "-d", "--disable", action="store_true",
        help="disable the action notification, e.g. while testing" )
args = p.parse_args()

# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

session = boto3.Session( profile_name=aws[ "profile" ] )

# build the notification list, adding PI if found
notify_list = [ "arn:aws:sns:us-west-2:{}:rcic-team-notify".format( aws[ "accountid" ] ) ]
pi_topic = "arn:aws:sns:us-west-2:{}:{}-{}-uci-notify".format( aws[ "accountid" ], args.user, args.host )
sns_client = session.client( "sns" )
try:
    sns_client.get_topic_attributes( TopicArn=pi_topic )
    notify_list.append( pi_topic )
except sns_client.exceptions.NotFoundException:
    print( "no SNS topic found for PI, notifications to RCIC Team only")

def define_metrics( bucketname ):
    m=[]
    expression = {
        "Id": "e1",
        "Label": "{} Total Storage".format( bucketname ),
        "ReturnData": True,
        "Expression": "SUM(METRICS())"
    }
    m.append( expression )
    n = 0
    for stype in [ "StandardStorage", "GlacierStorage" ]:
         n += 1
         metric = {
            "Id": "m{}".format( n ),
            "ReturnData": False,
            "MetricStat": {
                "Metric": {
                    "Namespace": "AWS/S3",
                    "MetricName": "BucketSizeBytes",
                    "Dimensions": [
                        {
                            "Name": "StorageType",
                            "Value": stype
                        },
                        {
                            "Name": "BucketName",
                            "Value": bucketname
                        }
                    ]
                },
                "Period": 86400,
                "Stat": "Sum"
            }
         }
         m.append( metric )
    return m


bucket = args.user + "-" + args.host + "-uci-bkup-bucket"
cw_client = session.client( "cloudwatch" )
cw_client.put_metric_alarm(
    AlarmName="{}-{} exceeded size".format( args.user, args.host ),
    AlarmDescription="The {} has exceeded {} TB of storage in Standard and Glacier".format( bucket, args.limit ),
    ActionsEnabled=False if args.disable else True,
    AlarmActions=notify_list,
    EvaluationPeriods=1,
    DatapointsToAlarm=1,
    Threshold=args.limit * 1000000000000,
    ComparisonOperator="GreaterThanThreshold",
    TreatMissingData="missing",
    Metrics=define_metrics( bucket )
)
