#! /usr/bin/env python3
# Read through a set of Alarm Template, personalize to the parameters, and then add to 
# Cloudwatch.   Structure is done so that 
#  1. alarm can be "designed/proofed" in the AWS console for a specific bucket,
#  2. JSON for that can be downloaded into the templates directory, 
#  3. Edited to replace specifics from the downloaded with generics (See code for what is replaced)
#  4. From generic templates, personalize and then put into cloudwatch

import argparse
import boto3
import os
import sys
import yaml
import json

scriptdir=os.path.realpath(os.path.dirname(__file__))
sys.path.append(os.path.join(scriptdir,"..","common"))
import rcs3functions as rcs3

def main(argv):
    scriptdir=os.path.realpath(os.path.dirname(__file__))
    configdir=os.path.normpath(os.path.join(scriptdir, "..","config"))
    templatedir=os.path.normpath(os.path.join(scriptdir, "..","templates","alarms-bucket"))

    aws=rcs3.read_aws_settings()
    
    usage="Create alarms for a specific system with number of objects quotaa and others"
    p = argparse.ArgumentParser( description=usage )
    p.add_argument( "owner",
            help="owner UCInetID" )
    p.add_argument( "host",
            help="hostname" )
    p.add_argument( "objectlimit", type=int,
            help="number objects limit in M" )
    p.add_argument( "quotalimit", type=int,
            help="Quota limit in TB" )
    args = p.parse_args()
    
    # override location of .aws/config
    if "configfile" in aws:
        os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]
    
    session = boto3.Session( profile_name=aws[ "profile" ] )
    
    # build the notification list, adding PI if found
    region=aws["region"]
    account=aws["accountid"]
    notify_list = [ '"arn:aws:sns:%s:%s:%s"' % (region,account,aws["admin_notify"])] 
    pi_topic = "arn:aws:sns:%s:%s:%s-%s-%s" % (region,account,args.owner,args.host,aws["owner_notify"])
    sns_client = session.client( "sns", region_name=aws[ "region" ] )
    try:
        sns_client.get_topic_attributes( TopicArn=pi_topic )
        notify_list.append( '"%s"' % pi_topic )
    except sns_client.exceptions.NotFoundException:
        print( "no SNS topic found for PI, notifications to cloudadmin Team only")
    notify=",".join(notify_list)
    
    # read each alarm template in aws["bucket_alarm_templates"]
    # substitute the following
    rvalues = { "%OWNER%": args.owner, 
                "%SYSTEM%": args.host,
                "%OBJECTQUOTA%": str(args.objectlimit * 1000000),
                "%SIZEQUOTA%": str(args.quotalimit * 1024*1024*1024*1024),
                "%LENS%" : aws["lens"],
                "%REGION%" : aws["region"],
                "%ACCOUNT%" : aws["accountid"],
                "%BUCKET%" : aws["bucket_postfix"],
                "%NOTIFY%" : notify }
    # Open each template file (which will be invalid json with %XYZ% replacements), read and replace.
    # then load the string as json
    cw_client = session.client( "cloudwatch", region_name=aws[ "region" ] )

    for f in aws["bucket_alarm_templates"]:
        with open(os.path.join(templatedir,f),"r") as tf:
            replaced = [ rcs3.replace_all(x,rvalues,comment='//') for x in tf.readlines()] 
            output = json.loads("".join(replaced))
            # make call cloudwatch 
            for MA in output['MetricAlarms']:
                put_alarm(cw_client,MA) 

def put_alarm(cw,MA):
    print("Putting Alarm: ",MA['AlarmName'], "into cloudwatch")
    # Common arguments (ignores anything superfluous in the MA dictionary) 
    MAargs = {
         'AlarmName' : MA['AlarmName'],
         'AlarmDescription' : MA['AlarmDescription'],
         'ActionsEnabled' : MA['ActionsEnabled'],
         'OKActions' : MA['OKActions'],
         'AlarmActions' : MA['AlarmActions'],
         'EvaluationPeriods' : MA['EvaluationPeriods'],
         'DatapointsToAlarm' : MA['DatapointsToAlarm'],
         'Threshold' : MA['Threshold'],
         'ComparisonOperator' : MA['ComparisonOperator'],
         'TreatMissingData' : MA['TreatMissingData']}
    
    # Two cases: 1) Alarm is a single Metric, 2) Alarm uses multiple metrics
    try:
         MAargs['MetricName'] = MA['MetricName']
         MAargs['Dimensions'] = MA['Dimensions']
         MAargs['Namespace'] = MA['Namespace']
         MAargs['Statistic'] = MA['Statistic']
         MAargs['Period'] = MA['Period']
    except:
         MAargs['Metrics'] = MA['Metrics']

    cw.put_metric_alarm(**MAargs)


if __name__ == "__main__":
    main(sys.argv[1:])

