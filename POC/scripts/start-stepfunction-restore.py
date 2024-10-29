#! /usr/bin/env python3

import argparse
import boto3
import botocore
import os
import sys
import yaml
import tempfile
import urllib.parse
import json

execdir = os.path.dirname(os.path.abspath(__file__))
basedir = os.path.dirname( execdir )
sys.path.append( basedir  + "/common" )


usage="Upload glacier restore list, encoding with urllib"
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
p.add_argument( "purpose",
        help="which step function to start" )
p.add_argument( "glacierlist",
        help="files to restore from Glacier, one-per-line" )
p.add_argument( "-v", "--verbose", action="store_true",
        help="optional print statements for more detail" )
p.add_argument( "-s", "--skipencoding", action="store_true",
        help="skip the urllib parse encoding" )
p.add_argument( "-d", "--daystoretain", type=int,
        help="number of days to retain restored files" )
args = p.parse_args()

with open( basedir + "/config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )

# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

if args.daystoretain:
    expireDays = args.daystoretain
else:
    expireDays = int( aws[ "s3_glacier_expire" ] )

# simple replace of asterisk character with percentage character
# (i.e. UNIX wildcard replaced with SQL wildcard) and
# restore the percentage character if already included as a wildcard
def fix_wildcard_characters( rawstr ):
    rs = rawstr
    for specialstr in [ "%2A", "%25" ]:
        tmpstr = rs.replace( specialstr, "%" )
        rs = tmpstr
    return rs

restoreList = []
with open( args.glacierlist, "r" ) as gf:
    for restorefilename in gf.readlines():
        if args.skipencoding:
            restoreList.append( restorefilename.strip() )
        else:
            tmpstring = urllib.parse.quote( restorefilename.strip() )
            encodedfilename = fix_wildcard_characters( tmpstring )
            restoreList.append( encodedfilename )
if args.verbose:
    print( restoreList )
    print( "expireDays {}".format( expireDays ) )

# when run from AWS services, profile is not used
if "profile" in aws:
    session = boto3.Session( profile_name=aws[ "profile" ] )
else:
    session = boto3

if "region" in aws:
    sfn = session.client( "stepfunctions", region_name=aws[ "region" ] )
else:
    sfn = session.client( "stepfunctions" )

sfnArn = "arn:aws:states:{}:{}:stateMachine:{}-{}-sfn-{}"\
    .format( aws[ "region" ], aws[ "accountid" ], args.user, args.host, args.purpose )
sfnInput = json.dumps( { "RestoreList": restoreList, "ExpireDays": expireDays } )
if args.verbose:
    print( "Calling ARN: {}".format( sfnArn ) )
    print( "Using input: {}".format( sfnInput ) )

sys.exit(0)

try:
    response = sfn.start_execution(
        stateMachineArn=sfnArn,
        input=sfnInput,
    )
    if args.verbose:
        print(response)
except Exception as error:
    print( type(error).__name__ )
    print( error )
    sys.exit( -1 )
