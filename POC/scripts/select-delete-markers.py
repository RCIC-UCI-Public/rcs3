#! /usr/bin/python3

import argparse
import json

usage="Transform AWS list-object output to delete-object input"
p = argparse.ArgumentParser( description=usage )
p.add_argument( "inputfile",
        help="JSON file to read from" )
p.add_argument( "outputfile",
        help="save JSON output, create new file or overwrite existing" )
p.add_argument( "-m", "--maxcount", type=int, default=1000,
        help="maximum number of objects to include per file" )
g = p.add_mutually_exclusive_group()
g.add_argument( "-a", "--all-objects",
        action="store_true",
        help="all objects even if no associated delete marker" )
g.add_argument( "-i", "--include-objects",
        action="store_true",
        help="include original objects along with delete markers" )
args = p.parse_args()


fp = open( args.inputfile )
try:
    jp = json.load( fp )
except:
    #print( "Unexpected error: %s" % e )
    print( "Error parsing", args.inputfile )
    exit(0)
objs = []
objkeys = set()


def save_objects( o, f, n ):
    fn = "{}.{}".format( f, n )
    fp = open( fn, "w" )
    wrapper = {}
    wrapper[ "Objects" ] = o
    wrapper[ "Quiet" ] = False
    #json.dump( wrapper, fp , indent=4)
    json.dump( wrapper, fp )
    print( "{}".format( fn ) )


count = 0
filen = 1
for i in jp[ "DeleteMarkers" ]:
    x = {}
    objkeys.add( i[ "Key" ] )
    x[ "Key" ] =  i[ "Key" ]
    x[ "VersionId" ] =  i[ "VersionId" ]
    objs.append( x )
    count += 1
    if count == args.maxcount:
        save_objects( objs, args.outputfile, filen )
        objs = []
        count = 0
        filen += 1

if args.all_objects:
    for i in jp[ "Versions" ]:
        x = {}
        x[ "Key" ] =  i[ "Key" ]
        x[ "VersionId" ] =  i[ "VersionId" ]
        objs.append( x )
        count += 1
        if count == args.maxcount:
            save_objects( objs, args.outputfile, filen )
            objs = []
            count = 0
            filen += 1

if args.include_objects:
    for i in jp[ "Versions" ]:
        if i[ "Key" ] in objkeys:
            x = {}
            x[ "Key" ] =  i[ "Key" ]
            x[ "VersionId" ] =  i[ "VersionId" ]
            objs.append( x )
            count += 1
            if count == args.maxcount:
                save_objects( objs, args.outputfile, filen )
                objs = []
                count = 0
                filen += 1

if count > 0:
    save_objects( objs, args.outputfile, filen )

