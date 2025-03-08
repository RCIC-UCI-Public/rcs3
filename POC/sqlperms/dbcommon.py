#!/usr/bin/env python3

import argparse
import sys
from rcs3_awsperms import rcs3awsdb

if __name__ == '__main__':
         parser = argparse.ArgumentParser(description='AWS Policy Fieldsi Management',allow_abbrev=True)
         parser.add_argument('-verbose', action='store_true',help='verbosity')
         parser.add_argument('command', metavar='command',choices=['list','listview','add','delete','generate'], nargs=1, help='add | delete | list | listview | generate')
         parser.add_argument('table', metavar='table',choices=['policy','resource','principal','action','restriction'], nargs=1, help='policy | resource| principal | action | restriction')
         parser.add_argument('qarg', help='query argument')

         args = parser.parse_args() 
         command = args.command[0]
         table = args.table[0]
         qarg = args.qarg
         verbose = args.verbose

         db = rcs3awsdb(verbose)
         if  verbose:
             print ("command is %s, table %s" % (command,table), file=sys.stderr)
         if command == "listview":
             print(db.getSetEntries(table=table,setName=qarg))
         elif command == "list":
             if table == "action":
                 fields=("service","permission")
             else:
                 fields=("name","pattern")
             print(db.formatList(setView=table,setName=qarg,fields=fields))
             
            
