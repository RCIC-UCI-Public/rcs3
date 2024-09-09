#!/usr/bin/env python3
import sqlite3
import sys

# Connecting to sqlite
# connection object
def createDB ( dbname ):
    connection_obj = sqlite3.connect(dbname)  
    try:
         connection_obj = sqlite3.connect(dbname)  
    except:
         sys.stderr.write("Could not create/access %s\n" % dbname)
         sys.exit(-1)

    # cursor object
    cursor_obj = connection_obj.cursor()
    
    # Drop the  table if already exists.
    cursor_obj.execute("DROP TABLE IF EXISTS FOLDERS")
    # Creating table FOLDERS, default mode is 0700
    foldertable = """ CREATE TABLE FOLDERS (
                ID INTEGER PRIMARY KEY NOT NULL,
                FOLDER VARCHAR(512) NOT NULL UNIQUE,
                UID INTEGER DEFAULT -1,
                GID INTEGER DEFAULT -1,
                JMTIME REAL,
                JATIME REAL,
                MODE INTEGER DEFAULT 0x1C0 );"""
    cursor_obj.execute(foldertable)
    
    # Creating table FILES, default mode is 0700
    cursor_obj.execute("DROP TABLE IF EXISTS FILES")
    filetable = """ CREATE TABLE FILES (
                ID INTEGER PRIMARY KEY NOT NULL,
                FILENAME VARCHAR(512) NOT NULL,
                ANCESTORID INTEGER NOT NULL,
                FOLDERID INTEGER NOT NULL,
                UID INTEGER DEFAULT -1,
                GID INTEGER DEFAULT -1,
                MODE INTEGER DEFAULT 0x1C0,
                JMTIME REAL,
                JATIME REAL,
                SIZE INTEGER DEFAULT 0);"""
                                                            
    cursor_obj.execute(filetable)
    # Creating table OBJECTS
    cursor_obj.execute("DROP TABLE IF EXISTS OBJECTS")
    objecttable = """ CREATE TABLE OBJECTS (
                OBJID VARCHAR(50) PRIMARY KEY NOT NULL,
                FILEID INTEGER NOT NULL,
                CLASSID INTEGER,
                CURRENT INTEGER DEFAULT 1,
                DELETEMARK INTEGER DEFAULT 1,
                RESTORED INTEGER DEFAULT 0); """
                                                            
    cursor_obj.execute(objecttable)
    
    # Create table STORAGECLASS for Enumerated S3 Storage types
    classtable = """ CREATE TABLE STORAGECLASS (
                ID INTEGER PRIMARY KEY,
                CLASS VARCHAR(32) );"""
    cursor_obj.execute(classtable)

    # FILE/FOLDER VIEW
    cursor_obj.execute("DROP VIEW IF EXISTS ALLFILES")
    allfilesview = """ CREATE VIEW ALLFILES AS 
                SELECT fi.ID,fo2.FOLDER as LEVEL1,fo.FOLDER,fi.FILENAME,fi.UID,fi.GID,fi.MODE,fi.SIZE,fi.jmtime,fi.jatime from FILES fi INNER JOIN FOLDERS fo ON fi.FOLDERID=fo.ID INNER JOIN FOLDERS fo2 on fo2.ID=fi.ancestorid;""" 
    cursor_obj.execute(allfilesview)
    cursor_obj.execute("DROP VIEW IF EXISTS ALLOBJECTS")
    allobjectsview = """ CREATE VIEW ALLOBJECTS AS 
                SELECT OBJID,FOLDER,FILENAME,UID,GID,MODE,JMTIME,SIZE,
                CURRENT,DELETEMARK,STORAGECLASS.CLASS,RESTORED FROM 
                OBJECTS INNER JOIN ALLFILES ON OBJECTS.FILEID=ALLFILES.ID 
                INNER JOIN STORAGECLASS ON OBJECTS.CLASSID=STORAGECLASS.ID ;"""
    
    cursor_obj.execute(allobjectsview)

    ## Insert the basic enumerated storage types into Storage Class
    cursor_obj.execute('INSERT INTO STORAGECLASS(CLASS) VALUES("STANDARD")') 
    cursor_obj.execute("INSERT INTO STORAGECLASS(CLASS) VALUES('REDUCED_REDUNDANCY')") 
    cursor_obj.execute("INSERT INTO STORAGECLASS(CLASS) VALUES('STANDARD_IA')") 
    cursor_obj.execute("INSERT INTO STORAGECLASS(CLASS) VALUES('ONEZONE_IA')") 
    cursor_obj.execute("INSERT INTO STORAGECLASS(CLASS) VALUES('INTELLIGENT_TIERING')") 
    cursor_obj.execute("INSERT INTO STORAGECLASS(CLASS) VALUES('GLACIER')") 
    cursor_obj.execute("INSERT INTO STORAGECLASS(CLASS) VALUES('DEEP_ARCHIVE')") 
    cursor_obj.execute("INSERT INTO STORAGECLASS(CLASS) VALUES('GLACIER_IR')") 
    cursor_obj.execute("INSERT INTO STORAGECLASS(CLASS) VALUES('SNOW')") 
    connection_obj.commit()
    
    cursor_obj.execute("CREATE INDEX DIRNAMES on FOLDERS(folder)")
    cursor_obj.execute("PRAGMA journal_mode=memory")
    cursor_obj.execute("PRAGMA synchronous=off")
    cursor_obj.execute("PRAGMA foreign_keys=on")
    connection_obj.commit()

    print("Tables are Ready")
    # Close the connection
    connection_obj.close()

if __name__ == "__main__":
    createDB(sys.argv[1])
