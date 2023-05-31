#! /usr/bin/python3

import argparse
import json

usage="Transform AWS list-object output to delete-object input"
p = argparse.ArgumentParser( description=usage )
p.add_argument( "inputfile",
        help="JSON file to read from" )
p.add_argument( "outputfile",
        help="save JSON output, create new file or overwrite existing" )
p.add_argument( "-i", "--include-objects",
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
sp = open( args.outputfile, "w" )
objs = []
objkeys = set()

for i in jp[ "DeleteMarkers" ]:
    x = {}
    #print( i[ "Key" ] )
    #print( i[ "VersionId" ] )
    objkeys.add( i[ "Key" ] )
    x[ "Key" ] =  i[ "Key" ]
    x[ "VersionId" ] =  i[ "VersionId" ]
    objs.append( x )

if args.include_objects:
    for i in jp[ "Versions" ]:
        if i[ "Key" ] in objkeys:
            x = {}
            #print( i[ "Key" ] )
            #print( i[ "VersionId" ] )
            x[ "Key" ] =  i[ "Key" ]
            x[ "VersionId" ] =  i[ "VersionId" ]
            objs.append( x )

wrapper = {}
wrapper[ "Objects" ] = objs
wrapper[ "Quiet" ] = False
json.dump( wrapper, sp , indent=4)

