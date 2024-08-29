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
    records = 0
    processed=100000
    processedHuman=1000000
    phCount=0
    rootdir =  sys.argv[1]
    rtd_len = len(rootdir.split(os.path.sep))+1
    # Need a record for the root directory
    try:
        stats=os.stat(rootdir)
    except:
        stats=os.stat('.')

    print('insert into folders(folder,uid,gid,mode) values("%s",%d,%d,%d);' % (rootdir,stats.st_uid,stats.st_gid,stats.st_mode))
  

    # Write out some debugging information
    sys.stderr.write("Record Progress every %d records\n" % processed)
    sys.stderr.write("  0M ")
    sys.stderr.flush()

    for record in parse_json_from_stdin():
        records += 1
        if records % processed == 0:
             sys.stderr.write('.')
             sys.stderr.flush()
             if records % processedHuman == 0:
                 phCount += 1
                 sys.stderr.write("\n%3dM "% phCount)

        # Process each record here
        metadata=record['Metadata']
        uid=int(metadata['uid'],10)
        gid=int(metadata['gid'],10)
        mode=int(metadata['mode'],8)
        pathname=parse.quote(os.path.join(rootdir,record['Path']))
        labname=os.path.sep.join(pathname.split(os.path.sep)[0:rtd_len])
        basename=parse.quote(record['Name'])
        isDir=record['IsDir']
        
        if isDir:
            print('insert into folders(folder,uid,gid,mode) values("%s",%d,%d,%d);' % (pathname,uid,gid,mode))
        else:
            size=record['Size']
            subselect='(select ID from FOLDERS where folder="%s")' % os.path.dirname(pathname)
            subselect2='(select ID from FOLDERS where folder="%s")' % labname
            print('insert into files(ancestorid,folderid,filename,uid,gid,mode,size) values(%s,%s,"%s",%d,%d,%d,%d);' % 
                    (subselect2,subselect,basename,uid,gid,mode,size))
