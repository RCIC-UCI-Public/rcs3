#! /usr/bin/env python3

import argparse
import boto3
import json
import os
import sys
import yaml

execdir = os.path.dirname(os.path.abspath(__file__))
basedir = os.path.dirname( execdir )
sys.path.append( basedir  + "/common" )

from rcs3functions import delete_user_keys, create_user_key


usage="Replace IAM user access keys"
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
args = p.parse_args()

with open( basedir + "/config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )

# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

acctname = args.user +  "-" + args.host + "-sa"
keyfile = aws[ "outputdir" ] + args.user + "-" + args.host + ".credentials"

# when run from AWS services, profile is not used
if "profile" in aws:
    session = boto3.Session( profile_name=aws[ "profile" ] )
else:
    session = boto3

if "region" in aws:
    iam_client = session.client( "iam", region_name=aws[ "region" ] )
else:
    iam_client = session.client( "iam" )

# remove user keys, create new key, save to file
try:
    delete_user_keys( iam_client, acctname )
    userkey = create_user_key( iam_client, acctname )
    with open( keyfile, "w" ) as savefile:
        json.dump( userkey, savefile, indent=4 )
except iam_client.exceptions.NoSuchEntityException:
    print( "Service account does not exist:", acctname )
