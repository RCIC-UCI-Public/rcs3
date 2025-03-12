#!/usr/bin/env python3

import argparse
import sys
import json
from rcs3_awsperms import rcs3awsdb

if __name__ == '__main__':
         parser = argparse.ArgumentParser(description='AWS Policy Fieldsi Management',allow_abbrev=True)
         parser.add_argument('-verbose', action='store_true',help='verbosity')
         parser.add_argument('command', metavar='command',choices=['list','listview','add','delete','generate'], nargs=1, help='add | delete | list | listview | generate')
         parser.add_argument('space', metavar='space',choices=['policy','resource','principal','action','restriction'], nargs=1, help='policy | resource| principal | action | restriction')
         parser.add_argument('cmdArg', help='query argument')
         parser.add_argument('extra', nargs='?', help='extra argument')
         

         args = parser.parse_args() 
         command = args.command[0]
         space = args.space[0]
         cmdArg = args.cmdArg
         extra=args.extra
         verbose = args.verbose

         db = rcs3awsdb(verbose)
         if  verbose:
             print ("command is %s, space %s" % (command,space), file=sys.stderr)
         if command == "listview":
             print(db.getSetEntries(table=space,setName=cmdArg))
         elif command == "add":
             if args.extra is not None:
                 db.addElement(eClass=space,kw=cmdArg,val=args.extra)
         elif command == "list":
             if table == "action":
                 fields=("service","permission")
             else:
                 fields=("name","pattern")
             print(db.formatList(setView=table,setName=cmdArg,fields=fields))
         elif command == "generate":
             theDoc=json.loads(db.document(setView=space,setName=cmdArg))
             print(json.dumps(theDoc,indent=4))
            
             
             
            
