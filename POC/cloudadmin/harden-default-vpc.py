#! /usr/bin/env python3

import argparse
import boto3
import json
import os
import sys
import yaml

with open( "config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )

usage="Tighten the security group rules on the unmodified, default VPC.  Should only be run once per AWS account.  Running on a modified VPC will have unpredictable results."
p = argparse.ArgumentParser( description=usage )
p.add_argument( "securitygroup",
        help="name of the security group, should be \"default\"" )
p.add_argument( "-v", "--verbose", action="store_true",
        help="optional print statements for more detail" )
p.add_argument( "-f", "--force", action="store_true",
        help="live dangerously, ignore warnings and proceed" )
args = p.parse_args()

# Sanity check before proceeding
if args.securitygroup != "default":
    if not args.force:
        print( "Use \"default\" or --force option" )
        sys.exit( -1 )

# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

# when run from AWS services, profile is not used
if "profile" in aws:
    session = boto3.Session( profile_name=aws[ "profile" ] )
else:
    session = boto3

ec2 = session.client( "ec2" )

# retrieve the security group id of the default VPC
response = ec2.describe_security_groups( GroupNames=[ args.securitygroup ] )
g_id = response[ "SecurityGroups" ][0][ "GroupId" ]
if args.verbose:
    print( g_id )

# retrieve the security group rule id of the default ingress rule
response = ec2.describe_security_group_rules( Filters=[{ "Name": "group-id", "Values": [g_id] }] )
count_ingress_rules = 0
for sgr in response[ "SecurityGroupRules" ]:
    if not sgr[ "IsEgress" ]:
        sgr_id = sgr[ "SecurityGroupRuleId" ]
        if args.verbose:
            print( sgr_id )
        count_ingress_rules += 1

# Sanity check that we've found the default ingress rule and no other ingress rules
if count_ingress_rules == 0:
    print( "No ingress rules found in {}".format( args.securitygroup ) )
    sys.exit( -1 )
elif count_ingress_rules > 1:
    if not args.force:
        print( "More than one ingress rules found in {}".format( args.securitygroup ) )
        sys.exit( -1 )

print( "Modify {}".format( args.securitygroup ) )

# Change the default ingress rule which allows all inbound traffic
response = ec2.modify_security_group_rules(
    GroupId=g_id,
    SecurityGroupRules=[
        {
            'SecurityGroupRuleId': sgr_id,
            'SecurityGroupRule': {
                'IpProtocol': "tcp",
                'FromPort': 22,
                'ToPort': 22,
                'CidrIpv4': "128.200.0.0/16",
            }
        },
    ]
    #, DryRun=True
)
if args.verbose:
    print( response )

# Add additional allowed networks
for cidr in [ "128.195.0.0/16", "192.5.19.0/24" ]:
    response = ec2.authorize_security_group_ingress(
        CidrIp=cidr, FromPort=22, GroupId=g_id, IpProtocol="tcp", ToPort=22
    )
    if args.verbose:
        print( response )
