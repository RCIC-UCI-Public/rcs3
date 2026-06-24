#! /usr/bin/env python3

import argparse
import boto3
import os
import sys
import yaml

scriptdir=os.path.realpath(os.path.dirname(__file__))
sys.path.append(os.path.join(scriptdir,"..","common"))
import rcs3functions as rcs3

configdir=os.path.normpath(os.path.join(scriptdir, "..","config"))
templatedir=os.path.normpath(os.path.join(scriptdir, "..","templates","alarms-bucket"))

aws=rcs3.read_aws_settings()


usage="""Delete CloudWatch all alarms related to a specific user and host."""
p = argparse.ArgumentParser( description=usage )
p.add_argument( "owner",
        help="user ID of owner" )
p.add_argument( "host",
        help="hostname" )
p.add_argument( "-v", "--verbose", action="store_true",
        help="optional print statements for more detail" )
args = p.parse_args()


# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

# when run from AWS services, profile is not used
if "profile" in aws:
    session = boto3.Session( profile_name=aws[ "profile" ] )
else:
    session = boto3

service="cloudwatch"
if "region" in aws:
    cw_client = session.client( service, region_name=aws[ "region" ] )
else:
    cw_client = session.client( service )


alarm_prefix=f"{args.owner}-{args.host}"
if args.verbose:
    print( f"Searching for alarms: {alarm_prefix}" )
try:
    response = cw_client.describe_alarms(
        AlarmNamePrefix=alarm_prefix
    )
except:
    print( f"Error retrieving alarms: {alarm_prefix}" )

def delete_alarms( alarms ):
    """Helper function which calls boto3 delete_alarms()"""
    if args.verbose:
        print( f"Deleting: {alarms}" )
    try:
        cw_client.delete_alarms(
            AlarmNames = alarms
        )
    except:
        print( f"Error deleting: {alarms}" )

# composite alarms can only be deleted one at a time
alarm_name=""
test0 = alarm_prefix + r" "
test1 = alarm_prefix + r"-"
for composite_alarm in response[ "CompositeAlarms" ]:
    alarm_name = composite_alarm[ "AlarmName" ]
    if alarm_name.startswith( test0 ) or alarm_name.startswith( test1 ):
        delete_alarms( [ alarm_name ] )

# metric alarms can be deleted 100 at a time
name_count = 0
alarm_list = []
print( f"{test0} {test1}" )
for metric_alarm in response[ "MetricAlarms" ]:
    alarm_name = metric_alarm[ "AlarmName" ]
    if alarm_name.startswith( test0 ) or alarm_name.startswith( test1 ):
        alarm_list.append( alarm_name )
        name_count += 1
    if name_count == 100:
        delete_alarms( alarm_list )
        name_count = 0
        alarm_list = []
if name_count > 0:
    delete_alarms( alarm_list )
