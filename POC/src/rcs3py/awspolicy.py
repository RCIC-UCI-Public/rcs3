#!/usr/bin/env python3

import argparse
import sys
import json
import os
from jinja2 import Environment,BaseLoader,meta

# Make sure that we can import local items
# myDirectory=os.path.realpath(os.path.dirname(__file__))
# sys.path.append(myDirectory)
from rcs3py import rcs3awsdb

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

# 6.  To create a policy document, need to first create a set and then add policy(ies) to it
#     awspolicy addSet policy SA-backup-policy
#     awspolicy addToSet policy SA-backup-policy <sid of policy>
#     awspolicy addToSet policy SA-backup-policy <sid2 if policy> 
#    
# 7. Testing a complete policy
# --- Rendering with jinja2 variables for human readability, testing
#
#     o Generate a file with aws-settings.yaml converted to standardized jinja2 variables
#               ../common/genvars.py > /tmp/myvars
#
#     o (Optional) edit generated file to add "OWNER":"<owner name>", "SYSTEM":"<systemname>" to the dictionary
#       Note: "FUNCTION" is another good testing key for generic lambda policies
#
#     o generate a policy specifying the variables
#         awspolicy.py --variables="$(cat /tmp/myvars)" generate policy template-policy3
#
#
# --- To see the jinja2 template (not rendered)
#         awspolicy.py generate policy template-policy3
#      Note: in general this form is NOT parseable JSON. It is not "pretty printed"
#

def main(Args=sys.argv[1:]):

    commands = ('add', 'addSet', 'addToSet',
       'delete','deleteSet','deleteFromSet',
       'format','generate','getVal','getVars','list','listSet','listView','modify','setNames','variables')

    spaces = ('action', 'policy', 'principal','resource','condition','all')

    # Command-specific options
    actionOptions = ('service','permission')
    policyOptions = ('actionSet','principalSet','resourceSet', 'conditionSet')
    policyKeys = tuple( x.replace('Set','') for x in policyOptions)

    parser = argparse.ArgumentParser(description='AWS Policy Document Generator',allow_abbrev=True)
    parser.add_argument('-verbose', action='store_true',help='verbosity')
    parser.add_argument('--variables',default=None, help ='string dictionary of jinja2 variables')
    parser.add_argument('command', metavar='command',choices=commands, nargs=1, help=f'{commands}')
    parser.add_argument('space', metavar='space',choices=spaces, nargs=1, help=f'{spaces}')
    parser.add_argument('spaceArg', default='%',nargs='?', help='space argument')
    parser.add_argument('extra', nargs='*', help='extra (context-specific) space argument')
    for x in actionOptions:
        parser.add_argument(f'--{x}', default=None, help=f'action space {x} qualifier (default: None)')
    
    for x in policyOptions:
        parser.add_argument(f'--{x}', default=None, help=f'policy space {x} qualifier (default: None)')

    args = parser.parse_args(Args) 
    command = args.command[0]
    space = args.space[0]
    spaceArg = args.spaceArg
    extra=args.extra
    verbose = args.verbose

    db = rcs3awsdb(verbose)
    # This is a bit circuitous, want eval(args.x), but need to build it in pieces for scope issues
    act = dict(zip(actionOptions, (f'args.{x}' for x in actionOptions)))
    pol = dict(zip(policyKeys,(f'args.{x}' for x in policyOptions)))
    ACT = {}; POL = {}
    for k,v in act.items():
        ACT[k] = eval(v)
    for k,v in pol.items():
        POL[k] = eval(v)
    optParams = { 'action': ACT, 'policy': POL}

    if  verbose:
        print ("command is %s, space %s" % (command,space), file=sys.stderr)
    if command == "listview":
        print(db.getSetEntries(table=space,setName=spaceArg))
    elif command == "add":
        if args.extra is not None:
            db.addElement(eClass=space,kw=spaceArg,val=args.extra,optParams=optParams)
    elif command == "addSet":
            db.addSet(space,spaceArg)
    elif command == "addToSet":
            db.addToSet(space,spaceArg,extra)
    elif command == "deleteFromSet":
            db.deleteFromSet(space,spaceArg,extra)
    elif command == "getVal":
            print(db.getVal(space,spaceArg))
    elif command == "getVars":
            print(db.getVars(space,spaceArg))
    elif command == "list":
            print(db.list(space,spaceArg))
    elif command == "listSet":
        print(db.listSet(space,spaceArg))
    elif command == "listView":
            print(db.list(space,spaceArg,view=True))
    elif command == "setNames":
            print(db.list(space,spaceArg,setNames=True))
    elif command == "modify":
        if args.extra is not None:
            db.modifyElement(eClass=space,kw=spaceArg,val=args.extra,optParams=optParams)
    elif command == "variables":
            print(db.variables(space))
    elif command == "generate":
        textDoc=db.document(setView=space,setName=spaceArg)

        if args.variables is not None:
            environment = Environment()
            j2template = environment.from_string(textDoc)
            ast = environment.parse(textDoc)
            #j2template = Template(textDoc)
            #textDoc = j2template.render(eval(args.variables))
            print(meta.find_undeclared_variables(ast)) 
        try:
            # Try to load as a JSON -- might fail with certain jinja2 constructs
            theDoc=json.loads(textDoc)
            print(json.dumps(theDoc,indent=4))
        except:
            pass
            # print(textDoc)
       
        
        
if __name__ == '__main__':
        main()       
