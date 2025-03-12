#!/usr/bin/env python3

import sqlite3
import sys
import statementParts as SP;

class elements:
    def __init__(self):
        self._maps = { 'action':'actions','constraint':'constraints', 'principal':'principals',
                'policy':'policies','resource':'resources'}
        self._tcols = { 'action': ('service','permission'),
                'constraint' : ('name','pattern'),
                'principal' : ('name','pattern'),
                'policy' : ('sid','effect'),
                'resource' : ('name','pattern')}

    def etable(self,tname):
        """ map the singular name to the table name that holds the baseline elements"""
        return self._maps[tname]

    def cols(self,tname):
        """ names of the fields in each element table """
        return self._tcols[tname]

class rcs3awsdb:
    def __init__(self,verbose=False):
       self.connection=sqlite3.connect('rcs3aws.db')
       self.cursor = self.connection.cursor()
       self.cursor.execute("PRAGMA foreign_keys=on")
       self.verbose = verbose
       self.elem = elements()

    def execute(self,stmt,errorsToCaller=False):
       try:
           if self.verbose:
               print("execute: '%s'" % stmt, file=sys.stderr)
           self.cursor.execute(stmt)
       except sqlite3.IntegrityError as e:
           if not errorsToCaller:
           	print("Integrity Error for: '%s'" % stmt, file=sys.stderr)
           else:
                raise(e)
               

    def commit(self):
       self.connection.commit()

    def lookup(self,stmt):
       """ execute the statement and return rows that matched.
           Return an empty list on error or if stmt is None"""
       if stmt is None:
           return []
       try:
           self.execute(stmt)
           rvals = self.cursor.fetchall() 
       except:
           rvals = []
       return rvals

    def getColumnNames(self,table=None):
       """ return the tuple of column names for a table """
       if table is None:
           return []
       cols=self.lookup("SELECT name FROM pragma_table_info('%s')" % table)
       cnames=[ x[0] for x in cols]
       return cnames

    def getTableEntries(self,table=None,query=None):
       """ return a tuple ([column Names],[rows]) of entries in a table that match the query"""
       columns = self.getColumnNames(table)
       return (columns,self.lookup(query))

    def getSetEntries(self,table="policy",setName='%'):
       """ return a tuple ([column Names],[rows]) of entries in a set view that match setName """
       tableView = "%sSetsView" % table 
       query = "SELECT * from '%s' where setName like '%s' order by setName" % (tableView, setName)
       return self.getTableEntries(table=tableView,query=query)
    
    def formatList(self,setView=None,setName=None,fields=(),joiner=":"):
       """Return formatted (suitable for inclusion in json policy statement) list elements in the set  """
       (fieldNames,rows)=self.getSetEntries(table=setView,setName=setName);
       asDict = [ dict(zip(fieldNames,x)) for x in rows ]
       if type(fields) is str:
           selectors = (fields,)
       else:
           selectors = fields

       # Pythonic way to select only the fields from each row (by field name) and then joining into strings 
       joinedFields=[ joiner.join( (row[key] for key in selectors) ) for row in asDict ]

       # Finally, need each joinedField to be wrapped in double quotes and then put in a comma separated list
       formatted = ",\n".join( ('"%s"' %x for x in joinedFields) )
       return formatted

    def document(self,setName,setView="policy"):
       """Using statement parts, format a complete policy document"""
       
       theDoc = ""
       statements = []
       # Read each meta-statement in from the policySetsView to format out a statement
       (fieldNames,rows)=self.getSetEntries(table=setView,setName=setName);
       print(setName, setView)
       asDict = [ dict(zip(fieldNames,x)) for x in rows ]
       for entry in asDict:
           # Each entry can have multiple list expansions. expand all list (sets) into formatted
           # strings to make up a single policy statement 
           PList = self.formatList(setView="principal",setName=entry['principal'],fields="pattern")
           RList = self.formatList(setView="resource",setName=entry['resource'],fields="pattern")
           #Clist = self.formatList(setView="condition",setName=entry['condition'],fields="pattern")
           CList=""
           sid = entry['sid']
           effect = entry['effect']
           action = self.formatList(setView="action",setName=entry['action'],fields=("service","permission"))
           resource= SP.resourceTemplate.format(RESOURCELIST=RList) if len(RList) > 0 else ""
           principal= SP.principalTemplate.format(PRINCIPALLIST=PList) if len(PList) > 0 else ""
           condition= SP.conditionTemplate.format(CONDITIONLIST=CList) if len(CList) > 0 else ""

           completeStatement=(SP.spartTemplate.format(
               SID=sid,EFFECT=effect,ACTIONLIST=action,RESOURCE=resource,PRINCIPAL=principal,CONDITION=condition))
           statements.extend([completeStatement])
       
       # Join all the statements into a full policy document
       return SP.jsonTemplate.format(STATEMENTLIST=",\n".join(statements))


    def addElement(self,eClass,kw,val,optParams={}):
       """add a base element to the eClass """
       table = self.elem.etable(eClass)
       cols = self.elem.cols(eClass)

       fields = [ e for e in cols ]
       values = [f"'{kw}'", f"'{val}'"]

       # Need special handling for policies since there a number of optional arguments to include cross tables
       # a SID is required for a policy - its the "name"
       if eClass == 'policy':
           try:
              for (k,v) in optParams[eClass].items():
                  fields.extend([k,])
                  term=f"(select ID from {k}Sets where setName='{v}')" if v is not None else 'NULL'
                  values.extend([term,])
           except:
               pass
       tfields=",".join(fields)
       tvalues=",".join(values)
       stmt = f"INSERT INTO {table}({tfields}) VALUES({tvalues});"

       print(stmt)
       #self.execute(stmt) 
       #self.commit()
    
    def lookuporgs(self,org='%'):
       """ return list of orgs that match a single search criteria """
       stmt = """SELECT ID,ORGNAME,ORGDESC
                      FROM ORGS WHERE ORGNAME LIKE '%s';"""  % org
       return self.lookup(stmt)

    def lookupuserroles(self,uid='%'):
       """ return list of roles that match a user """
       stmt = """SELECT UCINETID,LAST,FIRST,ORGNAME,ROLENAME,ROLEDESC
                      FROM ADMINS WHERE UCINETID LIKE '%s' ORDER by UCINETID,ROLENAME;"""  % uid
       return self.lookup(stmt)

    def addorg(self,org,orgdesc):
       if len(self.lookuproles(org)) == 0:
          stmt = """INSERT INTO ORGS(ORGNAME,ORGDESC) VALUES('%s','%s')""" % (org,orgdesc)
          self.execute(stmt)
          self.commit()

    def addrole(self,role,roledesc):
       if len(self.lookuproles(role)) == 0:
          stmt = """INSERT INTO ROLES(ROLENAME,ROLEDESC) VALUES('%s','%s')""" % (role,roledesc)
          self.execute(stmt)
          self.commit()

    def adduser(self,uid,last,first,campusid,email,dept):

       statement = """INSERT INTO USERS(UCINETID,LAST,FIRST,UCICAMPUSID,EMAIL,ORG) 
                VALUES('%s','%s','%s','%s','%s',
                (Select ID from ORGS where ORGNAME='%s'));""" % (uid,last,first,campusid,email,dept) 
       self.execute(statement)
       self.commit()

    def adduserrole(self,uid,role):
       statement = """INSERT INTO USERROLES(USER,ROLE) 
                VALUES((Select ID from USERS where UCINETID='%s'),
                       (Select ID from ROLES where ROLENAME='%s'));""" % (uid,role) 
       try:
           self.execute(statement,errorsToCaller=True)
           self.commit()
       except Exception as e:
           print("User %s already has role %s" % (uid,role), file=sys.stderr)

    def deluserrole(self,uid,role='%'):
       statement = """DELETE FROM USERROLES where 
                USER=(Select ID from USERS where UCINETID='%s') and ROLE=(Select ID from ROLES where ROLENAME like '%s');""" % (uid,role) 
       self.execute(statement)
       self.commit()

    def deluser(self,uid):
       statement = """DELETE FROM USERS WHERE UCINETID='%s';""" % uid
       self.execute(statement)
       self.commit()
