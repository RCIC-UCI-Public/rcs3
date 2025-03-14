## This builds the RCS3 AWS Permissions Database
# I. Add all actions
awspolicy.py add action athena getDataCatalog
awspolicy.py add action athena getQueryExecution
awspolicy.py add action athena startQueryExecution
awspolicy.py add action athena stopQueryExecution
awspolicy.py add action cloudwatch DeleteAlarms
awspolicy.py add action cloudwatch DescribeAlarms
awspolicy.py add action cloudwatch GetMetricData
awspolicy.py add action cloudwatch PutMetricAlarm
awspolicy.py add action cloudwatch PutMetricData
awspolicy.py add action dynamodb GetItem
awspolicy.py add action dynamodb PutItem
awspolicy.py add action dynamodb UpdateItem
awspolicy.py add action glue BatchCreatePartition
awspolicy.py add action glue BatchDeletePartition
awspolicy.py add action glue BatchDeleteTable
awspolicy.py add action glue BatchGetPartition
awspolicy.py add action glue CreateDatabase
awspolicy.py add action glue CreatePartition
awspolicy.py add action glue CreateTable
awspolicy.py add action glue DeleteDatabase
awspolicy.py add action glue DeletePartition
awspolicy.py add action glue DeleteTable
awspolicy.py add action glue GetDatabase
awspolicy.py add action glue GetDatabases
awspolicy.py add action glue GetPartition
awspolicy.py add action glue GetPartitions
awspolicy.py add action glue GetTable
awspolicy.py add action glue GetTables
awspolicy.py add action glue UpdateDatabase
awspolicy.py add action glue UpdatePartition
awspolicy.py add action glue UpdateTable
awspolicy.py add action iam CreateAccessKey
awspolicy.py add action iam DeleteAccessKey
awspolicy.py add action iam ListAccessKeys
awspolicy.py add action iam ListUsers
awspolicy.py add action iam passRole
awspolicy.py add action lambda InvokeFunction
awspolicy.py add action logs CreateLogGroup
awspolicy.py add action logs CreateLogStream
awspolicy.py add action logs FilterLogEvents
awspolicy.py add action logs GetLogEvents
awspolicy.py add action logs GetLogRecord
awspolicy.py add action logs GetQueryResults
awspolicy.py add action logs PutLogEvents
awspolicy.py add action logs StartQuery
awspolicy.py add action logs StopQuery
awspolicy.py add action s3 '*'
awspolicy.py add action s3 AbortMultipartUpload
awspolicy.py add action s3 BypassGovernanceRetention
awspolicy.py add action s3 CreateAccessPoint
awspolicy.py add action s3 CreateAccessPointForObjectLambda
awspolicy.py add action s3 CreateBucket
awspolicy.py add action s3 CreateJob
awspolicy.py add action s3 CreateMultiRegionAccessPoint
awspolicy.py add action s3 DeleteBucket
awspolicy.py add action s3 DeleteBucketPolicy
awspolicy.py add action s3 DeleteObject
awspolicy.py add action s3 DeleteObjectVersion
awspolicy.py add action s3 DescribeJob
awspolicy.py add action s3 GetAccountPublicAccessBlock
awspolicy.py add action s3 GetBucketAcl
awspolicy.py add action s3 GetBucketLocation
awspolicy.py add action s3 GetBucketLogging
awspolicy.py add action s3 GetBucketNotification
awspolicy.py add action s3 GetBucketObjectLockConfiguration
awspolicy.py add action s3 GetBucketPolicy
awspolicy.py add action s3 GetBucketPolicyStatus
awspolicy.py add action s3 GetBucketPublicAccessBlock
awspolicy.py add action s3 GetBucketVersioning
awspolicy.py add action s3 GetEncryptionConfiguration
awspolicy.py add action s3 GetLifecycleConfiguration
awspolicy.py add action s3 GetObject
awspolicy.py add action s3 GetObjectAcl
awspolicy.py add action s3 GetObjectAttributes
awspolicy.py add action s3 GetObjectRetention
awspolicy.py add action s3 GetObjectVersion
awspolicy.py add action s3 GetObjectVersionAcl
awspolicy.py add action s3 GetObjectVersionAttributes
awspolicy.py add action s3 GetObjectVersionTagging
awspolicy.py add action s3 ListAllMyBuckets
awspolicy.py add action s3 ListBucket
awspolicy.py add action s3 ListBucketMultipartUploads
awspolicy.py add action s3 ListBucketVersions
awspolicy.py add action s3 ListJobs
awspolicy.py add action s3 ListMultipartUploadParts
awspolicy.py add action s3 PutBucketAcl
awspolicy.py add action s3 PutObject
awspolicy.py add action s3 PutObjectAcl
awspolicy.py add action s3 RestoreObject
awspolicy.py add action s3 UpdateJobPriority
awspolicy.py add action s3 UpdateJobStatus
awspolicy.py add action sns GetTopicAttributes
awspolicy.py add action sns ListTopics
awspolicy.py add action sns Publish
awspolicy.py add action states StartExecution
awspolicy.py add action states StartSyncExecution
awspolicy.py add action sts AssumeRole

## II. Create Action Groups

awspolicy.py addSet action athenaExecution
awspolicy.py addToSet action athenaExecution athena getDataCatalog
awspolicy.py addToSet action athenaExecution athena getQueryExecution
awspolicy.py addToSet action athenaExecution athena startQueryExecution
awspolicy.py addToSet action athenaExecution athena stopQueryExecution


awspolicy.py addSet action cloudwatchAlarms 
awspolicy.py addToSet action cloudwatchAlarms cloudwatch DeleteAlarms
awspolicy.py addToSet action cloudwatchAlarms cloudwatch DescribeAlarms
awspolicy.py addToSet action cloudwatchAlarms cloudwatch GetMetricData
awspolicy.py addToSet action cloudwatchAlarms cloudwatch PutMetricAlarm

awspolicy.py addSet action cloudwatchPutMetric 
awspolicy.py addToSet action cloudwatchPutMetric cloudwatch PutMetricData

awspolicy.py addSet action dynamoDBItems
awspolicy.py addToSet action dynamoDBItems dynamodb GetItem
awspolicy.py addToSet action dynamoDBItems dynamodb PutItem
awspolicy.py addToSet action dynamoDBItems dynamodb UpdateItem

awspolicy.py addSet action gluePermissions 
awspolicy.py addToSet action gluePermissions glue BatchCreatePartition
awspolicy.py addToSet action gluePermissions glue BatchDeletePartition
awspolicy.py addToSet action gluePermissions glue BatchDeleteTable
awspolicy.py addToSet action gluePermissions glue BatchGetPartition
awspolicy.py addToSet action gluePermissions glue CreateDatabase 
awspolicy.py addToSet action gluePermissions glue CreatePartition
awspolicy.py addToSet action gluePermissions glue CreateTable
awspolicy.py addToSet action gluePermissions glue DeleteDatabase
awspolicy.py addToSet action gluePermissions glue DeletePartition
awspolicy.py addToSet action gluePermissions glue DeleteTable
awspolicy.py addToSet action gluePermissions glue GetDatabase
awspolicy.py addToSet action gluePermissions glue GetDatabases
awspolicy.py addToSet action gluePermissions glue GetPartition
awspolicy.py addToSet action gluePermissions glue GetPartitions
awspolicy.py addToSet action gluePermissions glue GetTable
awspolicy.py addToSet action gluePermissions glue GetTables
awspolicy.py addToSet action gluePermissions glue UpdateDatabase
awspolicy.py addToSet action gluePermissions glue UpdatePartition
awspolicy.py addToSet action gluePermissions glue UpdateTable


awspolicy.py addSet action updateAccessKey 
awspolicy.py addToSet action updateAccessKey iam CreateAccessKey
awspolicy.py addToSet action updateAccessKey iam DeleteAccessKey
awspolicy.py addToSet action updateAccessKey iam ListAccessKeys

awspolicy.py addSet action listUserKeys
awspolicy.py addToSet action listUserKeys iam ListAccessKeys
awspolicy.py addToSet action listUserKeys iam ListUsers

awspolicy.py addSet action iamPassRole
awspolicy.py addToSet action iamPassRole iam passRole

awspolicy.py addSet action lambdaInvoke 
awspolicy.py addToSet action lambdaInvoke lambda InvokeFunction

awspolicy.py addSet action createLogGroup
awspolicy.py addToSet action createLogGroup logs CreateLogGroup

awspolicy.py addSet action putLogEvents 
awspolicy.py addToSet action putLogEvents logs CreateLogStream
awspolicy.py addToSet action putLogEvents logs PutLogEvents

awspolicy.py addSet action processLogEvents 
awspolicy.py addToSet action processLogEvents logs FilterLogEvents
awspolicy.py addToSet action processLogEvents logs GetLogEvents
awspolicy.py addToSet action processLogEvents logs GetLogRecord
awspolicy.py addToSet action processLogEvents logs GetQueryResults
awspolicy.py addToSet action processLogEvents logs StartQuery

awspolicy.py addSet action stopLogQuery 
awspolicy.py addToSet action stopLogQuery logs StopQuery

awspolicy.py addSet action s3Any
awspolicy.py addToSet action s3Any s3 '*'

awspolicy.py addSet action s3BatchRestore
awspolicy.py addToSet action s3BatchRestore s3 AbortMultipartUpload
awspolicy.py addToSet action s3BatchRestore s3 CreateJob
awspolicy.py addToSet action s3BatchRestore s3 DeleteObject
awspolicy.py addToSet action s3BatchRestore s3 DescribeJob
awspolicy.py addToSet action s3BatchRestore s3 GetAccountPublicAccessBlock
awspolicy.py addToSet action s3BatchRestore s3 GetBucketAcl
awspolicy.py addToSet action s3BatchRestore s3 GetBucketLocation
awspolicy.py addToSet action s3BatchRestore s3 GetBucketLogging
awspolicy.py addToSet action s3BatchRestore s3 GetBucketNotification
awspolicy.py addToSet action s3BatchRestore s3 GetBucketObjectLockConfiguration
awspolicy.py addToSet action s3BatchRestore s3 GetBucketPolicy
awspolicy.py addToSet action s3BatchRestore s3 GetBucketPolicyStatus
awspolicy.py addToSet action s3BatchRestore s3 GetBucketPublicAccessBlock
awspolicy.py addToSet action s3BatchRestore s3 GetBucketVersioning
awspolicy.py addToSet action s3BatchRestore s3 GetEncryptionConfiguration
awspolicy.py addToSet action s3BatchRestore s3 GetLifecycleConfiguration
awspolicy.py addToSet action s3BatchRestore s3 GetObject
awspolicy.py addToSet action s3BatchRestore s3 GetObjectAcl
awspolicy.py addToSet action s3BatchRestore s3 GetObjectAttributes
awspolicy.py addToSet action s3BatchRestore s3 GetObjectRetention
awspolicy.py addToSet action s3BatchRestore s3 GetObjectVersion
awspolicy.py addToSet action s3BatchRestore s3 GetObjectVersionAcl
awspolicy.py addToSet action s3BatchRestore s3 GetObjectVersionAttributes
awspolicy.py addToSet action s3BatchRestore s3 GetObjectVersionTagging
awspolicy.py addToSet action s3BatchRestore s3 ListBucket
awspolicy.py addToSet action s3BatchRestore s3 ListBucketMultipartUploads
awspolicy.py addToSet action s3BatchRestore s3 ListBucketVersions
awspolicy.py addToSet action s3BatchRestore s3 ListJobs
awspolicy.py addToSet action s3BatchRestore s3 ListMultipartUploadParts
awspolicy.py addToSet action s3BatchRestore s3 PutObject
awspolicy.py addToSet action s3BatchRestore s3 PutObjectAcl

awspolicy.py addSet action backupUserPermissions 
awspolicy.py addToSet action backupUserPermissions s3 AbortMultipartUpload
awspolicy.py addToSet action backupUserPermissions s3 DeleteObject
awspolicy.py addToSet action backupUserPermissions s3 GetBucketAcl
awspolicy.py addToSet action backupUserPermissions s3 GetBucketLocation
awspolicy.py addToSet action backupUserPermissions s3 GetBucketLogging
awspolicy.py addToSet action backupUserPermissions s3 GetBucketNotification
awspolicy.py addToSet action backupUserPermissions s3 GetBucketObjectLockConfiguration
awspolicy.py addToSet action backupUserPermissions s3 GetBucketPolicy
awspolicy.py addToSet action backupUserPermissions s3 GetBucketPolicyStatus
awspolicy.py addToSet action backupUserPermissions s3 GetBucketVersioning
awspolicy.py addToSet action backupUserPermissions s3 GetEncryptionConfiguration
awspolicy.py addToSet action backupUserPermissions s3 GetLifecycleConfiguration
awspolicy.py addToSet action backupUserPermissions s3 GetObject
awspolicy.py addToSet action backupUserPermissions s3 GetObjectAcl
awspolicy.py addToSet action backupUserPermissions s3 GetObjectAttributes
awspolicy.py addToSet action backupUserPermissions s3 GetObjectRetention
awspolicy.py addToSet action backupUserPermissions s3 GetObjectVersion
awspolicy.py addToSet action backupUserPermissions s3 GetObjectVersionAcl
awspolicy.py addToSet action backupUserPermissions s3 GetObjectVersionAttributes
awspolicy.py addToSet action backupUserPermissions s3 GetObjectVersionTagging
awspolicy.py addToSet action backupUserPermissions s3 ListBucket
awspolicy.py addToSet action backupUserPermissions s3 ListBucketMultipartUploads
awspolicy.py addToSet action backupUserPermissions s3 ListBucketVersions
awspolicy.py addToSet action backupUserPermissions s3 ListMultipartUploadParts
awspolicy.py addToSet action backupUserPermissions s3 PutObject
awspolicy.py addToSet action backupUserPermissions s3 PutObjectAcl


awspolicy.py addSet action limitedS3Permssions
awspolicy.py addToSet action limitedS3Permissions s3 AbortMultipartUpload
awspolicy.py addToSet action limitedS3Permissions s3 GetBucketLocation
awspolicy.py addToSet action limitedS3Permissions s3 GetObject
awspolicy.py addToSet action limitedS3Permissions s3 ListBucket
awspolicy.py addToSet action limitedS3Permissions s3 ListBucketMultipartUploads
awspolicy.py addToSet action limitedS3Permissions s3 ListMultipartUploadParts

awspolicy.py addSet action dangerousS3Permissions
awspolicy.py addToSet action dangerousS3Permissions s3 BypassGovernanceRetention
awspolicy.py addToSet action dangerousS3Permissions s3 CreateAccessPoint
awspolicy.py addToSet action dangerousS3Permissions s3 CreateAccessPointForObjectLambda
awspolicy.py addToSet action dangerousS3Permissions s3 CreateBucket
awspolicy.py addToSet action dangerousS3Permissions s3 CreateMultiRegionAccessPoint
awspolicy.py addToSet action dangerousS3Permissions s3 DeleteBucket
awspolicy.py addToSet action dangerousS3Permissions s3 DeleteBucketPolicy
awspolicy.py addToSet action dangerousS3Permissions s3 DeleteObjectVersion
awspolicy.py addToSet action dangerousS3Permissions s3 PutBucketAcl

awspolicy.py addSet action bypassGovernance
awspolicy.py addToSet action bypassGovernance s3 BypassGovernanceRetention

awspolicy.py addSet action s3BatchJobs 
awspolicy.py addToSet action s3BatchJobs s3 CreateJob
awspolicy.py addToSet action s3BatchJobs s3 DescribeJob
awspolicy.py addToSet action s3BatchJobs s3 ListJobs
awspolicy.py addToSet action s3BatchJobs s3 UpdateJobPriority
awspolicy.py addToSet action s3BatchJobs s3 UpdateJobStatus

awspolicy.py addSet action deleteBucket 
awspolicy.py addToSet action deleteBucket s3 DeleteBucket

awspolicy.py addSet action s3ListPutDeleteObjects 
awspolicy.py addToSet action s3PutDeleteObjects s3 DeleteObject
awspolicy.py addToSet action s3PutDeleteObjects s3 GetObject
awspolicy.py addToSet action s3PutDeleteObjects s3 ListBucket
awspolicy.py addToSet action s3PutDeleteObjects s3 PutObject

awspolicy.py addSet action s3GetDeleteObjects 
awspolicy.py addToSet action s3GetDeleteObjects s3 DeleteObject
awspolicy.py addToSet action s3GetDeleteObjects s3 GetObject

awspolicy.py addSet action listS3BatchJobs 
awspolicy.py addToSet action listS3BatchJobs s3 DescribeJob
awspolicy.py addToSet action listS3BatchJobs s3 ListJobs

awspolicy.py addSet action readBucketAndAttributes 
awspolicy.py addToSet action readBucketAndAttributes s3 GetAccountPublicAccessBlock
awspolicy.py addToSet action readBucketAndAttributes s3 GetBucketAcl
awspolicy.py addToSet action readBucketAndAttributes s3 GetBucketLocation
awspolicy.py addToSet action readBucketAndAttributes s3 GetBucketLogging
awspolicy.py addToSet action readBucketAndAttributes s3 GetBucketNotification
awspolicy.py addToSet action readBucketAndAttributes s3 GetBucketPolicy
awspolicy.py addToSet action readBucketAndAttributes s3 GetBucketPolicyStatus
awspolicy.py addToSet action readBucketAndAttributes s3 GetBucketPublicAccessBlock
awspolicy.py addToSet action readBucketAndAttributes s3 GetEncryptionConfiguration
awspolicy.py addToSet action readBucketAndAttributes s3 GetObject
awspolicy.py addToSet action readBucketAndAttributes s3 GetObjectAcl
awspolicy.py addToSet action readBucketAndAttributes s3 GetObjectAttributes
awspolicy.py addToSet action readBucketAndAttributes s3 ListBucket

awspolicy.py addSet action getObjectVersion 
awspolicy.py addToSet action getObjectVersion s3 GetObject
awspolicy.py addToSet action getObjectVersion s3 GetObjectVersion
awspolicy.py addToSet action getObjectVersion s3 ListBucket

awspolicy.py addSet action getPutObjectVersion 
awspolicy.py addToSet action getPutObjectVersion s3 GetObject
awspolicy.py addToSet action getPutObjectVersion s3 GetObjectVersion
awspolicy.py addToSet action getPutObjectVersion s3 PutObject

awspolicy.py addSet action getObject
awspolicy.py addToSet action getObject s3 GetObject

awspolicy.py addSet action listAllBuckets 
awspolicy.py addToSet action listAllBuckets s3 ListAllMyBuckets

awspolicy.py addSet action listBucket
awspolicy.py addToSet action listBucket s3 ListBucket

awspolicy.py addSet action putObject
awspolicy.py addToSet action putObject s3 PutObject

awspolicy.py addSet action restoreObject
awspolicy.py addToSet action restoreObject s3 RestoreObject

awspolicy.py addSet action snsListAndPublish
awspolicy.py addToSet action snsListAndPublish sns GetTopicAttributes
awspolicy.py addToSet action snsListAndPublish sns ListTopics
awspolicy.py addToSet action snsListAndPublish sns Publish

awspolicy.py addSet action snsListTopics
awspolicy.py addToSet action snsListTopics sns ListTopics

awspolicy.py addSet action snsPublish
awspolicy.py addToSet action snsPublish sns Publish

awspolicy.py addSet action sfnExecution
awspolicy.py addToSet action sfnExecution states StartExecution
awspolicy.py addToSet action sfnExecution states StartSyncExecution

awspolicy.py addSet action stsAssumeRole
awspolicy.py addToSet action stsAssumeRole sts AssumeRole

## Resources
awspolicy.py add resource any '*'
awspolicy.py add resource athenaDatacatalog 'arn:aws:athena:{{REGION}}:{{ACCOUNT}}:datacatalog/*'
awspolicy.py add resource athenaWorkgroup 'arn:aws:athena:{{REGION}}:{{ACCOUNT}}:workgroup/rcs3'
awspolicy.py add resource dynamodbTable 'arn:aws:dynamodb:{{REGION}}:{{ACCOUNT}}:table/*{{BUCKET_POSTFIX}}'
awspolicy.py add resource glueCatalog 'arn:aws:glue:{{REGION}}:{{ACCOUNT}}:catalog'
awspolicy.py add resource glueDatabase 'arn:aws:glue:{{REGION}}:{{ACCOUNT}}:database/*'
awspolicy.py add resource glueTable 'arn:aws:glue:{{REGION}}:{{ACCOUNT}}:table/*'
awspolicy.py add resource glueUserDefinedFunction 'arn:aws:glue:{{REGION}}:{{ACCOUNT}}:userDefinedFunction/*'
awspolicy.py add resource iamRestoreBatchPermsRole 'arn:aws:iam::{{ACCOUNT}}:role/{{OWNER}}-{{SYSTEM}}-restore-s3batch-perms-role'
awspolicy.py add resource backupServiceAccount 'arn:aws:iam::{{ACCOUNT}}:user/{{OWNER}}-{{SYSTEM}}-sa'
awspolicy.py add resource lambdaFunction 'arn:aws:lambda:{{REGION}}:{{ACCOUNT}}:function:{{FUNCTION}}'
awspolicy.py add resource lambdaFunctionMethods 'arn:aws:lambda:{{REGION}}:{{ACCOUNT}}:function:{{FUNCTION}}:*'
awspolicy.py add resource lambdaCalcUploadBytes 'arn:aws:lambda:{{REGION}}:{{ACCOUNT}}:function:calcUploadBytes'
awspolicy.py add resource lambdaCalcUploadBytesMethods 'arn:aws:lambda:{{REGION}}:{{ACCOUNT}}:function:calcUploadBytes:*'
awspolicy.py add resource lambdaKeyAgeMetric 'arn:aws:lambda:{{REGION}}:{{ACCOUNT}}:function:keyAgeMetric'
awspolicy.py add resource lambdaKeyAgeMetricMethods 'arn:aws:lambda:{{REGION}}:{{ACCOUNT}}:function:keyAgeMetric:*'
awspolicy.py add resource lambdaCreateAthenaQueries 'arn:aws:lambda:{{REGION}}:{{ACCOUNT}}:function:createAthenaQueries'
awspolicy.py add resource lambdaCreateAthenaQueriesMethods 'arn:aws:lambda:{{REGION}}:{{ACCOUNT}}:function:createAthenaQueries:*'
awspolicy.py add resource lambdaCreateS3BatchInput 'arn:aws:lambda:{{REGION}}:{{ACCOUNT}}:function:createS3BatchInput'
awspolicy.py add resource lambdaCreateS3BatchInputMethods 'arn:aws:lambda:{{REGION}}:{{ACCOUNT}}:function:createS3BatchInput:*'
awspolicy.py add resource lambdaPollCreateJobStatus 'arn:aws:lambda:{{REGION}}:{{ACCOUNT}}:function:pollCreateJobStatus'
awspolicy.py add resource lambdaPollCreateJobStatusMethods 'arn:aws:lambda:{{REGION}}:{{ACCOUNT}}:function:pollCreateJobStatus:*'
awspolicy.py add resource regionAccountAny 'arn:aws:logs:{{REGION}}:{{ACCOUNT}}:*'
awspolicy.py add resource loggroupCreateAthenaQueries 'arn:aws:logs:{{REGION}}:{{ACCOUNT}}:log-group:/aws/lambda/createAthenaQueries:*'
awspolicy.py add resource loggroupCreateS3BatchInput 'arn:aws:logs:{{REGION}}:{{ACCOUNT}}:log-group:/aws/lambda/createS3BatchInput:*'
awspolicy.py add resource loggroupPollCreateJobStatus 'arn:aws:logs:{{REGION}}:{{ACCOUNT}}:log-group:/aws/lambda/pollCreateJobStatus:*'
awspolicy.py add resource loggroupPostCloudwatchMetrics 'arn:aws:logs:{{REGION}}:{{ACCOUNT}}:log-group:/aws/lambda/postCloudwatchMetrics:*'
awspolicy.py add resource loggroupPrepDynamoImport 'arn:aws:logs:{{REGION}}:{{ACCOUNT}}:log-group:/aws/lambda/prepDynamoImport:*'
awspolicy.py add resource loggroupQueryS3Restore 'arn:aws:logs:{{REGION}}:{{ACCOUNT}}:log-group:/aws/lambda/queryS3Restore:*'
awspolicy.py add resource loggroupUpdateDynamodb 'arn:aws:logs:{{REGION}}:{{ACCOUNT}}:log-group:/aws/lambda/updateDynamodb:*'
awspolicy.py add resource loggroupCloudtrails 'arn:aws:logs:{{REGION}}x:{{ACCOUNT}}:log-group:aws-cloudtrail-logs-xiangmix-cncm2:*'
awspolicy.py add resource inventoryPrefix 'arn:aws:s3:::*{{INVENTORY_POSTFIX}}'
awspolicy.py add resource inventoryRCS3Path 'arn:aws:s3:::*{{INVENTORY_POSTFIX}}/rcs3/*'
awspolicy.py add resource reports 'arn:aws:s3:::{{REPORTS}}'
awspolicy.py add resource reportsContents 'arn:aws:s3:::{{REPORTS}}/*'
awspolicy.py add resource reportsOwner 'arn:aws:s3:::{{REPORTS}}/{{OWNER}}/*'
awspolicy.py add resource backupBucketPrefix 'arn:aws:s3:::{{OWNER}}-{{SYSTEM}}-{{BUCKET_POSTFIX}}'
awspolicy.py add resource backupBucketContents 'arn:aws:s3:::{{OWNER}}-{{SYSTEM}}-{{BUCKET_POSTFIX}}/*'
awspolicy.py add resource inventoryBucketPrefix 'arn:aws:s3:::{{OWNER}}-{{SYSTEM}}-{{INVENTORY_POSTFIX}}'
awspolicy.py add resource inventoryBucketPrefixContents 'arn:aws:s3:::{{OWNER}}-{{SYSTEM}}-{{INVENTORY_POSTFIX}}/*'
awspolicy.py add resource inventoryBucketRCS3Path 'arn:aws:s3:::{{OWNER}}-{{SYSTEM}}-{{INVENTORY_POSTFIX}}/rcs3/*'
awspolicy.py add resource snsRegionAccountAny 'arn:aws:sns:{{REGION}}:{{ACCOUNT}}:*'
awspolicy.py add resource snsOwnerNotify 'arn:aws:sns:{{REGION}}:{{ACCOUNT}}:{{OWNER}}-{{SYSTEM}}-{{OWNER_NOTIFY}}'
awspolicy.py add resource sfnFullMonty 'arn:aws:states:{{REGION}}:{{ACCOUNT}}:stateMachine:{{OWNER}}-{{SYSTEM}}-sfn-full-monty'


## Resource Groups

awspolicy.py addSet resource anyResource
awspolicy.py addToSet resource anyResource any

awspolicy.py addSet resource athenaResources
awspolicy.py addToSet resource athenaResources athenaDatacatalog
awspolicy.py addToSet resource athenaResources athenaWorkgroup

awspolicy.py addSet resource dynamodbBucket
awspolicy.py addToSet resource dynamodbBucket dynamodbTable

awspolicy.py addSet resource glueResources
awspolicy.py addToSet resource glueResources glueCatalog
awspolicy.py addToSet resource glueResources glueDatabase
awspolicy.py addToSet resource glueResources glueTable
awspolicy.py addToSet resource glueResources glueUserDefinedFunction

awspolicy.py addSet resource iamS3batchPermsRole
awspolicy.py addToSet resource iamS3batchPermsRole iamRestoreBatchPermsRole

awspolicy.py addSet resource backupServiceAccount
awspolicy.py addToSet resource backupServiceAccount backupServiceAccount 

awspolicy.py addSet resource lambdaFunction
awspolicy.py addToSet resource lambdaFunction lambdaFunction
awspolicy.py addToSet resource lambdaFunction lambdaFunctionMethods

awspolicy.py addSet resource lambdaCalcUploadBytes
awspolicy.py addToSet resource lambdaCalcUploadBytes lambdaCalcUploadBytes
awspolicy.py addToSet resource lambdaCalcUploadBytes lambdaCalcUploadBytesMethods

awspolicy.py addSet resource lambdaKeyAgeMetric
awspolicy.py addToSet resource lambdaKeyAgeMetric lambdaKeyAgeMetric
awspolicy.py addToSet resource lambdaKeyAgeMetric lambdaKeyAgeMetricMethods

awspolicy.py addSet resource lambdaCreateAthenaQueries
awspolicy.py addToSet resource lambdaCreateAthenaQueries lambdaCreateAthenaQueries
awspolicy.py addToSet resource lambdaCreateAthenaQueries lambdaCreateAthenaQueriesMethods

awspolicy.py addSet resource lambdaAthenaBatch
awspolicy.py addToSet resource lambdaAthenaBatch lambdaCreateAthenaQueries
awspolicy.py addToSet resource lambdaAthenaBatch lambdaCreateAthenaQueriesMethods
awspolicy.py addToSet resource lambdaAthenaBatch lambdaCreateS3BatchInput
awspolicy.py addToSet resource lambdaAthenaBatch lambdaCreateS3BatchInputMethods
awspolicy.py addToSet resource lambdaAthenaBatch lambdaPollCreateJobStatus
awspolicy.py addToSet resource lambdaAthenaBatch lambdaPollCreateJobStatusMethods

awspolicy.py addSet resource regionAccountAny
awspolicy.py addToSet resource regionAccountAny regionAccountAny

awspolicy.py addSet resource restoreLoggroups
awspolicy.py addToSet resource restoreLoggroups loggroupCreateAthenaQueries
awspolicy.py addToSet resource restoreLoggroups loggroupCreateS3BatchInput
awspolicy.py addToSet resource restoreLoggroups loggroupPollCreateJobStatus

awspolicy.py addSet resource loggroupCreateAthenaQueries
awspolicy.py addToSet resource loggroupCreateAthenaQueries loggroupCreateAthenaQueries

awspolicy.py addSet resource loggroupCreateS3BatchInput
awspolicy.py addToSet resource loggroupCreateS3BatchInput loggroupCreateS3BatchInput

awspolicy.py addSet resource loggroupPollCreateJobStatus
awspolicy.py addToSet resource loggroupPollCreateJobStatus loggroupPollCreateJobStatus

awspolicy.py addSet resource loggroupPostCloudwatchMetrics
awspolicy.py addToSet resource loggroupPostCloudwatchMetrics loggroupPostCloudwatchMetrics

awspolicy.py addSet resource loggroupPrepDynamoImport
awspolicy.py addToSet resource loggroupPrepDynamoImport loggroupPrepDynamoImport

awspolicy.py addSet resource loggroupQueryS3Restore
awspolicy.py addToSet resource loggroupQueryS3Restore loggroupQueryS3Restore

awspolicy.py addSet resource loggroupUpdateDynamodb
awspolicy.py addToSet resource loggroupUpdateDynamodb loggroupUpdateDynamodb

awspolicy.py addSet resource loggroupCloudtrails
awspolicy.py addToSet resource loggroupCloudtrails loggroupCloudtrails

awspolicy.py addSet resource inventoryPrefix
awspolicy.py addToSet resource inventoryPrefix inventoryPrefix

awspolicy.py addSet resource inventoryRCS3Path
awspolicy.py addToSet resource inventoryRCS3Path inventoryRCS3Path

awspolicy.py addSet resource reports
awspolicy.py addToSet resource reports reports

awspolicy.py addSet resource reportsContents
awspolicy.py addToSet resource reportsContents reportsContents

awspolicy.py addSet resource reportsOwner
awspolicy.py addToSet resource reportsOwner reportsOwner

awspolicy.py addSet resource backupBucket
awspolicy.py addToSet resource backupBucket backupBucketPrefix
awspolicy.py addToSet resource backupBucket backupBucketContents

awspolicy.py addSet resource backupBucketPrefix
awspolicy.py addToSet resource backupBucketPrefix backupBucketPrefix

awspolicy.py addSet resource backupBucketContents
awspolicy.py addToSet resource backupBucketContents backupBucketContents

awspolicy.py addSet resource inventoryBucket
awspolicy.py addToSet resource inventoryBucket inventoryBucketPrefix
awspolicy.py addToSet resource inventoryBucket inventoryBucketPrefixContents

awspolicy.py addSet resource inventoryBucketContents
awspolicy.py addToSet resource inventoryBucketContents inventoryBucketPrefixContents

awspolicy.py addSet resource inventoryBucketRCS3Path
awspolicy.py addToSet resource inventoryBucketRCS3Path inventoryBucketRCS3Path

awspolicy.py addSet resource snsRegionAccountAny
awspolicy.py addToSet resource snsRegionAccountAny snsRegionAccountAny

awspolicy.py addSet resource snsOwnerNotify
awspolicy.py addToSet resource snsOwnerNotify snsOwnerNotify

awspolicy.py addSet resource sfnFullMonty
awspolicy.py addToSet resource sfnFullMonty sfnFullMonty

# Principals

awspolicy.py add principal serviceS3Batch '{"Service":"batchoperations.s3.amazonaws.com"}'
awspolicy.py add principal serviceLambda '{"Service":"lambda.amazonaws.com"}'
awspolicy.py add principal serviceAWS '{"Service":"s3.amazonaws.com"}'
awspolicy.py add principal serviceScheduler '{"Service":"scheduler.amazonaws.com"}'
awspolicy.py add principal serviceStates '{"Service":"states.amazonaws.com"}'

# Principal Sets
awspolicy.py addSet principal serviceS3Batch
awspolicy.py addToSet principal serviceS3Batch serviceS3Batch

awspolicy.py addSet principal serviceLambda
awspolicy.py addToSet principal serviceLambda serviceLambda

awspolicy.py addSet principal serviceAWS
awspolicy.py addToSet principal serviceAWS serviceAWS

awspolicy.py addSet principal serviceScheduler
awspolicy.py addToSet principal serviceAWS serviceScheduler

awspolicy.py addSet principal serviceStates
awspolicy.py addToSet principal serviceStates serviceStates

# Conditions
awspolicy.py add condition arnBackupBucket '{"ArnLike" : {"aws:SourceArn": "arn:aws:s3:::{{OWNER}}-{{SYSTEM}}-{{POSTFIX_BUCKET}}"} }'
awspolicy.py add condition equalsAccount '{"StringEquals" : {"aws:SourceAccount": "{{ACCOUNT}}"} }'
awspolicy.py add condition equalsAccountAndControl '{"StringEquals" :  {"aws:SourceAccount": "{{ACCOUNT}}", "s3:x-amz-acl": "bucket-owner-full-control"} }'
awspolicy.py add condition s3PrefixOwner '{"StringEquals" : {"s3:prefix": ["{{OWNER}}", "{{OWNER}}/"], "s3:delimiter": ["/"]} }'
awspolicy.py add condition IPRestrictions '{ "{{IP_RULE}}" : "{{IP_ADDRESSES}}" }'

# Condition Sets

awspolicy.py addSet condition arnBackupBucket
awspolicy.py addToSet condition arnBackupBucket arnBackupBucket

awspolicy.py addSet condition equalsAccountAndControl
awspolicy.py addToSet condition equalsAccountAndControl equalsAccountAndControl

awspolicy.py addSet condition equalsAccount
awspolicy.py addToSet condition equalsAccount equalsAccount

awspolicy.py addSet condition IPRestrictions
awspolicy.py addToSet condition IPRestrictions IPRestrictions

awspolicy.py addSet condition s3PrefixOwner
awspolicy.py addToSet condition s3PrefixOwner s3PrefixOwner

## Policies

## For template-policy2
awspolicy.py add policy writeBackupBucket Allow --actionSet backupUserPermissions --resourceSet backupBucket --conditionSet IPRestrictions 
awspolicy.py add policy readInventoryBucket Allow --actionSet readBucketAndAttributes --resourceSet inventoryBucket
awspolicy.py add policy denyDangerousOps Deny --actionSet dangerousS3Permissions --resourceSet anyResource
awspolicy.py add policy publishNotifications Allow --actionSet snsPublish --resourceSet snsOwnerNotify --conditionSet IPRestrictions
awspolicy.py add policy snsListTopics Allow --actionSet snsListTopics --resourceSet snsRegionAccountAny --conditionSet IPRestrictions
awspolicy.py add policy rotateAccessKey Allow --actionSet updateAccessKey --resourceSet backupServiceAccount --conditionSet IPRestrictions

## For keyAgeMetric-policy
awspolicy.py add policy listUsersAndKeys Allow --actionSet listUserKeys --resourceSet anyResource 
awspolicy.py add policy createLogGroup Allow --actionSet createLogGroup --resourceSet anyResource 
awspolicy.py add policy createLogStream Allow --actionSet putLogEvents --resourceSet anyResource 
awspolicy.py add policy publishMetrics Allow --actionSet cloudwatchPutMetric --resourceSet anyResource 


### Policy "JSON" files based upon defined policies above
# == template-policy2 ===
awspolicy.py addSet policy template-policy2
awspolicy.py addToSet policy template-policy2 writeBackupBucket
awspolicy.py addToSet policy template-policy2 readInventoryBucket
awspolicy.py addToSet policy template-policy2 denyDangerousOps
awspolicy.py addToSet policy template-policy2 publishNotifications
awspolicy.py addToSet policy template-policy2 snsListTopics 
awspolicy.py addToSet policy template-policy2 rotateAccessKey 


## == keyAgeMetric-policy ==
awspolicy.py addSet policy keyAgeMetric-policy 
awspolicy.py addToSet policy keyAgeMetric-policy listUsersAndKeys
awspolicy.py addToSet policy keyAgeMetric-policy createLogGroup
awspolicy.py addToSet policy keyAgeMetric-policy createLogStream
awspolicy.py addToSet policy keyAgeMetric-policy publishMetrics


