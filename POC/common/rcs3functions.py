#!/usr/bin/env python3
# Commonly-used functions in RCS3 python programs
import os
import sys
import yaml
import json

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
    with open( os.path.join(yamlfile), "r" ) as f:
        aws = yaml.safe_load( f )
    return aws

def replace_all(text, dic):
    """ replace text with (key,value) (key is not regex).  """
    for target in dic.keys():
        text = text.replace(target, dic[target])
    return text

