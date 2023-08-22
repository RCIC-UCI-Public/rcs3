#! /usr/bin/env python3
# Read the aws-settings.yaml file and output bash variables
# 1. Keys are RCS3_<all caps of variable name>
# 2. List elements are comma-separated

import yaml
import sys
import os
import argparse

def main(argv):
    scriptdir=os.path.realpath(os.path.dirname(__file__))
    configdir=os.path.normpath(os.path.join(scriptdir, "..","config"))

    usage="Convert aws-settings file to bash variables"
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,allow_abbrev=True)
    parser.add_argument("-s", "--settings", dest="settings", default="aws-settings.yaml", help="Settings file")
    args = parser.parse_args()
    
    # Read the global configuration settings
    with open( os.path.join(configdir,args.settings), "r" ) as f:
        aws = yaml.safe_load( f )
     
    for x in aws.keys():
        key="RCS3_%s" % x.upper()
        value = aws[x]
        if type(aws[x]) == list:
        	value = ",".join(aws[x])
        
        print("%s=%s" % (key,value))

if __name__ == "__main__":
    main(sys.argv[1:])

