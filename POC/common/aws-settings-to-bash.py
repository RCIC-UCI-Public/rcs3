#! /usr/bin/env python3
# Read the aws-settings.yaml file and output bash variables
# 1. Keys are RCS3_<all caps of variable name>
# 2. List elements are comma-separated

# This will read the environment variable RCS3_AWS_SETTINGS, if set
# it will overwrite the default aws-settings.yaml  filename with RCS3_AWS_SETTINGS 

import yaml
import sys
import os
import argparse

def main(argv):
    scriptdir=os.path.realpath(os.path.dirname(__file__))
    configdir=os.path.normpath(os.path.join(scriptdir, "..","config"))

    # if RCS3_AWS_SETTINGS is defined, use it
    try:
       settingsfile=os.environ['RCS3_AWS_SETTINGS']
    except:
       settingsfile="aws-settings.yaml"

    usage="Convert aws-settings file to bash variables"
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,allow_abbrev=True)
    parser.add_argument("-s", "--settings", dest="settings", default=settingsfile, 
       help="Settings file (Default:%s)"%settingsfile)
    args = parser.parse_args()
    
    # Read the global configuration settings
    # If a path separator is in the 
    if os.path.sep in args.settings or os.path.exists(args.settings):
        yamlfile=args.settings
    else:
        yamlfile=os.path.join(configdir,args.settings)

    with open( yamlfile, "r" ) as f:
        aws = yaml.safe_load( f )
     
    for x in aws.keys():
        key="RCS3_%s" % x.upper()
        value = aws[x]
        if type(aws[x]) == list:
           if type(aws[x][0]) == dict:
              value = '"%s"' % str(aws[x])
           else:
              value = ",".join(aws[x])
        
        print("%s=%s" % (key,value))

if __name__ == "__main__":
    main(sys.argv[1:])

