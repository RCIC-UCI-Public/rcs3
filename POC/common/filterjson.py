#!/usr/bin/env python3
import json
import sys
import os
import urllib.parse as parse

def parse_json_from_stdin():
    """Parses JSON input from stdin one record at a time.

    Returns:
        A generator that yields each parsed JSON object.
    """

    for line in sys.stdin:
        if not line.startswith('{'):
            continue
        tline=line.rstrip()
        if tline.endswith(','):
            cline=tline[:-1]
        else:
            cline=tline
        try:
            data = json.loads(cline)
            yield data
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")

if __name__ == "__main__":
    rootdir =  sys.argv[1]
    # Need a record for the root directory
    try:
        stats=os.stat(rootdir)
    except:
        stats=os.stat('.')

    print('insert into folders(folder,uid,gid,mode) values("%s",%d,%d,%d);' % (rootdir,stats.st_uid,stats.st_gid,stats.st_mode))

    for record in parse_json_from_stdin():
        # Process each record here
        metadata=record['Metadata']
        uid=int(metadata['uid'],10)
        gid=int(metadata['gid'],10)
        mode=int(metadata['mode'],8)
        pathname=parse.quote(os.path.join(rootdir,record['Path']))
        basename=parse.quote(record['Name'])
        isDir=record['IsDir']
        
        if isDir:
            print('insert into folders(folder,uid,gid,mode) values("%s",%d,%d,%d);' % (pathname,uid,gid,mode))
        else:
            size=record['Size']
            subselect='(select ID from FOLDERS where folder="%s")' % os.path.dirname(pathname)
            print('insert into files(folderid,filename,uid,gid,mode,size) values(%s,"%s",%d,%d,%d,%d);' % 
                    (subselect,basename,uid,gid,mode,size))
