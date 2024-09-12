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
                SIZE INTEGER DEFAULT 0,
                OBJECTID VARCHAR(50) NOT NULL,
                CURRENT INTEGER DEFAULT 1,
                DELETEMARK INTEGER DEFAULT 1,
                STORCLASS VARCHAR(16) DEFAULT 'LOCAL',
                RESTORED INTEGER DEFAULT 0); """
                                                            
    cursor_obj.execute(filetable)
    
    # FILE/FOLDER VIEW
    cursor_obj.execute("DROP VIEW IF EXISTS ALLFILES")
    allfilesview = """ CREATE VIEW ALLFILES AS 
                SELECT fi.ID,fo2.FOLDER as LEVEL1,fo.FOLDER,fi.FILENAME,fi.UID,fi.GID,fi.MODE,fi.SIZE,fi.jmtime,fi.jatime from FILES fi INNER JOIN FOLDERS fo ON fi.FOLDERID=fo.ID INNER JOIN FOLDERS fo2 on fo2.ID=fi.ancestorid;""" 
    cursor_obj.execute(allfilesview)
    cursor_obj.execute("DROP VIEW IF EXISTS ALLOBJECTS")
    allobjectsview = """ CREATE VIEW ALLOBJECTS AS 
                SELECT fi.ID,fi.OBJECTID,fo2.FOLDER as LEVEL1,fo.FOLDER,fi.FILENAME,fi.SIZE,fi.jmtime,fi.CURRENT,fi.DELETEMARK,fi.STORCLASS,fi.RESTORED from FILES fi INNER JOIN FOLDERS fo ON fi.FOLDERID=fo.ID INNER JOIN FOLDERS fo2 on fo2.ID=fi.ancestorid;""" 
    
    cursor_obj.execute(allobjectsview)

    print("Tables are Ready")
    # Close the connection
    connection_obj.close()

if __name__ == "__main__":
    createDB(sys.argv[1])
