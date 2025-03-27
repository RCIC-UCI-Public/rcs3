#!/usr/bin/env python3
# print aws_settings.yaml as string
import os
import sys
# Make sure that we can import local items
myDirectory=os.path.realpath(os.path.dirname(__file__))
sys.path.append(myDirectory)
from rcs3functions import *
print( str(aws_to_j2vars(read_aws_settings())))
