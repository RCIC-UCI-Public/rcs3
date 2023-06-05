#!/usr/bin/env python3
# Generate rclone synchronization command lines based on yaml-formatted jobs files 

import yaml 
import re
import sys
import datetime
import socket 
import os
import io
import argparse
import pdb
import time


def generate(jobs,top_up,endpoint,dryrun=False,threads=2):
    with open( jobs, "r" ) as f:
        jobdefs = yaml.safe_load( f )
    
    for paths in jobdefs['srcpaths']:
        path=paths['path']
        excludes=paths['exclude_global']
        for jobs in paths['jobs']:
           try:
              subdirs=jobs['subdirectories']
           except:
              subdirs=None
           try:
              files=jobs['files']
           except:
              files=None
           write_rclone(endpoint, top_up, jobs['name'],path,subdirs,files,excludes,threads,dryrun)


def write_rclone(endpoint,top_up,jobname,path,subdirs,files,exclude,threads,dryrun):
    rc_global =  "--metadata --links --multi-thread-streams %d" % threads
    if dryrun:
        rc_global += " --dry-run"
    filter_file= "/tmp/%s.filter" % jobname
    log_file = "/tmp/%s.log" % jobname
    write_filter(filter_file,subdirs,files,exclude)
    if top_up is not None:
       sync="copy --max-age %s --no-traverse" %top_up
    else:
       sync="sync"

    logfilter="--log-file %s --filter %s" % (log_file, filter_file)
    cmd="rclone %s --log-level INFO %s %s %s %s:%s/%s" % (sync,rc_global,logfilter,path,endpoint,jobname,path)
    print(cmd)

def write_filter(file,subdirs,files,exclude):
    with open(file,"w") as f:
       if subdirs is not None:
           for d in subdirs:
               f.write("+ %s/**\n" % d)

       if files is not None:
           for fi in files:
               f.write("+ %s\n" % fi)
       
       if exclude is not None:
           for e in exclude:
               f.write("- %s\n" % e)
       f.write("- **\n")
    f.close()

       


        
## *****************************
## main routine
## *****************************

def main(argv):
    # descriptionand help lines for the usage  help
    description = "This file reads a jobs.yaml file to generate rclone commands for syncing data"

    helptopup = "If set, generates a 'top-up' copy command of recently modified files within the specified time period\n"
    helptopup += "Example: --top-up=24h.  Will copy files modified locally within the last 24 hours\n"

    helpjobsfile = "Override the default jobs.yaml file. Example: --jobs=testjobs.yaml\n"

    helpendpoint = "Override the default backup rclone endpoint( s3-backup )\n"

    ## Define command-line parser
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    # optional arguments
    parser.add_argument("-T", "--top-up", dest="top_up", default=None, help=helptopup)
    parser.add_argument("-J", "--jobs", dest="jobsfile", default="jobs.yaml", help=helpjobsfile)
    parser.add_argument("-E", "--endpoint",   dest="endpoint",   default="s3-backup", help=helpendpoint)
    parser.add_argument("-d", "--dry-run",   dest="dryrun",  default=False, action='store_true', help=helpendpoint)

    # Parse the arguments
    args = parser.parse_args()
    
    # Check for existence of args.jobsfile
    if not os.path.isfile(args.jobsfile):
       sys.stderr.write("jobs yaml file %s does not exist\n" % args.jobsfile)
       sys.exit(-1)
    generate(args.jobsfile,args.top_up,args.endpoint,args.dryrun)

if __name__ == "__main__":
    main(sys.argv[1:])
