#!/usr/bin/env python3
# Generate rclone synchronization command lines based on yaml-formatted jobs files 
# Author: Philip Papadopoulos (ppapadop@uci.edu)
# (C) UC Regents 2023 - 2024
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
import boto3
import platform
scriptdir=os.path.realpath(os.path.dirname(__file__))
sys.path.append(scriptdir)
from credentials import Updater

class runBackup(object):
   
    def run_backup(job):
        sync = "sync" if "sync" in job.cmd else "top-up"
        msg = "=== %s %s started at %s" % (job.name,sync,datetime.datetime.now())
        print(msg)
        sys.stdout.flush()
        if job.notify and job.system is not None:
            notify_sns(job.owner, job.system, "RCS3: Backup Job Start from %s" % job.system, msg)
        # Write the filter file for the job
        with open(job.filterfile,"w") as f:
            f.writelines(job.filters)
        process = subprocess.Popen(job.cmd)
        process.wait()
        return job

    def __init__(self,alljobs,parallel=2,lockfile="/var/lock/gen-backup.lock"):
        self._lockfile = lockfile 
        self._alljobs = alljobs
        self._parallel = parallel

    def run_jobs(self):
        try:
              lckfile = os.open(self._lockfile, os.O_CREAT | os.O_EXCL)
        except:
              print ("could not create lockfile %s in exclusive mode. Another backup running?" % self._lockfile)
              exit(-1)
               
        with Pool(self._parallel) as pool:
            finaljob = None
            try:
                for finished in pool.imap_unordered(runBackup.run_backup, self._alljobs):
                    msg = "=== %s completed at %s" % (finished.name,datetime.datetime.now())
                    print(msg)
                    sys.stdout.flush()
                    if finished.notify and finished.system is not None:
                        notify_sns(finished.owner, finished.system, "RCS3: Backup Job End from %s" % finished.system, msg)
                    finaljob = finished

                # All Jobs done. Rotate the access key
                if finaljob is not None:
                    print ("rotating access key for " ,finaljob.owner,finaljob.system)     
                    newCreds=Updater(finaljob.owner,finaljob.system)
                    newCreds.rotate()
                print("All tasks completed.")
                
                
            except:
                pass
            os.close(lckfile)
            os.unlink(self._lockfile)

class backupJob(object):
    def __init__(self,name,path,owner=None,system=None):
        self._name = str(name)
        self._destprefix = str(name)
        self._path = path
        self._destpath = self._path
        self._excludes = list()
        self._includedirs = list()
        self._includefiles = list()
        self._filters = list()
        self._logfile = "/tmp/%s.log" % name
        self._filterfile = "/tmp/%s.filter" % name
        self._threads = 2
        self._checkers = 32
        self._timestamp = None
        self._cmd = list()
        self._extra = list()
        self._rclonecmd = "rclone"
        self._owner = owner
        self._system = system
        self._notify = False 

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
    def destprefix(self):
        return self._destprefix
        
    @destprefix.setter
    def destprefix(self,value):
        self._destprefix = value 

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
    def checkers(self):
        return self._checkers

    @checkers.setter
    def checkers(self,value):
        self._checkers = value 

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self,value):
        """Set timestamp if of correct format"""
        r = re.compile('\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[A-Z]')
        if r.match(value) is not None:
            self._timestamp = value 
        else:
            sys.stderr.write("invalid timestamp format (%s). Exiting\n" % value)
            sys.exit(-1)

  
    @property
    def rclonecmd(self):
        return self._rclonecmd

    @rclonecmd.setter
    def rclonecmd(self,value):
        """Set Rclone cmd to override ENV """
        self._rclonecmd = value 

    @property
    def extra(self):
        return self._extra

    @extra.setter
    def extra(self,value):
        """Set Rclone extra arguments"""
        self._extra = re.split('\s+',value)

    @property
    def notify(self):
        return self._notify

    @notify.setter
    def notify(self,value):
        """Set Notify T/F"""
        self._notify = value 

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self,value):
        self._owner = value

    @property
    def system(self):
        return self._system

    @system.setter
    def system(self,value):
        self._system = value

    @property
    def cmd(self):
        return self._cmd
        
    def __str__(self):
        return " ".join(self._cmd) 

    ##### Methods ######
    def construct_cmd(self,endpoint,loglevel="INFO",top_up=None,dryrun=False,threads=None,checkers=None,baseonly=False):
        """ construct the rclone command for this backupJob"""
        if threads is not None:
           tcount = threads
        else:
           tcount = self._threads
        if checkers is not None:
           chkcount = checkers
        else:
           chkcount = self._checkers

        rc_global =  ["--stats-one-line-date", "--metadata", "--links", "--transfers", "%d" % tcount, "--checkers" , "%d" % chkcount]
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
        self._cmd = [ self._rclonecmd ]
        self._cmd.extend(confcred)
        self._cmd.extend(rc_global)
        if not baseonly:
            self._cmd.extend(logarg)
            self._cmd.extend(filefilter)
            self._cmd.extend(self._syncdirection(sync,endpoint))

    def _syncdirection(self,sync,endpoint):
        """ Default is backup from host to remote """
        # sync is of type [] in backup
        rval = [x for x in sync]
        rval.extend(self.extra)
        rval.extend([self._path,"%s:%s%s" % (endpoint,self._destprefix,self._destpath)])
        return rval

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

    def generate(self,jobsfile):
        """ returns a list of backupJobs (or recoveryJob) objects """ 
    
        alljobs = [] 
        jobscriptdir=os.path.realpath(os.path.dirname(jobsfile))
    
        with open( jobsfile, "r" ) as f:
            jobdefs = yaml.safe_load( f )
        
        for paths in jobdefs['srcpaths']:
            # Can read path or archivepath. Archivepath is a syntactic-sugar for recover jobs
            try:
                path=paths['path']
            except:
                path = None
            try:
                archivepath=paths['archivepath']
                path = archivepath
            except:
                pass

            try:
                excludes=paths['exclude_global']
            except:
                excludes=list()
    
            # Read common excludes from a file (must be in the same subdir as the jobs file)
            # exclude_file=os.path.normpath(os.path.join(jobscriptdir, paths['exclude_file']))
            try:
                exclude_file=os.path.normpath(os.path.join(jobscriptdir, paths['exclude_file']))
                with open( exclude_file,'r') as ef:
                    excludes_in_file = yaml.safe_load(ef)
                    excludes.extend(excludes_in_file)
            except KeyError as e:
                pass 
                      
            for jobs in paths['jobs']:
               # Creates either a backupjob or a recover job
               # python-fu to create a new object that is the same class as this one
               bupJob = object.__new__(type(self))
               bupJob.__init__(jobs['name'],path)
               alljobs.extend([bupJob])
    
               try:
                  bupJob._destpath = jobs['destpath']
               except:
                  bupJob._destpath = path 
    
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
                  bupJob.checkers=jobs['checkers']
               except:
                  pass
               try:
                  bupJob.destprefix=jobs['prefix']
               except:
                  pass
               try:
                  bupJob._mode=jobs['mode']
               except:
                  pass 
               try:
                  bupJob.excludes=excludes
                  bupJob.excludes=excludes+jobs['exclude']
               except:
                  pass
    
        return alljobs 

class recoveryJob(backupJob):
    """ Similar to a backupUp job but order is reversed """
    def __init__(self,name,archivepath,owner=None,system=None):
       super().__init__(name, archivepath,owner,system)
       self._archivepath=archivepath
       self._mode = "copy"

    def _syncdirection(self,sync,endpoint):
        """ Restore from remote to remote """
        rval = [x for x in self.extra]
        # If timestamp is set, use it 
        if self.timestamp is not None:
            rval.extend(["--s3-version-at",self.timestamp])
        # sync is based on mode in job (defaults to copy) 
        rval.extend([self._mode,"%s:%s" % (endpoint,self._archivepath),self._destpath])
        return rval

## Post to the SNS topic

def notify_sns(owner,system, subject, msg):

    if owner is None or system is None:
        return

    scriptdir=os.path.realpath(os.path.dirname(__file__))
    sys.path.append(os.path.join(scriptdir,"..","common"))
    import rcs3functions as rcs3

    configdir=os.path.normpath(os.path.join(scriptdir, "..","config"))
    aws=rcs3.read_aws_settings()
    #try:
    #    x = os.environ['AWS_SHARED_CREDENTIALS_FILE']
    #except:
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = os.path.join(configdir,'credentials')

    try:
        session = boto3.Session() 
        sns_client = session.client( "sns" , region_name=aws[ "region" ] )
    except:
        return # Fail silently

    # find the right SNS topic

    topic="{}-{}-{}".format( owner, system, aws['owner_notify'] )

    try:
        mytopics = list(filter(lambda x: x['TopicArn'].endswith(topic), sns_client.list_topics()['Topics']))
        # Select the first topic that matches
        myArn = mytopics[0]['TopicArn']
        response = sns_client.publish( TopicArn=myArn, Message=msg, Subject=subject)
    except Exception as m:
        print( "Could not use SNS notify. Error: {}".format(str(m)) )
        
        
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
    helptimestamp = "Restore based upon state at particular time. Format: 2023-09-24T12:00:00Z (Year-Month-Day(T)hour:minute:second(Zone). Use Z for Zulu (GMT) time. Default: None (most recent)"

    helpjob = "comma-separated list of job names to run, list, etc. \n"
    helpsyncjob = "comma separated list of sync jobs to run. Cannot set both jobs and syncjobs"
    helptopupjob = "comma separated list of top-up jobs to run. Cannot set both jobs and topupjobs"
    helpextra = "extra rclone arguments. Quote arguments. Example: '--metadata-exclude tier=GLACIER'. Default: None"
    ## Define command-line parser
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter,allow_abbrev=True)
    # optional arguments
    parser.add_argument("-T", "--top-up", dest="top_up", default=None, help=helptopup)
    parser.add_argument("-Y", "--yaml", dest="jobsfile", default=jobdefault, help=helpjobsfile)
    parser.add_argument("-E", "--endpoint",   dest="endpoint",   default="s3-backup", help=helpendpoint)
    parser.add_argument("-d", "--dry-run",   dest="dryrun",  default=False, action='store_true')
    parser.add_argument("-t", "--threads",   dest="threads",  default=None,help="Override #threads")
    parser.add_argument("-j", "--jobs",   dest="joblist",  default=None,help=helpjob)
    parser.add_argument("-x", "--extra",   dest="xrclone",  default=None,help=helpextra)
    parser.add_argument("-R", "--recover",   dest="recover",  default=False, action='store_true',help="Recover instead of backup")
    parser.add_argument("-S", "--timestamp", dest="timestamp",  default=None,help=helptimestamp)
    parser.add_argument("--sync-jobs",   dest="syncjobs",  default=None,help=helpsyncjob)
    parser.add_argument("--topup-jobs",   dest="topupjobs",  default=None,help=helptopupjob)
    parser.add_argument("-p", "--parallel",   dest="parallel",  default=2,help="how many backup jobs to run in parallel (2)")
    parser.add_argument("-K", "--checkers",  dest="checkers", default=32,help="how many checkers to run in parallel (32)")
    parser.add_argument("--rclonecmd",  dest="rclonecmd", default=None, help="Full path to rclone executable")
    parser.add_argument("--skipnotify",  dest="skipnotify", default=False, action='store_true', help="Do not notify when sync jobs have completed")
    parser.add_argument("--owner",  dest="owner", default=None, help="Owner of system. Must be specified if notifications sent")
    sysname = platform.node()
    parser.add_argument("--system",  dest="system", default=sysname, help="Override default name (%s) of system" % sysname)
    parser.add_argument("--lockfile",  dest="lockfile", default="/var/lock/gen-backup.lock",help="Alternate location for lockfile (default: /var/lock/gen-backup.lock)")

    parser.add_argument('command', metavar='command',choices=['list','run','detail','rclone'], nargs=1,
              help='list | detail | run | rclone ')

    # Parse the arguments
    args = parser.parse_args()
    command = args.command[0]    

    # Check for existence of args.jobsfile
    if not os.path.isfile(args.jobsfile):
       sys.stderr.write("jobs yaml file %s does not exist\n" % args.jobsfile)
       sys.exit(-1)

    # validate the if syncjoblist is non-empty or topupjoblist is non-empty that joblist is non-empty

    if (args.syncjobs is not None or args.topupjobs is not None) and args.joblist is not None:
       sys.stderr.write("cannot simultaneously specify --jobs and sync/topup jobs\n")
       sys.exit(-1)

    # Build the jobs
    # Are we recovering or backing up?
    yamlbackup = None
    if not args.recover:
       # Always backup up the job file (usually ../config/jobs.yaml)
       yamlbackup = backupJob('rcs3config',os.path.dirname(args.jobsfile),args.owner,args.system)
       yamlbackup.includefiles = [os.path.basename(args.jobsfile)]
       alljobs = [yamlbackup] 
       mode = yamlbackup
    else:
       alljobs = []
       mode = recoveryJob('notused','notused')
       
    alljobs.extend(mode.generate(args.jobsfile))
    if args.timestamp is not None:
       for job in alljobs:
           job.timestamp = args.timestamp

    if args.rclonecmd is not None:
       for job in alljobs:
           job.rclonecmd = args.rclonecmd

    if args.xrclone is not None:
       for job in alljobs:
           job.extra = args.xrclone

    # Filter the jobs based on optional jobslist argument
    syncjobs = []
    topupjobs = []
    if args.syncjobs != None:
        syncjobnames = args.syncjobs.split(",")
        syncjobs = list(filter( lambda x: True if x.name in syncjobnames else False, alljobs))

    if args.topupjobs != None:
        topupjobnames = args.topupjobs.split(",")
        topupjobs = list(filter( lambda x: True if x.name in topupjobnames else False, alljobs))

    # Always sync the jobs.yaml if in backup mode 
    if yamlbackup is not None:
        syncjobs.extend([yamlbackup])

    # Handle non-empty jobslist or a combination of sync/topupjobs 
    if args.joblist != None:
        jobnames = args.joblist.split(",")
        filteredjobs = filter( lambda x: True if x.name in jobnames else False, alljobs)
        alljobs=list(filteredjobs) 
    elif args.syncjobs != None or args.topupjobs != None:
        alljobs = [ x for x in syncjobs ]
        alljobs.extend(topupjobs)

    for job in alljobs:
        if args.threads is not None:
            job.threads = int(args.threads)
        if args.checkers is not None:
            job.checkers = int(args.checkers)
        if job in syncjobs:
           job.construct_cmd(args.endpoint,dryrun=args.dryrun)
        else:
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
    elif command == 'rclone':
        """ print the base rclone command with globals filled in """
        yamlbackup.construct_cmd(args.endpoint, baseonly=True)
        os.sys.stdout.write(str(yamlbackup))

    elif command == 'run':
        for job in alljobs:
           job.owner = args.owner
           job.system = args.system
           if 'sync' in job.cmd:
               if job != yamlbackup and args.skipnotify is False:
                   job.notify = True

        runner = runBackup(alljobs,parallel=int(args.parallel),lockfile=args.lockfile)
        runner.run_jobs()

if __name__ == "__main__":
    main(sys.argv[1:])
