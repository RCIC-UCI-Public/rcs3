#!/usr/bin/env python3 
# Retrieve the manifest for a particular owner/system 
import os
import sys
import argparse
import boto3
import json

scriptdir=os.path.realpath(os.path.dirname(__file__))
sys.path.append(os.path.join(scriptdir,"..","common"))
import rcs3functions as rcs3

def main(argv):
    scriptdir=os.path.realpath(os.path.dirname(__file__))
    configdir=os.path.normpath(os.path.join(scriptdir, "..","config"))
    aws=rcs3.read_aws_settings()
    
    usage="Retrieve the latest manifest for an owner/system pair"
    helpowner = "owner of system"
    helpsystem = "name of system"
    helpoutputdir = "directory to store manifest files (default /tmp/owner-system)"
    helpstdout = "stream output files to stdout"

    p = argparse.ArgumentParser( description=usage )
    p.add_argument("-o", "--owner",   dest="owner", default=None, help=helpowner)
    p.add_argument("-s", "--system",   dest="system", default=None, help=helpsystem)
    p.add_argument("-D", "--directory",   dest="directory", default=None, help=helpoutputdir)
    p.add_argument("-c", "--stdout",   dest="stdout", default=False, help=helpstdout, action='store_true')
    p.add_argument("-p", "--noprofile",   dest="noprofile",  default=False, action='store_true', help="Set to use [default] profile")
    p.add_argument("-d", "--dry-run",   dest="dryrun",  default=False, action='store_true')
    args = p.parse_args()
    
    owner=args.owner
    system=args.system
    if args.directory is None:
        directory = os.path.join("/","tmp","%s-%s" % (owner,system))
    else:
        directory = args.directory

    # Find the latest manifest file 
    if "configfile" in aws:
        os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]
    if args.noprofile:
        session = boto3.Session( profile_name="default")
    else:
        session = boto3.Session( profile_name=aws[ "profile" ])
        

    region=aws["region"]
    manifestbucket="%s-%s-%s" % (owner,system,aws["inventory_postfix"])
    databucket="%s-%s-%s" % (owner,system,aws["bucket_postfix"])
    mpath="%s/%s-%s-daily"%(databucket,owner,system)
    
    # 1. Find the latest manifest
    # It will be lexicographically last in the objects that have manifest.json
    s3_client = session.client( "s3", region_name=aws[ "region" ] )
    
    keys_list = []
    paginator = s3_client.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=manifestbucket, Prefix=mpath) 
    for page in page_iterator:
        # keys = [content['Key'] for content in page.get('Contents')]
        keys = [content['Key'] for content in page.get('Contents') if 'manifest.json' in content['Key']]
        keys_list.extend(keys)

    manifest=keys_list[-1]
   # Retrieve the manifest json file - that lists the objects that contain the actual manifest
    response = s3_client.get_object(Bucket=manifestbucket, Key=manifest)
    contents=response['Body'].read()
    jmanifest = json.loads(contents)
    allfiles = jmanifest['files']

   # if  args.stdout is False, save the files in the defined directory
    if not args.stdout and not os.path.isdir(directory):
        if not os.path.isfile(directory):
            os.mkdir(directory)
        else:
            sys.stderr.write("%s exists but is not a directory" % directory)

    # if writing to stdout create the outputfile (ofile)
    if args.stdout:
        ofile = open(sys.stdout.fileno(), 'wb')

    for file in allfiles:
        key = file['key']
        size = file['size']
        fname = os.path.basename(key)
        chunk_size = 64*1024*1024
        sys.stderr.write(f"\n == retrieving {key} ({size} bytes) ==\n")
        response = s3_client.get_object(Bucket=manifestbucket, Key=key)
        body = response['Body']
        outputfile = os.path.join(directory,fname)
        if not args.stdout:
            ofile = open(outputfile,'wb')
        while True:
            data = body.read(chunk_size)
            if not data:
                  break
            ofile.write(data)
        if not args.stdout:
            ofile.close()

     
if __name__ == "__main__":
    main(sys.argv[1:])

