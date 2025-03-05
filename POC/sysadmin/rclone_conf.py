#! /usr/bin/python3
""" Create rclone.conf from a template file. Write to standard Output when called as program. Otherwise create RcloneConf Object """

import argparse
import os
import sys
import yaml
scriptdir=os.path.realpath(os.path.dirname(__file__))
sys.path.append(os.path.join(scriptdir,"..","common"))
import rcs3functions as rcs3

class RcloneConf(object):

    def __init__(self,owner,host):
        self._owner = owner
        self._host = host
        self._configdir=os.path.normpath(os.path.join(scriptdir, "..","config"))
        self._templatedir=os.path.normpath(os.path.join(scriptdir, "..","templates"))
        self.customize()

    def __str__(self):
        return "".join(self._config)

    def customize(self):
        aws=rcs3.read_aws_settings()
        rvalues = { "xxxuserxxx": self._owner,
                "xxxhostxxx": self._host,
                "xxxregionxxx" : aws["region"],
                "xxxbucketxxx" : aws["bucket_postfix"],
                "xxxinventoryxxx" : aws["inventory_postfix"] }

        with open(os.path.join(self._templatedir,"rclone.conf")) as f:
            self._config = [ rcs3.replace_all(x,rvalues) for x in f.readlines()]

def main():
    usage="Create rclone.conf from template."
    p = argparse.ArgumentParser( description=usage )
    p.add_argument( "owner", help="ID of owner (e.g., UCInetID)" )
    p.add_argument( "host", help="hostname" )
    args = p.parse_args()
    conf = RcloneConf(args.owner,args.host)
    print(conf)

if __name__ == "__main__":
   main()

