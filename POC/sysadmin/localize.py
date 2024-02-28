#!/usr/bin/env python3
""" Localize the rclone and credentials for the particular system """

import argparse
import os
import sys
import stat
sys.path.append(os.path.realpath(os.path.dirname(__file__)))
from rclone_conf import RcloneConf
from credentials import Credentials

def main():
    usage="Create localize rclone-conf and aws credentials. Does NOT overwrite existing files"
    p = argparse.ArgumentParser( description=usage )
    p.add_argument( "owner", help="ID of onwer (e.g., UCInetID)" )
    p.add_argument( "host", help="hostname" )
    args = p.parse_args()
    scriptdir=os.path.realpath(os.path.dirname(__file__))
    configdir=os.path.normpath(os.path.join(scriptdir, "..","config"))

    conffile=os.path.join(configdir,"rclone.conf")
    credfile=os.path.join(configdir,"credentials")

    if not os.path.exists(conffile):
        conf = RcloneConf(args.owner, args.host)
        with open(conffile,"w") as f:
           f.write(str(conf))
           os.chmod(conffile, stat.S_IREAD | stat.S_IWRITE)
           sys.stderr.write("Wrote Rclone configuration: %s\n" % conffile)

    if not os.path.exists(credfile):
        creds = Credentials()
        with open(credfile,"w") as f:
           f.write(str(creds))
           os.chmod(credfile, stat.S_IREAD | stat.S_IWRITE)
           sys.stderr.write("Wrote AWS Credentials file: %s\n" % credfile)

if __name__ == "__main__":
   main()
        
