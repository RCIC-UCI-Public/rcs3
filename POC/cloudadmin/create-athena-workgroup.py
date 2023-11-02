#! /usr/bin/python3

import argparse
import boto3
import os
import sys
import yaml

with open( "config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )


usage="Create Athena workgroup for user and host"
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
p.add_argument( "-v", "--verbose", action="store_true",
        help="optional print statements for more detail" )
args = p.parse_args()

if not "schemafile" in aws:
    print( "Missing schema file in configuation settings" )
    sys.exit(1)

# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

# when run from AWS services, profile is not used
if "profile" in aws:
    session = boto3.Session( profile_name=aws[ "profile" ] )
else:
    session = boto3

if "region" in aws:
    athena = session.client( "athena", region_name=aws[ "region" ] )
else:
    athena = session.client( "athena" )
# create the work group, okay if already exists
try:
    response = athena.create_work_group(
        Name=args.user,
        Configuration={
            'ResultConfiguration': {
                'OutputLocation': "{}/{}".format( aws[ "reports" ], args.user )
            },
            'EnforceWorkGroupConfiguration': False,
            'PublishCloudWatchMetricsEnabled': True
        }
    )
except athena.exceptions.InvalidRequestException:
    pass    
