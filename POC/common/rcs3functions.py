#!/usr/bin/env python3
# Commonly-used functions in RCS3 python programs
import os
import sys
import yaml
import json
import io
import re
import boto3


class boto3Clients():
    def __init__(self):
       self._aws = read_aws_settings()
       # when run from AWS services, profile is not used
       if "profile" in self._aws:
           self._session = boto3.Session( profile_name=self._aws[ "profile" ] )
       else:
           self._session = boto3

       # create clients. Doesn't matter if they are used. 
       # compresses code
       self._b3clients= ["athena","cloudtrail","events","iam","lambda","logs","s3","sns","sqs","stepfunctions"]
       self._clients={}
       for c in self._b3clients:
           if "region" in self._aws:
                self._clients[c] = self._session.client( c, region_name=self._aws[ "region" ] )
           else:
                self._clients[c] = self._session.client(c)

           
           # Add the attribute to the object so caller can access boto3 clients as
           # obj.Lambda, obj.Athena, obj.S3 , obj.SFN
           if c == "stepfunctions":
               attrkey="SFN"
           elif len(c) == 3:
               attrkey = c.upper()
           else:
               attrkey= c.title() 
           setattr(self,attrkey,self._clients[c])

class TextIgnoreCommentsWrapper(io.TextIOWrapper):
    """ Wrap a file to filter out lines STARTING with '#' when reading, skip 'empty' lines if skipblank is true"""
    def __init__(self, filename, mode='r', encoding='utf-8',skipblank=True):
        file = open(filename, mode + 'b')  # Open in binary mode
        self.skip=skipblank
        super().__init__(file, encoding=encoding)

    def __iter__(self):
        return self

    def __next__(self):
        line = super().readline()
        while line and ( (re.match('\s*#',line) is not None) or (self.skip and re.match('\s',line) is not None)):
            line = super().readline()
        if not line:
            raise StopIteration
        return line

def read_aws_settings(settings=None,configdir=None):
    """return a dictionary of aws-settings"""
    scriptdir=os.path.realpath(os.path.dirname(__file__))
    if configdir is None:
       configdir=os.path.normpath(os.path.join(scriptdir, "..","config"))

    # if caller doesn't explicitly override, look at environment var, or take default
    if settings is None:
       # if RCS3_AWS_SETTINGS is defined, use it
       try:
          settings=os.environ['RCS3_AWS_SETTINGS']
       except:
          settings="aws-settings.yaml"

    # construct full path 
    yamlfile=os.path.join(configdir,settings)
    if os.path.sep in settings or os.path.exists(settings):
        yamlfile=settings

    # Read the global configuration settings
    try:
        with open( os.path.join(yamlfile), "r" ) as f:
           aws = yaml.safe_load( f )
    except Exception as e:
        errMsg = "ABORT: unable to open settings file '%s'\n" % yamlfile
        sys.stderr.write(errMsg)
        sys.exit(-1) 
    return aws

def aws_to_j2vars(aws):
    """ This takes all keys in AWS and returns keys that are all CAPS. It also does some static
        mapping for some keys. This is so older rcs3 versions out their will still work while 
        software transitions to jinja2 variables """

    sMap = [("ACCOUNT","ACCOUNTID"),("IP_ADDRESSES","IPRESTRICTIONS")]
    j2Vars = { k.upper() : v for k,v in aws.items() }
    for knew,kold in sMap:
        try:
           j2Vars[knew] = j2Vars[kold]
        except:
           pass
    return j2Vars

def replace_all(text, dic, comment=None):
    """ replace text with (key,value) (key is not regex). 
        will return '' if text begins with comment delimiter  """
    for target in dic.keys():
        text = text.replace(target, dic[target])
        if comment is not None and re.match("^\s*%s" % comment,text) is not None:
            text=''
    return text


def delete_user_keys( iam_client, acctname ):
    userkeys = iam_client.list_access_keys( UserName=acctname )
    #print( userkeys )
    for userkey in userkeys[ "AccessKeyMetadata" ]:
        #print( userkey[ "AccessKeyId" ] )
        iam_client.delete_access_key( UserName=acctname, AccessKeyId=userkey[ "AccessKeyId" ] )


def create_user_key( iam_client, acctname ):
    newkey = iam_client.create_access_key( UserName=acctname )
    # convert datetime object to text string, our next action is to save to
    # file and datatime object is unhelpful in this context
    dateobj = newkey[ "AccessKey" ][ "CreateDate" ]
    newkey[ "AccessKey" ][ "CreateDate" ] = dateobj.isoformat()
    # drop the ResponseMetadata info, not needed
    newkey.pop( "ResponseMetadata" )
    return newkey

