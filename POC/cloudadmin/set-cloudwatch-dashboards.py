#! /usr/bin/env python3
# Read through a set of Dashboard templates, personalize to the parameters, and then add to 
# Cloudwatch.   Structure is done so that 
#  1. Dashboard can be "designed/proofed" in the AWS console 
#  2. JSON for that can be downloaded into the templates directory, 
#  3. Edited to replace specifics from the downloaded with generics (See code for what is replaced)
#  4. From generic templates, personalize and then put into cloudwatch

import argparse
import boto3
import os
import sys
import yaml
import json

scriptdir=os.path.realpath(os.path.dirname(__file__))
sys.path.append(os.path.join(scriptdir,"..","common"))
import rcs3functions as rcs3

def main(argv):
    scriptdir=os.path.realpath(os.path.dirname(__file__))
    configdir=os.path.normpath(os.path.join(scriptdir, "..","config"))
    templatedir=os.path.normpath(os.path.join(scriptdir, "..","templates","dashboards"))

    aws=rcs3.read_aws_settings()
    
    usage="Create dashboards"
    p = argparse.ArgumentParser( description=usage )
    args = p.parse_args()
    
    # override location of .aws/config
    if "configfile" in aws:
        os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]
    
    session = boto3.Session( profile_name=aws[ "profile" ] )
    
    # build the notification list, adding PI if found
    region=aws["region"]
    account=aws["accountid"]
    lens=aws["lens"]

    # read each alarm template in aws["cloudwatch_dashboard_templates"]
    # substitute the following
    rvalues = { 
                "%LENS%" : aws["lens"],
                "%REGION%" : aws["region"],
                "%ACCOUNT%" : aws["accountid"],
                "%BUCKET%" : aws["bucket_postfix"]}

    # Open each template file (which will be invalid json with %XYZ% replacements), read and replace.
    # then load the string as json
    cw_client = session.client( "cloudwatch" )

    for f in aws["cloudwatch_dashboard_templates"]:
        with open(os.path.join(templatedir,f),"r") as tf:
            replaced = [ rcs3.replace_all(x,rvalues) for x in tf.readlines()] 
            output = json.loads("".join(replaced))
            # make call cloudwatch 
            put_dashboard(cw_client,output)

def put_dashboard(cw,DASH):
    print("Putting Dashboard: ",DASH['DashboardName'], "into cloudwatch")
    # Common arguments (ignores anything superfluous in the MA dictionary) 
    dashargs = {
         'DashboardName' : DASH['DashboardName'],
         'DashboardBody' : json.dumps(DASH) } 
    
    
    cw.put_dashboard(**dashargs)


if __name__ == "__main__":
    main(sys.argv[1:])

