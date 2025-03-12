#!/usr/bin/env python3

import argparse
import sys
import json
from rcs3_awsperms import rcs3awsdb

commands = ('add', 'addSet', 'addToSet',
            'delete','deleteSet','deleteFromSet',
            'format','generate','list','listSet','modify')

spaces = ('action', 'policy', 'principal','resource','condition')

# Command-specific options
actionOptions = ('service','permission')
#policyOptions = ('actionSet','principalSet','resourceSet', 'conditionSet')
policyOptions = ('actionSet','principalSet','resourceSet')

policyKeys = tuple( x.replace('Set','') for x in policyOptions)

# Command Structure
# awspolicy <command> <space> <arg1> [<context argument>] [--optional <arg> [ --optional <arg> ...] 

# Examples
# 1.  Add the S3:ListObject action
#     awspolicy add action S3 ListObject

# 2.  Add the backupBucket and backupBucketContents resources
#     awspolicy add resource backupBucket 'arn:aws:s3:::{{OWNER}}-{{SYSTEM}}-{{BACKUP_POSTFIX}}'     
#     awspolicy add resource backupBucketResources 'arn:aws:s3:::{{OWNER}}-{{SYSTEM}}-{{BACKUP_POSTFIX}}/*'     

# 3.  add the backupBucketResources set
#     awspolicy addSet resource backupBucketResources

# 4.  add the backupBucket and backupBucketContents to the backupBucketResources set
#     awspolicy addToSet resource backupBucketResources backupBucket
#     awspolicy addToSet resource backupBucketResources backupBucketContents

# 5.  a policy has a name (SID) and an Effect (optional argument)
#     awspolicy add policy <sid> <effect> [--actionSet=<name>] [--resourceSet=<name>] [--principalSet=<name>] [--conditionSet=<name>]
#     Note: the sets referred to must exist

#6    To create a policy document, need to first create a set and then add policy(ies) to it
#     awspolicy addSet policy SA-backup-policy
#     awspolicy addToSet policy SA-backup-policy <sid of policy>
#     awspolicy addToSet policy SA-backup-policy <sid2 if policy> 
#    

if __name__ == '__main__':

         parser = argparse.ArgumentParser(description='AWS Policy Document Generator',allow_abbrev=True)
         parser.add_argument('-verbose', action='store_true',help='verbosity')
         parser.add_argument('command', metavar='command',choices=commands, nargs=1, help=f'{commands}')
         parser.add_argument('space', metavar='space',choices=spaces, nargs=1, help=f'{spaces}')
         parser.add_argument('spaceArg', default='%',nargs='?', help='space argument')
         parser.add_argument('extra', nargs='?', help='extra (context-specific) space argument')
         for x in actionOptions:
             parser.add_argument(f'--{x}', default=None, help=f'action space {x} qualifier (default: None)')
         
         for x in policyOptions:
             parser.add_argument(f'--{x}', default=None, help=f'policy space {x} qualifier (default: None)')

         args = parser.parse_args() 
         command = args.command[0]
         space = args.space[0]
         spaceArg = args.spaceArg
         extra=args.extra
         verbose = args.verbose

         print(args)
         for x in policyOptions:
             print(x,eval(f'args.{x}'))
         db = rcs3awsdb(verbose)
         optParams = { 'action':dict(zip(actionOptions, (eval(f'args.{x}') for x in actionOptions))),
                      'policy':dict(zip(policyKeys,(eval(f'args.{x}') for x in policyOptions)))
                    }
         print(optParams)
         if  verbose:
             print ("command is %s, space %s" % (command,space), file=sys.stderr)
         if command == "listview":
             print(db.getSetEntries(table=space,setName=spaceArg))
         elif command == "add":
             if args.extra is not None:
                 db.addElement(eClass=space,kw=spaceArg,val=args.extra,optParams=optParams)

         elif command == "list":
             print(db.formatList(setView=space,setName=spaceArg,fields=fields,optParams=optParams))
         elif command == "generate":
             theDoc=json.loads(db.document(setView=space,setName=spaceArg))
             print(json.dumps(theDoc,indent=4))
            
             
             
            
