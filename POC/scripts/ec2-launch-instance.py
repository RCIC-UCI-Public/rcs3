#! /usr/bin/python3.9

import argparse
import boto3
import json
import os
import sys
import yaml


def make_tags( u, h ):
    tag_list = []
    tag_list.append( { "Key": "Name", "Value": "{} {} restore".format( u, h ) } )
    tag_list.append( { "Key": "User", "Value": "{}".format( u ) } )
    tag_list.append( { "Key": "Host", "Value": "{}".format( h ) } )
    tag_inst = {}
    tag_inst[ "ResourceType" ] = "instance"
    tag_inst[ "Tags" ] = tag_list
    tag_spec = []
    tag_spec.append( tag_inst )
    return tag_spec


with open( "config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )

usage=""
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
p.add_argument( "-v", "--verbose", action="store_true",
        help="optional print statements for more detail" )
p.add_argument( "-c", "--commandfile",
        help="override default commands run after ec2 start" )
args = p.parse_args()

if args.commandfile:
    cmdf = args.commandfile
elif "commandfile" in aws:
    cmdf = aws[ "commandfile" ]
else:
    cmdf = None
    cmds = ""
if cmdf:
    if args.verbose:
        print( "Reading commands from: {}".format( cmdf ) )
    with open( cmdf, "r" ) as fp:
        cmds = fp.read()


# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

session = boto3.Session( profile_name=aws[ "profile" ] )
ec2 = session.client( "ec2" )

response = ec2.run_instances(
  MaxCount= 1,
  MinCount= 1,
  ImageId= "ami-0507f77897697c4ba",
  InstanceType= "t2.micro",
  InstanceInitiatedShutdownBehavior= "terminate",
  KeyName= "lopez-fedaykin",
  DisableApiTermination= False,
  UserData= cmds,
  NetworkInterfaces= [
    {
      "AssociatePublicIpAddress": True,
      "DeviceIndex": 0,
      "Groups": [
        "sg-05eef13fa9b811cc7"
      ]
    }
  ],
  TagSpecifications= make_tags( args.user, args.host ),
  IamInstanceProfile= {
    "Arn": "arn:aws:iam::{}:instance-profile/read-restore-all-buckets-role".format( aws[ "accountid" ] )
  },
  PrivateDnsNameOptions= {
    "HostnameType": "ip-name",
    "EnableResourceNameDnsARecord": True,
    "EnableResourceNameDnsAAAARecord": False
  }
)
if args.verbose:
    print( response )
ec2_id = response[ "Instances" ][0][ "InstanceId" ]
response = ec2.describe_instances( InstanceIds=[ ec2_id ])
print( response[ "Reservations" ][0][ "Instances" ][0][ "PublicDnsName" ] )