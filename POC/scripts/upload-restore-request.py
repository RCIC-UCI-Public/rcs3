#! /usr/bin/env python3

import argparse
import boto3
import botocore
import os
import sys
import yaml
import tempfile
import urllib.parse
from datetime import date


execdir = os.path.dirname(os.path.abspath(__file__))
basedir = os.path.dirname( execdir )
sys.path.append( basedir  + "/common" )


usage="Upload glacier restore list, encoding with urllib"
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
p.add_argument( "glacierlist",
        help="files to restore from Glacier, one-per-line" )
p.add_argument( "-v", "--verbose", action="store_true",
        help="optional print statements for more detail" )
p.add_argument( "-s", "--skipencoding", action="store_true",
        help="skip the urllib parse encoding" )
args = p.parse_args()

with open( basedir + "/config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )

# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]


# simple replace of asterisk character with percentage character
# (i.e. UNIX wildcard replaced with SQL wildcard) and
# restore the percentage character if already included as a wildcard
def fix_wildcard_characters( rawstr ):
    rs = rawstr
    for specialstr in [ "%2A", "%25" ]:
        tmpstr = rs.replace( specialstr, "%" )
        rs = tmpstr
    return rs

if args.skipencoding:
    uploadfile = args.glacierlist
else:
    with open( args.glacierlist, "r" ) as gf:
        tmpprefix = args.user + "-" + args.host + "-"
        savedir = basedir + "/" + aws[ "outputdir" ]
        ( wd, uploadfile ) = tempfile.mkstemp( prefix=tmpprefix, dir=savedir, text=True )
        print( "Creating temporary file: {}".format( uploadfile ) )
        with open( wd, "w" ) as wf:
            for restorefilename in gf.readlines():
                tmpstring = urllib.parse.quote( restorefilename.strip() )
                encodedfilename = fix_wildcard_characters( tmpstring )
                if args.verbose:
                    print( "{}".format(encodedfilename) )
                wf.write( "{}\n".format(encodedfilename) )

# when run from AWS services, profile is not used
if "profile" in aws:
    session = boto3.Session( profile_name=aws[ "profile" ] )
else:
    session = boto3

if "region" in aws:
    s3 = session.client( "s3", region_name=aws[ "region" ] )
else:
    s3 = session.client( "s3" )

# remove s3:// prefix from reports bucket
rbucket = aws[ "reports" ].replace( "s3://", "" )
try:
    response = s3.put_object(
        Body=uploadfile,
        Bucket=rbucket,
        Key= args.user + "/" + args.host + "-restore-" + date.today().isoformat()
    )
    if args.verbose:
        print(response)
except Exception as error:
    print( type(error).__name__ )
    print( error )
    sys.exit( -1 )
