#! /usr/bin/python3

import argparse
import boto3
import json
import os
import sys
import yaml

sys.path.append( "scripts" )
from commonfunctions import delete_user_keys, create_user_key


usage="Replace IAM user access keys"
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
args = p.parse_args()

#print( args.user, args.host )
with open( "config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )

# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

acctname = args.user +  "-" + args.host + "-sa"
keyfile = aws[ "outputdir" ] + args.user + "-" + args.host + ".credentials"
session = boto3.Session( profile_name=aws[ "profile" ] )

# remove user keys, create new key, save to file
iam_client = session.client( "iam" )
try:
    delete_user_keys( iam_client, acctname )
    userkey = create_user_key( iam_client, acctname )
    with open( keyfile, "w" ) as savefile:
        json.dump( userkey, savefile, indent=4 )
except iam_client.exceptions.NoSuchEntityException:
    print( "Service account does not exist:", acctname )
