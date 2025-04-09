#!/usr/bin/env python3
# print aws_settings.yaml as string
import os
import sys
import argparse
# Make sure that we can import local items
myDirectory=os.path.realpath(os.path.dirname(__file__))
sys.path.append(myDirectory)
from rcs3functions import *

parser = argparse.ArgumentParser(description='Jinja2 Dictionary Generator from aws-settings+ options',allow_abbrev=True)

parser.add_argument('--function',default=None, help ='add/overwrite "FUNCTION":"<name of function>"')
parser.add_argument('--owner',default=None, help ='add/overwrite "OWNER":"<name of owner>"')
parser.add_argument('--system',default=None, help ='add/overwrite "SYSTEM":"<name of system>')
parser.add_argument('--variables',default=None, help ='String representation of variables to add')
args = parser.parse_args()


baseDict = aws_to_j2vars(read_aws_settings())
if args.function:
    baseDict["FUNCTION"] = args.function
if args.owner:
    baseDict["OWNER"] = args.owner
if args.system:
    baseDict["SYSTEM"] = args.system
if args.variables:
    for (k,v) in eval(args.variables).items():
         baseDict[k] = v

print(str(baseDict))
