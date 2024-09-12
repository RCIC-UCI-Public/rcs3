#!/usr/bin/env python3
import sys
import os
import csv

if __name__ == "__main__":

    records = 0
    processed=100000
    processedHuman=1000000
    phCount=0


    insfolderpat = 'INSERT INTO FOLDERS(FOLDER) VALUES("%s");' 
    insfilepat = 'INSERT INTO FILES(ancestorid,folderid,filename,size,jmtime,current,deletemark,storclass,objectid) values(%s,%s,"%s",%d,julianday("%s"),%d,%d,"%s","%s");' 

    objectcount = 0;
    objectbatch = 10000;

    # Write out some debugging information
    sys.stderr.write("Record Progress every %d records\n" % processed)
    sys.stderr.write("  0M ")
    sys.stderr.flush()

    csv_reader = csv.reader(sys.stdin)
    pathset=set()
    print ("BEGIN TRANSACTION;")
    for row in csv_reader:
        records += 1
        if records % processed == 0:
             sys.stderr.write('.')
             sys.stderr.flush()
             if records % processedHuman == 0:
                 phCount += 1
                 sys.stderr.write("\n%3dM "% phCount)

        # Process each record here
        try:
           bucket,prefix,oid,current,deletemark,size,modtime,storclass = row
        except:
           sys.stderr.write("Error reading row %d: %s\n" % (records,str(row)))
           sys.exit(-1) 
        
        # Break the filename and path
        fname=os.path.basename(prefix)
        folder=os.path.dirname(prefix)
        level1 = folder.split('/',2)[0]

        try:
            if level1 not in pathset:
                print(insfolderpat % (level1))
                pathset.add(level1)
            if folder not in pathset:
                print(insfolderpat % (folder))
                pathset.add(folder)
        except:
            sys.stderr.write("folder error with (%d): %s\n " % (records,str(row)))

        subselect='(select ID from FOLDERS where folder="%s")' % folder 
        subselect2='(select ID from FOLDERS where folder="%s")' % level1
        if len(size) == 0:
           nsize = 0;
        else:
           nsize = int(size)
        try: 
            icurrent = 1 if current == 'true' else 0
            ideletemark = 1 if deletemark == 'true'  else 0
            print( insfilepat % \
               (subselect2,subselect,fname,nsize,modtime,
               icurrent,ideletemark,storclass,oid))
        except:
            sys.stderr.write("error with (%d): %s\n " % (records,str(row)))
    print ("END TRANSACTION;")
    sys.stderr.write(" %d \n"% records)

