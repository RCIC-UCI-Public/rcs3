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
    """ returns a dictionary of
         jobname: (cmd, filter)  """

    alljobs = dict()
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
           try:
              threads=jobs['threads']
           except:
              pass

           jobname = jobs['name']
           (cmd,rcfilter) = write_rclone(endpoint, top_up, jobname, path,subdirs,files,excludes,threads,dryrun)
           alljobs[jobname] = (cmd,rcfilter)

    return alljobs


def write_rclone(endpoint,top_up,jobname,path,subdirs,files,exclude,threads,dryrun):
   
    """ Create the rclone command 
       return (cmd,filter)
              cmd  - list suitable to send to subprocess without resorting to shell=True
              filter - list of lines for the actual filter command """
    rc_global =  ["--metadata", "--links", "--multi-thread-streams", "%d" % threads]
    if dryrun:
        rc_global.extend([" --dry-run"])
    rc_filter = write_filter(subdirs,files,exclude)
    if top_up is not None:
       sync=["copy", "--max-age", "%s" % top_up, "--no-traverse"]
    else:
       sync=["sync"]

    loglevel=["--log-level", "INFO"]
    cmd=["rclone"]
    cmd.extend(sync)
    cmd.extend(loglevel)
    cmd.extend([path])
    cmd.extend(["%s:%s%s" % (endpoint,jobname,path)])
    
    return (cmd,rc_filter)

def write_filter(subdirs,files,exclude):
    """ return list of strings suitable for writing an rclone filter file """
    rval=[]
    if exclude is not None:
        for e in exclude:
            rval.extend(["- %s\n" % e])
    if subdirs is not None:
        for d in subdirs:
            rval.extend(["+ %s/**\n" % d])
    if files is not None:
        for fi in files:
            rval.extend(["+ %s\n" % fi])
    
    return rval 
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
    alljobs = generate(args.jobsfile,args.top_up,args.endpoint,args.dryrun)
    for job in alljobs.keys():
        (cmd1,rcfilter) = alljobs[job]
        # insert logfile and filter-from into command
        cmd=cmd1[:2]
        cmd.extend(["--logfile", "/tmp/%s.log" % job, "--filter-from", "/tmp/%s.filter" % job])
        cmd.extend(cmd1[2:])

        # write the filter file
        with open("/tmp/%s.log" % job, "w") as f:
            f.writelines(rcfilter)
        f.close()
        print(" ".join(cmd))

if __name__ == "__main__":
    main(sys.argv[1:])
