#! /usr/bin/env python3

import argparse
import boto3
import json
import os
import sys
import yaml

with open( "config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )

usage="Create an S3 gateway in a VPC both to lower cost of EC2 connections to S3 and to provide a security chokepoint which can be used in policy statements to control access."
p = argparse.ArgumentParser( description=usage )
p.add_argument( "vpcid",
        help="vpc id in which to create S3 gateway" )
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

ec2 = session.client( "ec2" )

# retrieve the route table id, needed for creating the S2 gateway
response = ec2.describe_route_tables(
    Filters=[
        {
            "Name": "vpc-id",
            "Values": [ args.vpcid ]
        }
    ]
)
rt_id = response[ "RouteTables" ][0][ "RouteTableId" ]
if args.verbose:
    print( rt_id )

# create the S3 gateway within the VPC
response = ec2.create_vpc_endpoint(
    VpcId = args.vpcid,
    ServiceName = "com.amazonaws.{}.s3".format( aws[ "region" ] ),
    TagSpecifications = [
        {
            "ResourceType": "vpc-endpoint",
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "s3-endpoint-vpc-{}".format( args.vpcid )
                }
            ]
        }
    ]
)
if args.verbose:
    print( response )
