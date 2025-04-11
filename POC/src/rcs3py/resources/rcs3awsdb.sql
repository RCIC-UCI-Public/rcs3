CREATE TABLE actionSets ( 
	ID                   INTEGER NOT NULL  PRIMARY KEY  ,
	setName              TEXT NOT NULL    ,
	CONSTRAINT unq_permSets_setName UNIQUE ( setName )
 );

CREATE TABLE actions ( 
	ID                   INTEGER NOT NULL  PRIMARY KEY  ,
	service              TEXT     ,
	permission           TEXT     
 );

CREATE UNIQUE INDEX unq_action ON actions ( service, permission );

CREATE TABLE conditionSets ( 
	ID                   INTEGER NOT NULL  PRIMARY KEY  ,
	setName              TEXT NOT NULL    ,
	CONSTRAINT unq_constraintSets UNIQUE ( setName )
 );

CREATE TABLE conditions ( 
	ID                   INTEGER NOT NULL  PRIMARY KEY  ,
	name                 TEXT NOT NULL    ,
	pattern              TEXT NOT NULL    ,
	CONSTRAINT unq_constraints UNIQUE ( name )
 );

CREATE TABLE policySets ( 
	ID                   INTEGER NOT NULL  PRIMARY KEY  ,
	setName              TEXT     ,
	CONSTRAINT unq_policySets UNIQUE ( setName )
 );

CREATE TABLE principalSets ( 
	ID                   INTEGER NOT NULL  PRIMARY KEY  ,
	setName              TEXT NOT NULL    ,
	CONSTRAINT unq_principalSets UNIQUE ( setName )
 );

CREATE TABLE principals ( 
	ID                   INTEGER NOT NULL  PRIMARY KEY  ,
	name                 TEXT NOT NULL    ,
	pattern              TEXT NOT NULL    ,
	CONSTRAINT unq_principals_name UNIQUE ( name )
 );

CREATE TABLE resourceSets ( 
	ID                   INTEGER NOT NULL  PRIMARY KEY  ,
	setName              TEXT NOT NULL    ,
	CONSTRAINT unq_resourceSets_setName UNIQUE ( setName )
 );

CREATE TABLE resources ( 
	ID                   INTEGER NOT NULL  PRIMARY KEY  ,
	name                 TEXT NOT NULL    ,
	pattern              TEXT NOT NULL    ,
	CONSTRAINT unq_resources_name UNIQUE ( name )
 );

CREATE TABLE actionSetMembers ( 
	ID                   INTEGER NOT NULL  PRIMARY KEY  ,
	memberID             INTEGER NOT NULL    ,
	setID                INTEGER     ,
	FOREIGN KEY ( setID ) REFERENCES actionSets( ID ) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY ( memberID ) REFERENCES actions( ID ) ON DELETE CASCADE ON UPDATE CASCADE
 );

CREATE UNIQUE INDEX unq_asmMemberSet ON actionSetMembers ( memberID, setID );

CREATE TABLE conditionSetMembers ( 
	ID                   INTEGER NOT NULL  PRIMARY KEY  ,
	memberID             INTEGER     ,
	setID                INTEGER     ,
	CONSTRAINT unq_conditionSetMembers UNIQUE ( memberID, setID ),
	FOREIGN KEY ( memberID ) REFERENCES conditions( ID ) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY ( setID ) REFERENCES conditionSets( ID ) ON DELETE CASCADE ON UPDATE CASCADE
 );

CREATE TABLE policies ( 
	ID                   INTEGER NOT NULL  PRIMARY KEY  ,
	sid                  TEXT NOT NULL    ,
	action               INTEGER NOT NULL    ,
	resource             INTEGER     ,
	principal            INTEGER     ,
	effect               TEXT     ,
	condition            INTEGER     ,
	CONSTRAINT unq_sidStatement UNIQUE ( sid ),
	FOREIGN KEY ( action ) REFERENCES actionSets( ID ) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY ( resource ) REFERENCES resourceSets( ID ) ON DELETE SET NULL ON UPDATE CASCADE,
	FOREIGN KEY ( principal ) REFERENCES principalSets( ID ) ON DELETE SET NULL ON UPDATE CASCADE,
	FOREIGN KEY ( condition ) REFERENCES conditionSets( ID ) ON DELETE CASCADE ON UPDATE CASCADE,
	CHECK (  EFFECT=='Allow' or EFFECT=='Deny' )
 );

CREATE UNIQUE INDEX unq_policies ON policies ( effect, action, resource, principal, condition );

CREATE TABLE policySetMembers ( 
	memberID             INTEGER NOT NULL    ,
	setID                INTEGER NOT NULL    ,
	ID                   INTEGER NOT NULL  PRIMARY KEY  ,
	FOREIGN KEY ( setID ) REFERENCES policySets( ID ) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY ( memberID ) REFERENCES policies( ID )  
 );

CREATE UNIQUE INDEX unq_policysetID ON policySetMembers ( setID, memberID );

CREATE TABLE principalSetMembers ( 
	ID                   INTEGER NOT NULL  PRIMARY KEY  ,
	memberID             INTEGER NOT NULL    ,
	setID                INTEGER NOT NULL    ,
	FOREIGN KEY ( memberID ) REFERENCES principals( ID ) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY ( setID ) REFERENCES principalSets( ID ) ON DELETE CASCADE ON UPDATE CASCADE
 );

CREATE UNIQUE INDEX unq_memberID ON principalSetMembers ( memberID, setID );

CREATE TABLE resourceSetMembers ( 
	ID                   INTEGER NOT NULL  PRIMARY KEY  ,
	memberID             INTEGER NOT NULL    ,
	setID                INTEGER     ,
	FOREIGN KEY ( memberID ) REFERENCES resources( ID ) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY ( setID ) REFERENCES resourceSets( ID ) ON DELETE CASCADE ON UPDATE CASCADE
 );

CREATE UNIQUE INDEX unq_rsmmemberID ON resourceSetMembers ( memberID, setID );

CREATE VIEW actionSetsView as select setName,service,permission from actionSetMembers asm join actions a on asm.memberID=a.id join actionSets aSets on asm.setID=aSets.ID;

CREATE VIEW conditionSetsView as select setName,name,pattern from conditionSetMembers csm join conditions c on csm.memberID=c.id join conditionSets cSets on csm.setID=cSets.ID;

CREATE VIEW policySetsView as select psets.setName,p.sid,p.effect,aset.setName as action, rset.setName as resource, prset.setName as principal, cset.setName as 'condition' from policySetMembers psm join policies p on psm.memberID=p.id join policySets psets on psm.setID=psets.ID join actionSets aset on p.action=aset.ID left join resourceSets rset on p.resource=rset.ID left join principalSets prset on p.principal=prset.ID left join conditionSets cset on p.'condition'=cset.ID;

CREATE VIEW policyView as select p.ID, p.sid,p.effect,aset.setName as action, rset.setName as resource, prset.setName as principal, cset.setName as 'condition'  from policies p join actionSets aset on p.action=aset.ID left join resourceSets rset on p.resource=rset.ID left join principalSets prset on p.principal=prset.ID left join conditionSets cset on p.'condition'=cset.ID order by p.sid;

CREATE VIEW principalSetsView as select setName,name,pattern from principalSetMembers psm join principals p on psm.memberID=p.id join principalSets pSets on psm.setID=pSets.ID;

CREATE VIEW resourceSetsView as select setName,name,pattern from resourceSetMembers rsm join resources r on rsm.memberID=r.id join resourceSets rSets on rsm.setID=rSets.ID;

