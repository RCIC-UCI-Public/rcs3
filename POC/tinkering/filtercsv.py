#!/usr/bin/env python3
import sys
import os
import csv

if __name__ == "__main__":
    records = 0
    processed=100000
    processedHuman=1000000
    phCount=0

    # Write out some debugging information
    sys.stderr.write("Record Progress every %d records\n" % processed)
    sys.stderr.write("  0M ")
    sys.stderr.flush()

    csv_reader = csv.reader(sys.stdin)
    pathset=set()
    for row in csv_reader:
        records += 1
        if records % processed == 0:
             sys.stderr.write('.')
             sys.stderr.flush()
             if records % processedHuman == 0:
                 phCount += 1
                 sys.stderr.write("\n%3dM "% phCount)

        # Process each record here
        bucket,prefix,oid,current,deletemark,size,modtime,storclass = row
        
        # Break the filename and path
        fname=os.path.basename(prefix)
        folder=os.path.dirname(prefix)
        level1 = folder.split('/',2)[0]

        if level1 not in pathset:
            print('insert into folders(folder) values("%s");' % (level1))
            pathset.add(level1)
        if folder not in pathset:
            print('insert into folders(folder) values("%s");' % (folder))
            pathset.add(folder)

        subselect='(select ID from FOLDERS where folder="%s")' % folder 
        subselect2='(select ID from FOLDERS where folder="%s")' % level1
        subselect3='(select ID from STORAGECLASS where CLASS="%s")' % storclass
        print('insert into files(ancestorid,folderid,filename,size,jmtime) values(%s,%s,"%s",%d,julianday("%s"));' % 
                    (subselect2,subselect,fname,int(size),modtime))

        subselect3='(select ID from allfiles where folder="%s" and filename="%s")' %(folder,fname)
        subselect4='(select ID from STORAGECLASS where CLASS="%s")' % storclass
        print('insert into objects(OBJID,FILEID,CLASSID,CURRENT,DELETEMARK) values("%s",%s,%s,%d,%d);' %
                 (oid,subselect3,subselect4,1 if current == 'true'  else 0,
                  1 if deletemark == 'true'  else 0)) 

