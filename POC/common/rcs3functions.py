#!/usr/bin/env python3
# Commonly-used functions in RCS3 python programs
import os
import sys
import yaml
import json
import io
import re


class TextIgnoreCommentsWrapper(io.TextIOWrapper):
    """ Wrap a file to filter out lines STARTING with '#' when reading"""
    def __init__(self, filename, mode='r', encoding='utf-8'):
        file = open(filename, mode + 'b')  # Open in binary mode
        super().__init__(file, encoding=encoding)

    def __iter__(self):
        return self

    def __next__(self):
        line = super().readline()
        while line and line.startswith("#"):
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

