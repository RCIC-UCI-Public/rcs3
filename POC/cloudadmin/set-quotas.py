#!/usr/bin/env python3 
# Process a quotas CSV file and Set All Quotas in AWS 
import os
import sys
import subprocess
import argparse
import csv

scriptdir=os.path.realpath(os.path.dirname(__file__))
sys.path.append(os.path.join(scriptdir,"..","common"))
import rcs3functions as rcs3

def main(argv):
    scriptdir=os.path.realpath(os.path.dirname(__file__))
    configdir=os.path.normpath(os.path.join(scriptdir, "..","config"))
    aws=rcs3.read_aws_settings()
    
    usage="Read quotas.csv file and then use set-bucket-alarms.py"
    helpowner = "Limit setting quotas to just a single owner (default: all owners)"
    helpquotafile = "Override default quota file (quotas.csv)"

    p = argparse.ArgumentParser( description=usage )
    p.add_argument("-o", "--owner",   dest="owner", default=None, help=helpowner)
    p.add_argument("-f", "--file",   dest="quotafile", default="quotas.csv", help=helpquotafile)
    p.add_argument("-d", "--dry-run",   dest="dryrun",  default=False, action='store_true')
    args = p.parse_args()
    
    if len(os.path.dirname(args.quotafile)) == 0:
        qfile = os.path.join(configdir,args.quotafile)
    else:
        qfile = args.quotafile

   # Read the quotas entry in csv file and execute set-bucket-alarms.py
    sba = os.path.join(scriptdir,"set-bucket-alarms.py")
    
    with rcs3.TextIgnoreCommentsWrapper(qfile) as fw:
        csv_reader = csv.reader(fw,skipinitialspace=True)
        header = next(csv_reader)
        for row in csv_reader: 
            owner,system,oquota,szquota = row
            if args.owner is None or args.owner == owner:
                cmd = [ sba ]
                cmd.extend(row)
                if args.dryrun:
                    print(" ".join(cmd))
                else:
                    subprocess.run(cmd,check=True)

if __name__ == "__main__":
    main(sys.argv[1:])

