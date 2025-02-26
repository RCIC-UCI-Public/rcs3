insert into actions(service,permission) values('athena','getDataCatalog');
insert into actions(service,permission) values('athena','getQueryExecution');
insert into actions(service,permission) values('athena','startQueryExecution');
insert into actions(service,permission) values('athena','stopQueryExecution');
insert into actions(service,permission) values('cloudwatch','DeleteAlarms');
insert into actions(service,permission) values('cloudwatch','DescribeAlarms');
insert into actions(service,permission) values('cloudwatch','GetMetricData');
insert into actions(service,permission) values('cloudwatch','PutMetricAlarm');
insert into actions(service,permission) values('glue','BatchCreatePartition');
insert into actions(service,permission) values('glue','BatchDeletePartition');
insert into actions(service,permission) values('glue','BatchDeleteTable');
insert into actions(service,permission) values('glue','BatchGetPartition');
insert into actions(service,permission) values('glue','CreateDatabase');
insert into actions(service,permission) values('glue','CreatePartition');
insert into actions(service,permission) values('glue','CreateTable');
insert into actions(service,permission) values('glue','DeleteDatabase');
insert into actions(service,permission) values('glue','DeletePartition');
insert into actions(service,permission) values('glue','DeleteTable');
insert into actions(service,permission) values('glue','GetDatabase');
insert into actions(service,permission) values('glue','GetDatabases');
insert into actions(service,permission) values('glue','GetPartition');
insert into actions(service,permission) values('glue','GetPartitions');
insert into actions(service,permission) values('glue','GetTable');
insert into actions(service,permission) values('glue','GetTables');
insert into actions(service,permission) values('glue','UpdateDatabase');
insert into actions(service,permission) values('glue','UpdatePartition');
insert into actions(service,permission) values('glue','UpdateTable');
insert into actions(service,permission) values('iam','passRole');
insert into actions(service,permission) values('lambda','InvokeFunction');
insert into actions(service,permission) values('s3','AbortMultipartUpload');
insert into actions(service,permission) values('s3','CreateJob');
insert into actions(service,permission) values('s3','DeleteObject');
insert into actions(service,permission) values('s3','DescribeJob');
insert into actions(service,permission) values('s3','GetBucketLocation');
insert into actions(service,permission) values('s3','GetObject');
insert into actions(service,permission) values('s3','ListBucket');
insert into actions(service,permission) values('s3','ListBucketMultipartUploads');
insert into actions(service,permission) values('s3','ListJobs');
insert into actions(service,permission) values('s3','ListMultipartUploadParts');
insert into actions(service,permission) values('s3','PutObject');
insert into actions(service,permission) values('s3','UpdateJobPriority');
insert into actions(service,permission) values('s3','UpdateJobStatus');
insert into actions(service,permission) values('sns','GetTopicAttributes');
insert into actions(service,permission) values('sns','ListTopics');
insert into actions(service,permission) values('sns','Publish');
insert into actions(service,permission) values('states','StartExecution'); 
insert into actions(service,permission) values('states','StartSyncExecution');

insert into actionSets(setName) values('bucketList');
insert into actionSetMembers(memberID,setID) values((select ID from actions a where a.service='s3' and a.permission='GetObject'),(select ID from actionSets where actionSets.setName='bucketList'));
insert into actionSetMembers(memberID,setID) values((select ID from actions a where a.service='s3' and a.permission='GetBucketLocation'),(select ID from actionSets where actionSets.setName='bucketList'));
insert into actionSetMembers(memberID,setID) values((select ID from actions a where a.service='s3' and a.permission='ListBucket'),(select ID from actionSets where actionSets.setName='bucketList'));
insert into actionSetMembers(memberID,setID) values((select ID from actions a where a.service='s3' and a.permission='ListMultipartUploadParts'),(select ID from actionSets where actionSets.setName='bucketList'));
insert into actionSetMembers(memberID,setID) values((select ID from actions a where a.service='s3' and a.permission='ListBucketMultipartUploads'),(select ID from actionSets where actionSets.setName='bucketList'));
insert into actionSetMembers(memberID,setID) values((select ID from actions a where a.service='s3' and a.permission='AbortMultipartUpload'),(select ID from actionSets where actionSets.setName='bucketList'));

insert into actionSets(setname) values('writeObjects');
insert into actionSetMembers(memberID,setID) values((select ID from actions a where a.service='s3' and a.permission='ListBucket'),(select ID from actionSets where actionSets.setName='writeObjects'));
insert into actionSetMembers(memberID,setID) values((select ID from actions a where a.service='s3' and a.permission='GetObject'),(select ID from actionSets where actionSets.setName='writeObjects'));
insert into actionSetMembers(memberID,setID) values((select ID from actions a where a.service='s3' and a.permission='PutObject'),(select ID from actionSets where actionSets.setName='writeObjects'));
insert into actionSetMembers(memberID,setID) values((select ID from actions a where a.service='s3' and a.permission='DeleteObject'),(select ID from actionSets where actionSets.setName='writeObjects'));

insert into actionSets(setName) values('s3BatchSubmit');
insert into actionSetMembers(memberID,setID) values((select ID from actions a where a.service='s3' and a.permission='CreateJob'),(select ID from actionSets where actionSets.setName='s3BatchSubmit'));
insert into actionSetMembers(memberID,setID) values((select ID from actions a where a.service='s3' and a.permission='DescribeJob'),(select ID from actionSets where actionSets.setName='s3BatchSubmit'));
insert into actionSetMembers(memberID,setID) values((select ID from actions a where a.service='s3' and a.permission='ListJobs'),(select ID from actionSets where actionSets.setName='s3BatchSubmit'));
insert into actionSetMembers(memberID,setID) values((select ID from actions a where a.service='s3' and a.permission='UpdateJobPriority'),(select ID from actionSets where actionSets.setName='s3BatchSubmit'));
insert into actionSetMembers(memberID,setID) values((select ID from actions a where a.service='s3' and a.permission='UpdateJobStatus'),(select ID from actionSets where actionSets.setName='s3BatchSubmit'));

insert into actionSets(setName) values('athenaExecution');
insert into actionSetMembers(memberID,setID) values((select ID from actions a where a.service='athena' and a.permission='startQueryExecution'),(select ID from actionSets where actionSets.setName='athenaExecution'));
insert into actionSetMembers(memberID,setID) values((select ID from actions a where a.service='athena' and a.permission='stopQueryExecution'),(select ID from actionSets where actionSets.setName='athenaExecution'));
insert into actionSetMembers(memberID,setID) values((select ID from actions a where a.service='athena' and a.permission='getQueryExecution'),(select ID from actionSets where actionSets.setName='athenaExecution'));
insert into actionSetMembers(memberID,setID) values((select ID from actions a where a.service='athena' and a.permission='getDataCatalog'),(select ID from actionSets where actionSets.setName='athenaExecution'));


insert into resources(name,pattern) values('backupBucket','arn:aws:s3:::{{OWNER}}-{{SYSTEM}}-{{BACKUP_POSTFIX}}');
insert into resources(name,pattern) values('backupBucketComps','arn:aws:s3:::{{OWNER}}-{{SYSTEM}}-{{BACKUP_POSTFIX}}/*');
insert into resources(name,pattern) values('inventoryBucket','arn:aws:s3:::{{OWNER}}-{{SYSTEM}}-{{INVENTORY_POSTFIX}}');
insert into resources(name,pattern) values('inventoryBucketComps','arn:aws:s3:::{{OWNER}}-{{SYSTEM}}-{{INVENTORY_POSTFIX}}/*');
insert into resources(name,pattern) values('inventoryBucketRCS3Path','arn:aws:s3:::{{OWNER}}-{{SYSTEM}}-{{INVENTORY_POSTFIX}}/rcs3/*');
insert into resources(name,pattern) values('athenaWorkgroup','arn:aws:athena:{{REGION}:{{ACCOUNT}}:workgroup/rcs3');
insert into resources(name,pattern) values('athenaDatacatalog','arn:aws:athena:{{REGION}:{{ACCOUNT}}:datacatalog/*');
insert into resources(name,pattern) values('any','*');

insert into resourceSets(setName) values('backupBucket');
insert into resourceSets(setName) values('inventoryBucket');
insert into resourceSets(setName) values('inventoryBucketRCS3');
insert into resourceSets(setName) values('athenaWorkgroupCatalog');
insert into resourceSets(setName) values('any');

insert into resourceSetMembers(memberID,setID) values((select ID from resources r where r.name='backupBucket'),(select ID from resourceSets where resourceSets.setName='backupBucket'));
insert into resourceSetMembers(memberID,setID) values((select ID from resources r where r.name='backupBucketComps'),(select ID from resourceSets where resourceSets.setName='backupBucket'));
insert into resourceSetMembers(memberID,setID) values((select ID from resources r where r.name='inventoryBucket'),(select ID from resourceSets where resourceSets.setName='inventoryBucket'));
insert into resourceSetMembers(memberID,setID) values((select ID from resources r where r.name='inventoryBucketComps'),(select ID from resourceSets where resourceSets.setName='inventoryBucket'));
insert into resourceSetMembers(memberID,setID) values((select ID from resources r where r.name='inventoryBucketRCS3Path'),(select ID from resourceSets where resourceSets.setName='inventoryBucketRCS3'));
insert into resourceSetMembers(memberID,setID) values((select ID from resources r where r.name='any'),(select ID from resourceSets where resourceSets.setName='any'));

insert into resourceSetMembers(memberID,setID) values((select ID from resources r where r.name='athenaWorkgroup'),(select ID from resourceSets where resourceSets.setName='athenaWorkgroupCatalog'));
insert into resourceSetMembers(memberID,setID) values((select ID from resources r where r.name='athenaDatacatalog'),(select ID from resourceSets where resourceSets.setName='athenaWorkgroupCatalog'));

insert into policies(sid,action,resource,effect) values('primaryBucketList',(select ID from actionSets where setName='bucketList'),(select ID from resourceSets where setName='backupBucket'),'Allow');
insert into policies(sid,action,resource,effect) values('inventoryBucketList',(select ID from actionSets where setName='bucketList'),(select ID from resourceSets where setName='inventoryBucket'),'Allow');
insert into policies(sid,action,resource,effect) values('AllowWriteRCS3Path',(select ID from actionSets where setName='writeObjects'),(select ID from resourceSets where setName='inventoryBucketRCS3'),'Allow');
insert into policies(sid,action,resource,effect) values('AllowS3Batch',(select ID from actionSets where setName='s3BatchSubmit'),(select ID from resourceSets where setName='any'),'Allow');
insert into policies(sid,action,resource,effect) values('athenaAccess',(select ID from actionSets where setName='athenaExecution'),(select ID from resourceSets where setName='athenaWorkgroupCatalog'),'Allow');


insert into policySets(setName) values('restore-stepfunc-perms-policy');
insert into policySetMembers(memberID,setID) values((select ID from policies where sid='primaryBucketList'),(select ID from policySets where setName='restore-stepfunc-perms-policy'));
insert into policySetMembers(memberID,setID) values((select ID from policies where sid='inventoryBucketList'),(select ID from policySets where setName='restore-stepfunc-perms-policy'));
insert into policySetMembers(memberID,setID) values((select ID from policies where sid='AllowWriteRCS3Path'),(select ID from policySets where setName='restore-stepfunc-perms-policy'));
insert into policySetMembers(memberID,setID) values((select ID from policies where sid='AllowS3Batch'),(select ID from policySets where setName='restore-stepfunc-perms-policy'));
insert into policySetMembers(memberID,setID) values((select ID from policies where sid='athenaAccess'),(select ID from policySets where setName='restore-stepfunc-perms-policy'));

