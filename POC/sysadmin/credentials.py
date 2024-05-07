#! /usr/bin/python3
""" Create credentials  from a template file. Write to standard Output when called as program. 
Otherwise create Credentials Object """

import argparse
import os
import sys
import yaml
import boto3
import tempfile
import stat
scriptdir=os.path.realpath(os.path.dirname(__file__))
sys.path.append(os.path.join(scriptdir,"..","common"))
import rcs3functions as rcs3

class Credentials(object):

    def __init__(self,access_key=None,secret_access_key=None):
        if access_key is None:
            self._access_key = input("Enter AWS Access Key: ")
        else:
            self._access_key=access_key
        if secret_access_key is None:
            self._secret_access_key = input("Enter AWS Secret Access Key: ")
        else:
            self._secret_access_key=secret_access_key
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

class Updater(Credentials):


    def __init__(self,owner,system,credfile=None):
        if owner is None or system is None:
           raise Exception("owner or system is None when attempting to update credentials") 

        scriptdir=os.path.realpath(os.path.dirname(__file__))
        self._configdir=os.path.normpath(os.path.join(scriptdir, "..","config"))
        self._credfile = credfile
        if credfile is None:
            self._credfile = os.path.join(self._configdir,'credentials')
        os.environ['AWS_SHARED_CREDENTIALS_FILE'] = self._credfile 

        self.SA = "{}-{}-sa".format(owner,system)
    
        try:
            aws=rcs3.read_aws_settings()
            self.session = boto3.Session(profile_name='default') 
            self.iam_client = self.session.client( "iam" , region_name=aws[ "region" ] )
        except:
            self.iam_client = None
            print( "Could not create iam client for {}. Error: {}".format(self.SA,str(m)) )
            return

        # Generate a new set of access keys for the service account
        try:
            response = self.iam_client.create_access_key(UserName=self.SA)
            access_key_id = response['AccessKey']['AccessKeyId']
            secret_access_key_id = response['AccessKey']['SecretAccessKey']
        except Exception as m:
            print( "Could not create new access key for {}. Error: {}".format(self.SA,str(m)) )
        super().__init__(access_key=access_key_id, secret_access_key=secret_access_key_id)
     
    def rotate(self):
        ## Create a temporary file for the new credentials.
        try:
            (fd,tmpPath) = tempfile.mkstemp(dir=self._configdir, text=True)
            with open(tmpPath,'w') as fh:
                fh.write(str(self))
            os.close(fd)
            os.chmod(tmpPath, stat.S_IREAD | stat.S_IWRITE)
        except Exception as m:
            print( "Could not create new credentials file for {}. Error: {}".format(self.SA,str(m)) )
            return

        # Move the temporary file to the old credfile name (on windows have to delete old file first)
        try:
            os.rename(self._credfile,tmpPath+"rcs3")
            os.rename(tmpPath,self._credfile)
            os.remove(tmpPath+"rcs3")
        except Exception as m:
            print( "Could not rename credentials file ({}) for {}. Error: {}".format(tmpPath,self.SA,str(m)) )
            return
    
        # List access keys for user, delete any that do not match the new access key
        try:
            response = self.iam_client.list_access_keys(UserName=self.SA)
            for key in response['AccessKeyMetadata']:
                if key['AccessKeyId'] != self._access_key:
                     dresponse = self.iam_client.delete_access_key(UserName=self.SA,AccessKeyId=key['AccessKeyId'])
        except Exception as m:
            print( " Error deleting unused access keys for {}. Error: {}".format(self.SA,str(m)) )
            return

def main():
    usage="AWS credentials file from template."
    if len(sys.argv) == 3:
        newCreds = Updater(sys.argv[1],sys.argv[2])
        newCreds.rotate()
    else:
        creds = Credentials()
        print(creds)

if __name__ == "__main__":
   main()
        
