#!/usr/bin/env python3

import sqlite3
import os
import sys
import shlex
import json
from jinja2 import Template
from platformdirs import user_config_dir

# Make sure that we can import local items
myDirectory=os.path.realpath(os.path.dirname(__file__))
sys.path.append(myDirectory)

import statementParts as SP;

class elements:
    def __init__(self):
        self._maps = { 'action':'actions','condition':'conditions', 'principal':'principals',
                'policy':'policies','resource':'resources'}
        self._tcols = { 'action': ('service','permission'),
                'condition' : ('name','pattern'),
                'principal' : ('name','pattern'),
                'policy' : ('sid','effect'),
                'resource' : ('name','pattern')}

    def etable(self,tname):
        """ map the singular name to the table name that holds the baseline elements"""
        return self._maps[tname]

    def cols(self,tname):
        """ names of the fields in each element table """
        return self._tcols[tname]

    def patternSpaces(self):
        """ Return the spaces where 'pattern' is a field name """
        f = lambda x: x[0] if 'pattern' in x[1] else None
        spaces = list(filter( lambda y: y is not None, [ f(x) for x in self._tcols.items()]))
        return spaces

class rcs3awsdb:
    def __init__(self,verbose=False,database='rcs3aws.db'):
       self._dbfile = database
       if os.path.sep not in database:
           pkgOrName = __name__ if len(__package__) == 0 else __package__
           configPath = user_config_dir(pkgOrName)
           os.makedirs(configPath, exist_ok=True)
           self._dbfile=os.path.join(configPath,database)
       if verbose:
           print(self._dbfile)
       callInitialize = True if not os.path.exists(self._dbfile) else False
       self.connection=sqlite3.connect(self._dbfile)
       self.cursor = self.connection.cursor()
       self.cursor.execute("PRAGMA foreign_keys=on")
       self.verbose = verbose
       self.elem = elements()
       if callInitialize:
           self.initializeDB()

    def initializeDB(self):
       """ Construct the database and populate """ 
       resourceDir = os.path.join(myDirectory,'resources')
       self._dbconfig=os.path.join(resourceDir,"rcs3awsdb.config")
       self._tabledefs=os.path.join(resourceDir,"rcs3awsdb.sql")

       if self.verbose:
           print(f"Initializing Database at '{self._dbfile}'. Just a few moments...", file=sys.stderr)
       # Build out the structure
       with open(self._tabledefs,"r") as td:
           sqlscript = td.read() 
       self.cursor.executescript(sqlscript)
       self.connection.commit()

       # Populate the database
       try:
           import awspolicy
       except:
           from rcs3py import awspolicy   
       with open(self._dbconfig,"r") as dbc:
           for l in dbc.readlines():
               if l.startswith('#') or len(l) < 3:
                   pass
               else:
                   args = shlex.split(l)
                   awspolicy.main(args)



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
    
    def quoteOrRaw(self,arg):
        """Arg is a string, but the string might represent a dictionary. If so, don't quote,
           else quote """

        # Special handling: A string that starts with with '#' and '#':
        #              o strip the leading and trailing #
        #              o do NOT quote
        # Needed to escape out complex jinja2 expressions

        if len(arg) > 2 and arg.startswith('#') and arg.endswith('#'):
            return arg[1:-1]

        # Try to guess if we should NOT quote
        # 1. Is this a string-version of python dict
        try:
            isDict = eval(arg)
            if type(isDict) is dict:
                return arg
        except:
            pass
        # 2. if enclosed in { }, is this a string-version of python dict
        try:
            isDict = eval(f"{{ {arg} }}")
            if type(isDict) is dict:
                return arg
        except:
            if arg.startswith("{"):
                return arg
        return '"%s"' % arg

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
       formatted = ",\n".join( (self.quoteOrRaw(x) for x in joinedFields) )

       return formatted

    def document(self,setName,setView="policy",j2Vars=None,jsonFormat=False):
       """Using statement parts, format a complete policy document, return as a string
          If j2Vars is supplied, then render variables prior to returning"""
       
       theDoc = ""
       statements = []
       # Read each meta-statement in from the policySetsView to format out a statement
       (fieldNames,rows)=self.getSetEntries(table=setView,setName=setName);
       asDict = [ dict(zip(fieldNames,x)) for x in rows ]
       for entry in asDict:
           # Each entry can have multiple list expansions. expand all list (sets) into formatted
           # strings to make up a single policy statement 
           PList = self.formatList(setView='principal',setName=entry['principal'],fields="pattern")
           RList = self.formatList(setView='resource',setName=entry['resource'],fields="pattern")
           CList = self.formatList(setView='condition',setName=entry['condition'],fields="pattern")
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
       theDoc = SP.jsonTemplate.format(STATEMENTLIST=",\n".join(statements))
       
       # Render the jinja2 variables in theDoc
       if j2Vars is not None:
           j2template = Template(theDoc)
           theDoc = j2template.render(j2Vars)

       # Return JSON or String 
       if jsonFormat:
           return json.loads(theDoc)
       return theDoc



    def addElement(self,eClass,kw,val,optParams={},update=False):
       """add (or optionally modify existing) a base element to the eClass """
       table = self.elem.etable(eClass)
       cols = self.elem.cols(eClass)

       fields = [ e for e in cols ]
       values = [f"'{kw}'", f"'{val[0]}'"]

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
       if not update:
           stmt = f"INSERT INTO {table}({tfields}) VALUES({tvalues});"
       elif table !=  "actions":
           setFormat = [ f"{x[0]} = {x[1]}" for x in  list(zip(fields,values))[1:] ]
           setString = ", ".join(setFormat)
           stmt = f"UPDATE {table} SET {setString} WHERE {fields[0]} = {values[0]};"
       else:
           return

       self.execute(stmt) 
       self.commit()
    
    def modifyElement(self,eClass,kw,val,optParams={}):
       """ modify an existing base element to the eClass """
       self.addElement(eClass,kw,val,optParams={},update=True)

    def addSet(self,space,setName):
       """Add a Set of setName to the space """
       stmt = f"INSERT INTO {space}Sets(setName) VALUES('{setName}');"
       self.execute(stmt) 
       self.commit()
    
    def addToSet(self,space,setName,*selectors,delete=False):
       """Add (or Delete) selectors into setName to the space """
       # Special Handling for action space
       if space == 'action':
           service,permission = selectors[0][0], selectors[0][1]
           memberID = f"( select ID from {self.elem.etable(space)} where service='{service}' and permission='{permission}')"
       else:
           name = selectors[0][0]
           memberID = f"(select ID from {self.elem.etable(space)} where {self.elem.cols(space)[0]}='{name}')"
       setID = f"(select ID from {space}Sets where setName='{setName}')"
       if delete:
           stmt = f"""DELETE FROM {space}SetMembers WHERE memberID={memberID} and setID={setID};"""
       else: 
           stmt = f"""INSERT INTO {space}SetMembers(memberID,setID) 
                  VALUES({memberID},{setID});"""
       self.execute(stmt) 
       self.commit()
    
    def deleteFromSet(self,space,setName,*selectors):
       """Delete selectors into setName to the space """
       self.addToSet(space,setName,*selectors,delete=True)

    def printRows(self,fieldNames,rows):
       """ Format a "table" for human-readable printing """
       header = " | ".join(fieldNames)
       data = header + "\n"
       for row in rows:
           sfmt = tuple((str(x) for x in row))
           srow = ( "" if x is None else x for x in sfmt)
           data += " | ".join(srow) + "\n"
       return data 

    
    def list(self,space,key='%',view=False,setNames=False):
       (fieldNames,rows) = self.listRaw(space,key,view,setNames)
       return self.printRows(fieldNames,rows)

    def getVal(self, space,key='%',view=False,setNames=False,field=None):
       if field is None:
          field=self.elem.cols(space)[1]
       (fieldNames,rows) = self.listRaw(space,key,view,setNames)
       idx = fieldNames.index(field)
       rvals = [ row[idx] for row in rows ]
       if len(rvals) > 1:
           return rvals
       else:
           return rvals[0]
       



    def listRaw(self,space,key='%',view=False,setNames=False):
       """ List the Elements of a space,view,or Sets""" 
       keyColumn = self.elem.cols(space)[0]
       if view:
           table=f"{space}View"
       elif setNames:
           table=f"{space}Sets"
           keyColumn = "setName"
       else:
           table = self.elem.etable(space)
       query = f"SELECT * from {table} where {keyColumn} like '{key}' order by {keyColumn}" 
       (fieldNames,rows)=self.getTableEntries(table,query)
       return (fieldNames,rows)

    def listSet(self,space,key='%'):
       """ List the Elements of a Set """ 
       (fieldNames,rows)=self.getSetEntries(table=space,setName=key)
       return self.printRows(fieldNames,rows)

    def variables(self,space):
        """ Return the set of Jinja2 variables defined """
        definedVars= set()
        if space == "all":
            searchSpace = self.elem.patternSpaces()
        else:
            searchSpace = [space,]

        
        for table in searchSpace:
            etable=self.elem.etable(table)
            query = f"SELECT * from {etable}" 
            (fieldNames,rows)=self.getTableEntries(etable,query)
            asDictList = [ dict(zip(fieldNames,x)) for x in rows ]
            for rowDict in asDictList:
                pattern=rowDict['pattern']
                # look for split items that have '}}' in them -- these are strings that start with a jinja2 var
                jvars = filter(lambda x: "}}" in x, pattern.split("{{"))
                trimmedVars = [ x.replace("}}"," ").strip().split()[0] for x in jvars ]
                for x in trimmedVars:
                    definedVars.add(x)

        return definedVars
