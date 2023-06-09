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
import subprocess
from multiprocessing import Pool

class runBackup(object):
   
    def run_backup(job):
        print("=== %s started at %s" % (job.name,datetime.datetime.now()))
        # Write the filter file for the job
        with open(job.filterfile,"w") as f:
            f.writelines(job.filters)
        process = subprocess.Popen(job.cmd)
        process.wait()
        return job.name

    def __init__(self,alljobs,parallel=2):
        self._lockfile = "/var/lock/gen-backup.lock"
        self._alljobs = alljobs
        self._parallel = parallel

    def run_jobs(self):
        try:
              lckfile = os.open(self._lockfile, os.O_CREAT | os.O_EXCL)
        except:
              print ("could not create lockfile %s in exclusive mode. Another backup running?" % self._lockfile)
              exit(-1)
               
        with Pool(self._parallel) as pool:
            try:
                for finished in pool.imap_unordered(runBackup.run_backup, self._alljobs):
                    print("=== %s completed at %s" % (finished,datetime.datetime.now()))
                print("All tasks completed.")
            except:
                pass
            os.close(lckfile)
            os.unlink(self._lockfile)

class backupJob(object):
    def __init__(self,name,path):
        self._name = str(name)
        self._path = path
        self._excludes = list()
        self._includedirs = list()
        self._includefiles = list()
        self._filters = list()
        self._logfile = "/tmp/%s.log" % name
        self._filterfile = "/tmp/%s.filter" % name
        self._threads = 2
        self._cmd = list()

    ## Standard Setters and Getters for various components of a backup job object
    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path

    @property
    def filters(self):
        return self._filters

    @property
    def logfile(self):
        return self._logfile
        
    @logfile.setter
    def logfile(self,value):
        self._logfile = value 

    @property
    def filterfile(self):
        return self._filterfile

    @filterfile.setter
    def filterfile(self,value):
        self._filterfile = value 

    @property
    def excludes(self):
        return self._excludes

    @excludes.setter
    def excludes(self,value):
        self._excludes = value 

    @property
    def includedirs(self):
        return self._includedirs

    @includedirs.setter
    def includedirs(self,value):
        self._includedirs = value 

    @property
    def includefiles(self):
        return self._includefiles

    @includefiles.setter
    def includefiles(self,value):
        self._includefiles = value 

    @property
    def threads(self):
        return self._threads

    @threads.setter
    def threads(self,value):
        self._threads = value 

    @property
    def cmd(self):
        return self._cmd
        
    def __str__(self):
        return " ".join(self._cmd) 

    ##### Methods ######
    def construct_cmd(self,endpoint,loglevel="INFO",top_up=None,dryrun=False,threads=None):
        """ construct the rclone command for this backupJob"""
        if threads is not None:
           tcount = threads
        else:
           tcount = self._threads
        rc_global =  ["--metadata", "--links", "--transfers", "%d" % tcount]
        if dryrun:
            rc_global.extend(["--dry-run"])
        self._build_filters()
        if top_up is not None:
           sync=["copy", "--max-age", "%s" % top_up, "--no-traverse"]
        else:
           sync=["sync"]
        logarg=["--log-level", loglevel]
        filefilter = ["--log-file", self._logfile, "--filter-from", self._filterfile]
        
        # config files
        # get realpath to this script
        scriptdir=os.path.realpath(os.path.dirname(__file__))
        configdir=os.path.normpath(os.path.join(scriptdir, "..","config"))
        rclone_config=os.path.join(configdir,"rclone.conf")
        credentials=os.path.join(configdir,"credentials")
        confcred = ["--config", rclone_config, "--s3-shared-credentials-file",credentials]
 
        # build the command in pieces
        self._cmd=["rclone"]
        self._cmd.extend(sync)
        self._cmd.extend(confcred)
        self._cmd.extend(logarg)
        self._cmd.extend(filefilter)
        self._cmd.extend(rc_global)
        self._cmd.extend([self._path])
        self._cmd.extend(["%s:%s%s" % (endpoint,self._name,self._path)])

    def _build_filters(self):
        self._filters=list()
        for e in self._excludes:
            self._filters.extend(["- %s\n" % e])
        for d in self._includedirs:
            self._filters.extend(["+ %s/**\n" % d])
        for fi in self._includefiles:
            self._filters.extend(["+ %s\n" % fi])
        # catchall to exclude anything else not explicitly included or excluded above
        self._filters.extend(["- **\n"])

def generate(jobsfile):
    """ returns a list of backupJobs objects """ 

    alljobs = [] 
    with open( jobsfile, "r" ) as f:
        jobdefs = yaml.safe_load( f )
    
    for paths in jobdefs['srcpaths']:
        path=paths['path']
        try:
            excludes=paths['exclude_global']
        except:
            excludes=list()
        for jobs in paths['jobs']:
           bupJob = backupJob(jobs['name'],path)
           alljobs.extend([bupJob])

           try:
              bupJob.includedirs = jobs['subdirectories']
           except:
              pass
           try:
              bupJob.includefiles=jobs['files']
           except:
              pass
           try:
              bupJob.threads=jobs['threads']
           except:
              pass
           try:
              bupJob.excludes=excludes
              bupJob.excludes=excludes+jobs['exclude']
           except:
              pass

    return alljobs 


## *****************************
## main routine
## *****************************

def main(argv):

    scriptdir=os.path.realpath(os.path.dirname(__file__))
    configdir=os.path.normpath(os.path.join(scriptdir, "..","config"))
    jobdefault=os.path.join(configdir,"jobs.yaml")

    # descriptionand help lines for the usage  help
    description = "This file reads a jobs.yaml file to generate rclone commands for syncing data"

    helptopup = "If set, generates a 'top-up' copy command of recently modified files within the specified time period\n"
    helptopup += "Example: --top-up=24h.  Will copy files modified locally within the last 24 hours\n"

    helpjobsfile = "Override the default jobs file (%s). Example: --yaml=testjobs.yaml\n" % jobdefault

    helpendpoint = "Override the default backup rclone endpoint( s3-backup )\n"

    helpjob = "comma-separated list of job names to run, list, etc. \n"
    ## Define command-line parser
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter,allow_abbrev=True)
    # optional arguments
    parser.add_argument("-T", "--top-up", dest="top_up", default=None, help=helptopup)
    parser.add_argument("-Y", "--yaml", dest="jobsfile", default=jobdefault, help=helpjobsfile)
    parser.add_argument("-E", "--endpoint",   dest="endpoint",   default="s3-backup", help=helpendpoint)
    parser.add_argument("-d", "--dry-run",   dest="dryrun",  default=False, action='store_true')
    parser.add_argument("-t", "--threads",   dest="threads",  default=None,help="Override #threads")
    parser.add_argument("-j", "--jobs",   dest="joblist",  default=None,help=helpjob)
    parser.add_argument("-p", "--parallel",   dest="parallel",  default=2,help="how many backup jobs to run in parallel (2)")
    parser.add_argument('command', metavar='command',choices=['list','run','detail'], nargs=1,
              help='list | detail | run  ')

    # Parse the arguments
    args = parser.parse_args()
    command = args.command[0]    

    # Check for existence of args.jobsfile
    if not os.path.isfile(args.jobsfile):
       sys.stderr.write("jobs yaml file %s does not exist\n" % args.jobsfile)
       sys.exit(-1)
    # Build the jobs
    alljobs = generate(args.jobsfile)
    # Filter the jobs based on optional jobslist argument
    if args.joblist != None:
        jobnames = args.joblist.split(",")
        filteredjobs = filter( lambda x: True if x.name in jobnames else False, alljobs)
        alljobs=list(filteredjobs) 

    for job in alljobs:
        if args.threads is not None:
            job.threads = int(args.threads)
        job.construct_cmd(args.endpoint,dryrun=args.dryrun,top_up=args.top_up) 

    if command == 'list' or command == 'detail':
        for job in alljobs:
            print (job.name,job.path)
            if command == 'detail':
                print("== filter contents (output to: %s) ==" % job.filterfile)
                sys.stdout.writelines(job.filters)
                print("== command ==")
                print(job)
                print("=============")
    elif command == 'run':
        runner = runBackup(alljobs,parallel=int(args.parallel))
        runner.run_jobs()

if __name__ == "__main__":
    main(sys.argv[1:])
