#! /usr/bin/env python3

import argparse
import boto3
import os
import sys
import yaml
from datetime import datetime,timedelta
from dateutil.tz import *

scriptdir=os.path.realpath(os.path.dirname(__file__))
sys.path.append(os.path.join(scriptdir,"..","common"))
import rcs3functions as rcs3

configdir=os.path.normpath(os.path.join(scriptdir, "..","config"))

aws=rcs3.read_aws_settings()



def lambda_handler(event, context):
    session = boto3.Session( profile_name=aws[ "profile" ] )
    cw_client = session.client( "cloudwatch", region_name=aws['region'] )
    iam_client = session.client( "iam", region_name=aws['region'] )
    
    # Get the list of users
    try:
        users = iam_client.list_users() 
    except Exception as m:
        print( "Invalid call  {}".format( m ) )
           
    # Filter the users whose name only ends with '-sa' (Service Account)
    allusers = filter(lambda y: y.endswith('-sa'),[ x['UserName'] for x in users['Users'] ] )
    today=datetime.now(tzlocal())

    for u in allusers:
        response = iam_client.list_access_keys( UserName=u)
        keys=[ (x['AccessKeyId'],x['CreateDate'],x['Status']) for x in response['AccessKeyMetadata'] ]
        for (key,created,status) in keys:
            delta = today - created
            print (f"{u} ({key},{delta}) : ", end='')
            if status == 'Active' and (today - created) > timedelta(days=2):
                print ('ALARM')
            else:
                print ('OK')

if __name__ == "__main__":
    usage="""Get list of accounts, find access keys, find creation time of access key"""
    p = argparse.ArgumentParser( description=usage )
    args = p.parse_args()

    lambda_handler(None,None)    
