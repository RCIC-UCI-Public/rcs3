#! /usr/bin/env python3

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


with open( config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )

usage="Allow the user to launch an EC2 instance for self-service restores from S3 Glacier"
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
p.add_argument( "-v", "--verbose", action="store_true",
        help="optional print statements for more detail" )
args = p.parse_args()

if "commandfile" in aws:
    cmdf = aws[ "commandfile" ]
    if args.verbose:
        print( "Reading commands from: {}".format( cmdf ) )
    with open( cmdf, "r" ) as fp:
        cmds = fp.read()
else:
    cmds = ""


# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

if "profile" in aws:
    session = boto3.Session( profile_name=aws[ "profile" ] )
else:
    session = boto3

ec2 = session.client( "ec2" )

response = ec2.run_instances(
  MaxCount= 1,
  MinCount= 1,
  ImageId= aws[ "ami" ],
  InstanceType= aws[ "instancetype" ],
  InstanceInitiatedShutdownBehavior= "terminate",
  KeyName= aws[ "keypair" ],
  DisableApiTermination= False,
  UserData= cmds,
  NetworkInterfaces= [
    {
      "AssociatePublicIpAddress": True,
      "DeviceIndex": 0
    }
  ],
  TagSpecifications= make_tags( args.user, args.host ),
  IamInstanceProfile= {
    "Arn": "arn:aws:iam::{}:instance-profile/{}-{}-restore"\
        .format( aws[ "accountid" ], args.user, args.host )
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
print( "Instance id: {}".format( ec2_id ) )
