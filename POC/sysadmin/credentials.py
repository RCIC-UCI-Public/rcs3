#! /usr/bin/python3
""" Create credentials  from a template file. Write to standard Output when called as program. 
Otherwise create Credentials Object """

import argparse
import os
import sys
import yaml
scriptdir=os.path.realpath(os.path.dirname(__file__))
sys.path.append(os.path.join(scriptdir,"..","common"))
import rcs3functions as rcs3

class Credentials(object):

    def __init__(self):
        self._access_key = input("Enter AWS Access Key: ")
        self._secret_access_key = input("Enter AWS Secret Access Key: ")
        self._configdir=os.path.normpath(os.path.join(scriptdir, "..","config"))
        self._templatedir=os.path.normpath(os.path.join(scriptdir, "..","templates"))
        self.customize()

    def __str__(self):
        return "".join(self._config)

    def customize(self):
        rvalues = { "xxxaccess_keyxxx": self._access_key,
                "xxxsecret_keyxxx": self._secret_access_key}
        with open(os.path.join(self._templatedir,"credentials.in")) as f:
            self._config = [ rcs3.replace_all(x,rvalues) for x in f.readlines()]

def main():
    usage="AWS credentials file from template."
    creds = Credentials()
    print(creds)

if __name__ == "__main__":
   main()
        
