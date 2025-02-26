CREATE TABLE policySetMembers (
        memberID             INT NOT NULL    ,
        setID                INT NOT NULL    ,
        ID                   INTEGER NOT NULL  PRIMARY KEY  ,
        FOREIGN KEY ( setID ) REFERENCES policySets( ID ) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY ( memberID ) REFERENCES policies( ID )
 ) ;
CREATE UNIQUE INDEX unq_policysetID ON policySetMembers ( setID,memberID );
CREATE TABLE policySets (
        ID                   INTEGER PRIMARY KEY  ,
        setName              TEXT,
        CONSTRAINT unq_policySets UNIQUE ( setName )
 );
CREATE TABLE policies (
        ID                   INTEGER NOT NULL  PRIMARY KEY  ,
        sid                  TEXT NOT NULL    ,
        action               INT NOT NULL    ,
        resource             INT     ,
        principal            INT     ,
        effect               TEXT     ,
        CONSTRAINT unq_sidStatement UNIQUE ( sid ),
        FOREIGN KEY ( action ) REFERENCES actionSets( ID ) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY ( resource ) REFERENCES resourceSets( ID ) ON DELETE SET NULL ON UPDATE CASCADE,
        FOREIGN KEY ( principal ) REFERENCES principalSets( ID ) ON DELETE SET NULL ON UPDATE CASCADE,
        CHECK ( EFFECT=='Allow' or EFFECT=='Deny' )
 ) ;
CREATE UNIQUE INDEX unq_policies ON policies ( effect,action,resource,principal );
CREATE TABLE principalSetMembers (
        ID                   INTEGER NOT NULL  PRIMARY KEY  ,
        memberID             INT NOT NULL    ,
        setID                INT NOT NULL    ,
        FOREIGN KEY ( memberID ) REFERENCES principals( ID ) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY ( setID ) REFERENCES principalSets( ID ) ON DELETE CASCADE ON UPDATE CASCADE
 ) ;
CREATE UNIQUE INDEX unq_memberID ON principalSetMembers ( memberID,setID );
CREATE TABLE principalSets (
        ID                   INTEGER PRIMARY KEY  ,
        setName              TEXT NOT NULL    ,
        CONSTRAINT unq_principalSets UNIQUE ( setName )
 );
CREATE TABLE principals (
        ID                   INTEGER  PRIMARY KEY  ,
        name                 TEXT NOT NULL    ,
        pattern              TEXT NOT NULL    ,
        CONSTRAINT unq_principals_name UNIQUE ( name )
 );
CREATE TABLE resourceSetMembers (
        ID                   INTEGER NOT NULL  PRIMARY KEY  ,
        memberID             INT NOT NULL    ,
        setID                INT     ,
        FOREIGN KEY ( memberID ) REFERENCES resources( ID ) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY ( setID ) REFERENCES resourceSets( ID ) ON DELETE CASCADE ON UPDATE CASCADE
 ) ;
CREATE UNIQUE INDEX unq_rsmmemberID ON resourceSetMembers ( memberID,setID );
CREATE TABLE resourceSets (
        ID                   INTEGER  PRIMARY KEY  ,
        setName              TEXT NOT NULL    ,
        CONSTRAINT unq_resourceSets_setName UNIQUE ( setName )
 );
CREATE TABLE resources (
        ID                   INTEGER PRIMARY KEY  ,
        name                 TEXT NOT NULL    ,
        pattern              TEXT NOT NULL    ,
        CONSTRAINT unq_resources_name UNIQUE ( name )
 );
CREATE TABLE actionSetMembers (
        ID                   INTEGER NOT NULL  PRIMARY KEY  ,
        memberID             INT NOT NULL    ,
        setID                INT     ,
        FOREIGN KEY ( setID ) REFERENCES actionSets( ID ) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY ( memberID ) REFERENCES actions( ID ) ON DELETE CASCADE ON UPDATE CASCADE
 ) ;
CREATE UNIQUE INDEX unq_asmMemberSet ON actionSetMembers ( memberID, setID );
CREATE TABLE actionSets (
        ID                   INTEGER PRIMARY KEY  ,
        setName              TEXT NOT NULL    ,
        CONSTRAINT unq_permSets_setName UNIQUE ( setName )
 );
CREATE TABLE actions (
        ID                   INTEGER PRIMARY KEY  ,
        service              TEXT     ,
        permission           TEXT
 );
CREATE UNIQUE INDEX unq_action ON actions(service, permission );
CREATE VIEW actionSetsView as select setName,service,permission from actionSetMembers asm join actions a on asm.memberID=a.id join actionSets aSets on asm.setID=aSets.ID
/* actionSetsView(setName,service,permission) */;
CREATE VIEW resourceSetsView as select setName,name,pattern from resourceSetMembers rsm join resources r on rsm.memberID=r.id join resourceSets rSets on rsm.setID=rSets.ID
/* resourceSetsView(setName,name,pattern) */;
CREATE VIEW principalSetsView as select setName,name,pattern from principalSetMembers psm join principals p on psm.memberID=p.id join principalSets pSets on psm.setID=pSets.ID
/* principalSetsView(setName,name,pattern) */;
CREATE VIEW policySetsView as select psets.setName,p.sid,p.effect,aset.setName as action, rset.setName as resource, prset.setName as principal from policySetMembers psm join policies p on psm.memberID=p.id join policySets psets on psm.setID=psets.ID join actionSets aset on p.action=aset.ID join resourceSets rset on p.resource=rset.ID left join principalSets prset on p.principal=prset.ID
/* policySetsView(setName,sid,effect,"action",resource,principal) */;
