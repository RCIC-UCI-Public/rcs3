#!/bin/bash -i
MYDIR=$(dirname $(realpath $0))
AWSPOLICY=$MYDIR/awspolicy.py

## This builds the RCS3 AWS Permissions Database
# I. Add all actions
$AWSPOLICY add action athena getDataCatalog
$AWSPOLICY add action athena getQueryExecution
$AWSPOLICY add action athena startQueryExecution
$AWSPOLICY add action athena stopQueryExecution
$AWSPOLICY add action cloudwatch DeleteAlarms
$AWSPOLICY add action cloudwatch DescribeAlarms
$AWSPOLICY add action cloudwatch GetMetricData
$AWSPOLICY add action cloudwatch PutMetricAlarm
$AWSPOLICY add action cloudwatch PutMetricData
$AWSPOLICY add action dynamodb GetItem
$AWSPOLICY add action dynamodb PutItem
$AWSPOLICY add action dynamodb UpdateItem
$AWSPOLICY add action glue BatchCreatePartition
$AWSPOLICY add action glue BatchDeletePartition
$AWSPOLICY add action glue BatchDeleteTable
$AWSPOLICY add action glue BatchGetPartition
$AWSPOLICY add action glue CreateDatabase
$AWSPOLICY add action glue CreatePartition
$AWSPOLICY add action glue CreateTable
$AWSPOLICY add action glue DeleteDatabase
$AWSPOLICY add action glue DeletePartition
$AWSPOLICY add action glue DeleteTable
$AWSPOLICY add action glue GetDatabase
$AWSPOLICY add action glue GetDatabases
$AWSPOLICY add action glue GetPartition
$AWSPOLICY add action glue GetPartitions
$AWSPOLICY add action glue GetTable
$AWSPOLICY add action glue GetTables
$AWSPOLICY add action glue UpdateDatabase
$AWSPOLICY add action glue UpdatePartition
$AWSPOLICY add action glue UpdateTable
$AWSPOLICY add action iam CreateAccessKey
$AWSPOLICY add action iam DeleteAccessKey
$AWSPOLICY add action iam ListAccessKeys
$AWSPOLICY add action iam ListUsers
$AWSPOLICY add action iam passRole
$AWSPOLICY add action lambda InvokeFunction
$AWSPOLICY add action logs CreateLogGroup
$AWSPOLICY add action logs CreateLogStream
$AWSPOLICY add action logs FilterLogEvents
$AWSPOLICY add action logs GetLogEvents
$AWSPOLICY add action logs GetLogRecord
$AWSPOLICY add action logs GetQueryResults
$AWSPOLICY add action logs PutLogEvents
$AWSPOLICY add action logs StartQuery
$AWSPOLICY add action logs StopQuery
$AWSPOLICY add action s3 '*'
$AWSPOLICY add action s3 AbortMultipartUpload
$AWSPOLICY add action s3 BypassGovernanceRetention
$AWSPOLICY add action s3 CreateAccessPoint
$AWSPOLICY add action s3 CreateAccessPointForObjectLambda
$AWSPOLICY add action s3 CreateBucket
$AWSPOLICY add action s3 CreateJob
$AWSPOLICY add action s3 CreateMultiRegionAccessPoint
$AWSPOLICY add action s3 DeleteBucket
$AWSPOLICY add action s3 DeleteBucketPolicy
$AWSPOLICY add action s3 DeleteObject
$AWSPOLICY add action s3 DeleteObjectVersion
$AWSPOLICY add action s3 DescribeJob
$AWSPOLICY add action s3 GetAccountPublicAccessBlock
$AWSPOLICY add action s3 GetBucketAcl
$AWSPOLICY add action s3 GetBucketLocation
$AWSPOLICY add action s3 GetBucketLogging
$AWSPOLICY add action s3 GetBucketNotification
$AWSPOLICY add action s3 GetBucketObjectLockConfiguration
$AWSPOLICY add action s3 GetBucketPolicy
$AWSPOLICY add action s3 GetBucketPolicyStatus
$AWSPOLICY add action s3 GetBucketPublicAccessBlock
$AWSPOLICY add action s3 GetBucketVersioning
$AWSPOLICY add action s3 GetEncryptionConfiguration
$AWSPOLICY add action s3 GetLifecycleConfiguration
$AWSPOLICY add action s3 GetObject
$AWSPOLICY add action s3 GetObjectAcl
$AWSPOLICY add action s3 GetObjectAttributes
$AWSPOLICY add action s3 GetObjectRetention
$AWSPOLICY add action s3 GetObjectVersion
$AWSPOLICY add action s3 GetObjectVersionAcl
$AWSPOLICY add action s3 GetObjectVersionAttributes
$AWSPOLICY add action s3 GetObjectVersionTagging
$AWSPOLICY add action s3 ListAllMyBuckets
$AWSPOLICY add action s3 ListBucket
$AWSPOLICY add action s3 ListBucketMultipartUploads
$AWSPOLICY add action s3 ListBucketVersions
$AWSPOLICY add action s3 ListJobs
$AWSPOLICY add action s3 ListMultipartUploadParts
$AWSPOLICY add action s3 PutBucketAcl
$AWSPOLICY add action s3 PutObject
$AWSPOLICY add action s3 PutObjectAcl
$AWSPOLICY add action s3 RestoreObject
$AWSPOLICY add action s3 UpdateJobPriority
$AWSPOLICY add action s3 UpdateJobStatus
$AWSPOLICY add action sns GetTopicAttributes
$AWSPOLICY add action sns ListTopics
$AWSPOLICY add action sns Publish
$AWSPOLICY add action states StartExecution
$AWSPOLICY add action states StartSyncExecution
$AWSPOLICY add action sts AssumeRole

## II. Create Action Groups

$AWSPOLICY addSet action athenaExecution
$AWSPOLICY addToSet action athenaExecution athena getDataCatalog
$AWSPOLICY addToSet action athenaExecution athena getQueryExecution
$AWSPOLICY addToSet action athenaExecution athena startQueryExecution
$AWSPOLICY addToSet action athenaExecution athena stopQueryExecution


$AWSPOLICY addSet action cloudwatchAlarms 
$AWSPOLICY addToSet action cloudwatchAlarms cloudwatch DeleteAlarms
$AWSPOLICY addToSet action cloudwatchAlarms cloudwatch DescribeAlarms
$AWSPOLICY addToSet action cloudwatchAlarms cloudwatch GetMetricData
$AWSPOLICY addToSet action cloudwatchAlarms cloudwatch PutMetricAlarm

$AWSPOLICY addSet action cloudwatchPutMetric 
$AWSPOLICY addToSet action cloudwatchPutMetric cloudwatch PutMetricData

$AWSPOLICY addSet action dynamoDBItems
$AWSPOLICY addToSet action dynamoDBItems dynamodb GetItem
$AWSPOLICY addToSet action dynamoDBItems dynamodb PutItem
$AWSPOLICY addToSet action dynamoDBItems dynamodb UpdateItem

$AWSPOLICY addSet action gluePermissions 
$AWSPOLICY addToSet action gluePermissions glue BatchCreatePartition
$AWSPOLICY addToSet action gluePermissions glue BatchDeletePartition
$AWSPOLICY addToSet action gluePermissions glue BatchDeleteTable
$AWSPOLICY addToSet action gluePermissions glue BatchGetPartition
$AWSPOLICY addToSet action gluePermissions glue CreateDatabase 
$AWSPOLICY addToSet action gluePermissions glue CreatePartition
$AWSPOLICY addToSet action gluePermissions glue CreateTable
$AWSPOLICY addToSet action gluePermissions glue DeleteDatabase
$AWSPOLICY addToSet action gluePermissions glue DeletePartition
$AWSPOLICY addToSet action gluePermissions glue DeleteTable
$AWSPOLICY addToSet action gluePermissions glue GetDatabase
$AWSPOLICY addToSet action gluePermissions glue GetDatabases
$AWSPOLICY addToSet action gluePermissions glue GetPartition
$AWSPOLICY addToSet action gluePermissions glue GetPartitions
$AWSPOLICY addToSet action gluePermissions glue GetTable
$AWSPOLICY addToSet action gluePermissions glue GetTables
$AWSPOLICY addToSet action gluePermissions glue UpdateDatabase
$AWSPOLICY addToSet action gluePermissions glue UpdatePartition
$AWSPOLICY addToSet action gluePermissions glue UpdateTable


$AWSPOLICY addSet action updateAccessKey 
$AWSPOLICY addToSet action updateAccessKey iam CreateAccessKey
$AWSPOLICY addToSet action updateAccessKey iam DeleteAccessKey
$AWSPOLICY addToSet action updateAccessKey iam ListAccessKeys

$AWSPOLICY addSet action listUserKeys
$AWSPOLICY addToSet action listUserKeys iam ListAccessKeys
$AWSPOLICY addToSet action listUserKeys iam ListUsers

$AWSPOLICY addSet action iamPassRole
$AWSPOLICY addToSet action iamPassRole iam passRole

$AWSPOLICY addSet action lambdaInvoke 
$AWSPOLICY addToSet action lambdaInvoke lambda InvokeFunction

$AWSPOLICY addSet action createLogGroup
$AWSPOLICY addToSet action createLogGroup logs CreateLogGroup

$AWSPOLICY addSet action putLogEvents 
$AWSPOLICY addToSet action putLogEvents logs CreateLogStream
$AWSPOLICY addToSet action putLogEvents logs PutLogEvents

$AWSPOLICY addSet action processLogEvents 
$AWSPOLICY addToSet action processLogEvents logs FilterLogEvents
$AWSPOLICY addToSet action processLogEvents logs GetLogEvents
$AWSPOLICY addToSet action processLogEvents logs GetLogRecord
$AWSPOLICY addToSet action processLogEvents logs GetQueryResults
$AWSPOLICY addToSet action processLogEvents logs StartQuery

$AWSPOLICY addSet action stopLogQuery 
$AWSPOLICY addToSet action stopLogQuery logs StopQuery

$AWSPOLICY addSet action s3Any
$AWSPOLICY addToSet action s3Any s3 '*'

$AWSPOLICY addSet action s3BatchRestore
$AWSPOLICY addToSet action s3BatchRestore s3 AbortMultipartUpload
$AWSPOLICY addToSet action s3BatchRestore s3 CreateJob
$AWSPOLICY addToSet action s3BatchRestore s3 DeleteObject
$AWSPOLICY addToSet action s3BatchRestore s3 DescribeJob
$AWSPOLICY addToSet action s3BatchRestore s3 GetAccountPublicAccessBlock
$AWSPOLICY addToSet action s3BatchRestore s3 GetBucketAcl
$AWSPOLICY addToSet action s3BatchRestore s3 GetBucketLocation
$AWSPOLICY addToSet action s3BatchRestore s3 GetBucketLogging
$AWSPOLICY addToSet action s3BatchRestore s3 GetBucketNotification
$AWSPOLICY addToSet action s3BatchRestore s3 GetBucketObjectLockConfiguration
$AWSPOLICY addToSet action s3BatchRestore s3 GetBucketPolicy
$AWSPOLICY addToSet action s3BatchRestore s3 GetBucketPolicyStatus
$AWSPOLICY addToSet action s3BatchRestore s3 GetBucketPublicAccessBlock
$AWSPOLICY addToSet action s3BatchRestore s3 GetBucketVersioning
$AWSPOLICY addToSet action s3BatchRestore s3 GetEncryptionConfiguration
$AWSPOLICY addToSet action s3BatchRestore s3 GetLifecycleConfiguration
$AWSPOLICY addToSet action s3BatchRestore s3 GetObject
$AWSPOLICY addToSet action s3BatchRestore s3 GetObjectAcl
$AWSPOLICY addToSet action s3BatchRestore s3 GetObjectAttributes
$AWSPOLICY addToSet action s3BatchRestore s3 GetObjectRetention
$AWSPOLICY addToSet action s3BatchRestore s3 GetObjectVersion
$AWSPOLICY addToSet action s3BatchRestore s3 GetObjectVersionAcl
$AWSPOLICY addToSet action s3BatchRestore s3 GetObjectVersionAttributes
$AWSPOLICY addToSet action s3BatchRestore s3 GetObjectVersionTagging
$AWSPOLICY addToSet action s3BatchRestore s3 ListBucket
$AWSPOLICY addToSet action s3BatchRestore s3 ListBucketMultipartUploads
$AWSPOLICY addToSet action s3BatchRestore s3 ListBucketVersions
$AWSPOLICY addToSet action s3BatchRestore s3 ListJobs
$AWSPOLICY addToSet action s3BatchRestore s3 ListMultipartUploadParts
$AWSPOLICY addToSet action s3BatchRestore s3 PutObject
$AWSPOLICY addToSet action s3BatchRestore s3 PutObjectAcl

$AWSPOLICY addSet action backupUserPermissions 
$AWSPOLICY addToSet action backupUserPermissions s3 AbortMultipartUpload
$AWSPOLICY addToSet action backupUserPermissions s3 DeleteObject
$AWSPOLICY addToSet action backupUserPermissions s3 GetBucketAcl
$AWSPOLICY addToSet action backupUserPermissions s3 GetBucketLocation
$AWSPOLICY addToSet action backupUserPermissions s3 GetBucketLogging
$AWSPOLICY addToSet action backupUserPermissions s3 GetBucketNotification
$AWSPOLICY addToSet action backupUserPermissions s3 GetBucketObjectLockConfiguration
$AWSPOLICY addToSet action backupUserPermissions s3 GetBucketPolicy
$AWSPOLICY addToSet action backupUserPermissions s3 GetBucketPolicyStatus
$AWSPOLICY addToSet action backupUserPermissions s3 GetBucketVersioning
$AWSPOLICY addToSet action backupUserPermissions s3 GetEncryptionConfiguration
$AWSPOLICY addToSet action backupUserPermissions s3 GetLifecycleConfiguration
$AWSPOLICY addToSet action backupUserPermissions s3 GetObject
$AWSPOLICY addToSet action backupUserPermissions s3 GetObjectAcl
$AWSPOLICY addToSet action backupUserPermissions s3 GetObjectAttributes
$AWSPOLICY addToSet action backupUserPermissions s3 GetObjectRetention
$AWSPOLICY addToSet action backupUserPermissions s3 GetObjectVersion
$AWSPOLICY addToSet action backupUserPermissions s3 GetObjectVersionAcl
$AWSPOLICY addToSet action backupUserPermissions s3 GetObjectVersionAttributes
$AWSPOLICY addToSet action backupUserPermissions s3 GetObjectVersionTagging
$AWSPOLICY addToSet action backupUserPermissions s3 ListBucket
$AWSPOLICY addToSet action backupUserPermissions s3 ListBucketMultipartUploads
$AWSPOLICY addToSet action backupUserPermissions s3 ListBucketVersions
$AWSPOLICY addToSet action backupUserPermissions s3 ListMultipartUploadParts
$AWSPOLICY addToSet action backupUserPermissions s3 PutObject
$AWSPOLICY addToSet action backupUserPermissions s3 PutObjectAcl


$AWSPOLICY addSet action limitedS3Permissions
$AWSPOLICY addToSet action limitedS3Permissions s3 AbortMultipartUpload
$AWSPOLICY addToSet action limitedS3Permissions s3 GetBucketLocation
$AWSPOLICY addToSet action limitedS3Permissions s3 GetObject
$AWSPOLICY addToSet action limitedS3Permissions s3 ListBucket
$AWSPOLICY addToSet action limitedS3Permissions s3 ListBucketMultipartUploads
$AWSPOLICY addToSet action limitedS3Permissions s3 ListMultipartUploadParts

$AWSPOLICY addSet action dangerousS3Permissions
$AWSPOLICY addToSet action dangerousS3Permissions s3 BypassGovernanceRetention
$AWSPOLICY addToSet action dangerousS3Permissions s3 CreateAccessPoint
$AWSPOLICY addToSet action dangerousS3Permissions s3 CreateAccessPointForObjectLambda
$AWSPOLICY addToSet action dangerousS3Permissions s3 CreateBucket
$AWSPOLICY addToSet action dangerousS3Permissions s3 CreateMultiRegionAccessPoint
$AWSPOLICY addToSet action dangerousS3Permissions s3 DeleteBucket
$AWSPOLICY addToSet action dangerousS3Permissions s3 DeleteBucketPolicy
$AWSPOLICY addToSet action dangerousS3Permissions s3 DeleteObjectVersion
$AWSPOLICY addToSet action dangerousS3Permissions s3 PutBucketAcl

$AWSPOLICY addSet action bypassGovernance
$AWSPOLICY addToSet action bypassGovernance s3 BypassGovernanceRetention

$AWSPOLICY addSet action s3BatchJobs 
$AWSPOLICY addToSet action s3BatchJobs s3 CreateJob
$AWSPOLICY addToSet action s3BatchJobs s3 DescribeJob
$AWSPOLICY addToSet action s3BatchJobs s3 ListJobs
$AWSPOLICY addToSet action s3BatchJobs s3 UpdateJobPriority
$AWSPOLICY addToSet action s3BatchJobs s3 UpdateJobStatus

$AWSPOLICY addSet action deleteBucket 
$AWSPOLICY addToSet action deleteBucket s3 DeleteBucket

$AWSPOLICY addSet action s3ListPutDeleteObjects 
$AWSPOLICY addToSet action s3ListPutDeleteObjects s3 DeleteObject
$AWSPOLICY addToSet action s3ListPutDeleteObjects s3 GetObject
$AWSPOLICY addToSet action s3ListPutDeleteObjects s3 ListBucket
$AWSPOLICY addToSet action s3ListPutDeleteObjects s3 PutObject

$AWSPOLICY addSet action s3GetDeleteObjects 
$AWSPOLICY addToSet action s3GetDeleteObjects s3 DeleteObject
$AWSPOLICY addToSet action s3GetDeleteObjects s3 GetObject

$AWSPOLICY addSet action listS3BatchJobs 
$AWSPOLICY addToSet action listS3BatchJobs s3 DescribeJob
$AWSPOLICY addToSet action listS3BatchJobs s3 ListJobs

$AWSPOLICY addSet action readBucketAndAttributes 
$AWSPOLICY addToSet action readBucketAndAttributes s3 GetAccountPublicAccessBlock
$AWSPOLICY addToSet action readBucketAndAttributes s3 GetBucketAcl
$AWSPOLICY addToSet action readBucketAndAttributes s3 GetBucketLocation
$AWSPOLICY addToSet action readBucketAndAttributes s3 GetBucketLogging
$AWSPOLICY addToSet action readBucketAndAttributes s3 GetBucketNotification
$AWSPOLICY addToSet action readBucketAndAttributes s3 GetBucketPolicy
$AWSPOLICY addToSet action readBucketAndAttributes s3 GetBucketPolicyStatus
$AWSPOLICY addToSet action readBucketAndAttributes s3 GetBucketPublicAccessBlock
$AWSPOLICY addToSet action readBucketAndAttributes s3 GetEncryptionConfiguration
$AWSPOLICY addToSet action readBucketAndAttributes s3 GetObject
$AWSPOLICY addToSet action readBucketAndAttributes s3 GetObjectAcl
$AWSPOLICY addToSet action readBucketAndAttributes s3 GetObjectAttributes
$AWSPOLICY addToSet action readBucketAndAttributes s3 ListBucket

$AWSPOLICY addSet action getObjectVersion 
$AWSPOLICY addToSet action getObjectVersion s3 GetObject
$AWSPOLICY addToSet action getObjectVersion s3 GetObjectVersion
$AWSPOLICY addToSet action getObjectVersion s3 ListBucket

$AWSPOLICY addSet action getPutObjectVersion 
$AWSPOLICY addToSet action getPutObjectVersion s3 GetObject
$AWSPOLICY addToSet action getPutObjectVersion s3 GetObjectVersion
$AWSPOLICY addToSet action getPutObjectVersion s3 PutObject

$AWSPOLICY addSet action getObject
$AWSPOLICY addToSet action getObject s3 GetObject

$AWSPOLICY addSet action listAllBuckets 
$AWSPOLICY addToSet action listAllBuckets s3 ListAllMyBuckets

$AWSPOLICY addSet action listBucket
$AWSPOLICY addToSet action listBucket s3 ListBucket

$AWSPOLICY addSet action putObject
$AWSPOLICY addToSet action putObject s3 PutObject

$AWSPOLICY addSet action restoreObject
$AWSPOLICY addToSet action restoreObject s3 RestoreObject

$AWSPOLICY addSet action snsListAndPublish
$AWSPOLICY addToSet action snsListAndPublish sns GetTopicAttributes
$AWSPOLICY addToSet action snsListAndPublish sns ListTopics
$AWSPOLICY addToSet action snsListAndPublish sns Publish

$AWSPOLICY addSet action snsListTopics
$AWSPOLICY addToSet action snsListTopics sns ListTopics

$AWSPOLICY addSet action snsPublish
$AWSPOLICY addToSet action snsPublish sns Publish

$AWSPOLICY addSet action sfnExecution
$AWSPOLICY addToSet action sfnExecution states StartExecution
$AWSPOLICY addToSet action sfnExecution states StartSyncExecution

$AWSPOLICY addSet action stsAssumeRole
$AWSPOLICY addToSet action stsAssumeRole sts AssumeRole

## Resources
$AWSPOLICY add resource any '*'
$AWSPOLICY add resource athenaDatacatalog 'arn:aws:athena:{{REGION}}:{{ACCOUNT}}:datacatalog/*'
$AWSPOLICY add resource athenaWorkgroup 'arn:aws:athena:{{REGION}}:{{ACCOUNT}}:workgroup/rcs3'
$AWSPOLICY add resource dynamodbTable 'arn:aws:dynamodb:{{REGION}}:{{ACCOUNT}}:table/*{{BUCKET_POSTFIX}}'
$AWSPOLICY add resource glueCatalog 'arn:aws:glue:{{REGION}}:{{ACCOUNT}}:catalog'
$AWSPOLICY add resource glueDatabase 'arn:aws:glue:{{REGION}}:{{ACCOUNT}}:database/*'
$AWSPOLICY add resource glueTable 'arn:aws:glue:{{REGION}}:{{ACCOUNT}}:table/*'
$AWSPOLICY add resource glueUserDefinedFunction 'arn:aws:glue:{{REGION}}:{{ACCOUNT}}:userDefinedFunction/*'
$AWSPOLICY add resource iamRestoreBatchPermsRole 'arn:aws:iam::{{ACCOUNT}}:role/{{OWNER}}-{{SYSTEM}}-restore-s3batch-perms-role'
$AWSPOLICY add resource backupServiceAccount 'arn:aws:iam::{{ACCOUNT}}:user/{{OWNER}}-{{SYSTEM}}-sa'
$AWSPOLICY add resource lambdaFunction 'arn:aws:lambda:{{REGION}}:{{ACCOUNT}}:function:{{FUNCTION}}'
$AWSPOLICY add resource lambdaFunctionMethods 'arn:aws:lambda:{{REGION}}:{{ACCOUNT}}:function:{{FUNCTION}}:*'
$AWSPOLICY add resource lambdaCalcUploadBytes 'arn:aws:lambda:{{REGION}}:{{ACCOUNT}}:function:calcUploadBytes'
$AWSPOLICY add resource lambdaCalcUploadBytesMethods 'arn:aws:lambda:{{REGION}}:{{ACCOUNT}}:function:calcUploadBytes:*'
$AWSPOLICY add resource lambdaKeyAgeMetric 'arn:aws:lambda:{{REGION}}:{{ACCOUNT}}:function:keyAgeMetric'
$AWSPOLICY add resource lambdaKeyAgeMetricMethods 'arn:aws:lambda:{{REGION}}:{{ACCOUNT}}:function:keyAgeMetric:*'
$AWSPOLICY add resource lambdaCreateAthenaQueries 'arn:aws:lambda:{{REGION}}:{{ACCOUNT}}:function:createAthenaQueries'
$AWSPOLICY add resource lambdaCreateAthenaQueriesMethods 'arn:aws:lambda:{{REGION}}:{{ACCOUNT}}:function:createAthenaQueries:*'
$AWSPOLICY add resource lambdaCreateS3BatchInput 'arn:aws:lambda:{{REGION}}:{{ACCOUNT}}:function:createS3BatchInput'
$AWSPOLICY add resource lambdaCreateS3BatchInputMethods 'arn:aws:lambda:{{REGION}}:{{ACCOUNT}}:function:createS3BatchInput:*'
$AWSPOLICY add resource lambdaPollCreateJobStatus 'arn:aws:lambda:{{REGION}}:{{ACCOUNT}}:function:pollCreateJobStatus'
$AWSPOLICY add resource lambdaPollCreateJobStatusMethods 'arn:aws:lambda:{{REGION}}:{{ACCOUNT}}:function:pollCreateJobStatus:*'
$AWSPOLICY add resource logsRegionAccountAny 'arn:aws:logs:{{REGION}}:{{ACCOUNT}}:*'
$AWSPOLICY add resource loggroupCreateAthenaQueries 'arn:aws:logs:{{REGION}}:{{ACCOUNT}}:log-group:/aws/lambda/createAthenaQueries:*'
$AWSPOLICY add resource loggroupCreateS3BatchInput 'arn:aws:logs:{{REGION}}:{{ACCOUNT}}:log-group:/aws/lambda/createS3BatchInput:*'
$AWSPOLICY add resource loggroupPollCreateJobStatus 'arn:aws:logs:{{REGION}}:{{ACCOUNT}}:log-group:/aws/lambda/pollCreateJobStatus:*'
$AWSPOLICY add resource loggroupPostCloudwatchMetrics 'arn:aws:logs:{{REGION}}:{{ACCOUNT}}:log-group:/aws/lambda/postCloudwatchMetrics:*'
$AWSPOLICY add resource loggroupPrepDynamoImport 'arn:aws:logs:{{REGION}}:{{ACCOUNT}}:log-group:/aws/lambda/prepDynamoImport:*'
$AWSPOLICY add resource loggroupQueryS3Restore 'arn:aws:logs:{{REGION}}:{{ACCOUNT}}:log-group:/aws/lambda/queryS3Restore:*'
$AWSPOLICY add resource loggroupUpdateDynamodb 'arn:aws:logs:{{REGION}}:{{ACCOUNT}}:log-group:/aws/lambda/updateDynamodb:*'
$AWSPOLICY add resource loggroupCloudtrail 'cloudtrail-logs-{{TRAIL}}'
$AWSPOLICY add resource loggroupCloudtrailArn 'arn:aws:logs:{{REGION}}x:{{ACCOUNT}}:log-group:aws-cloudtrail-logs-{{TRAIL}}:*'
$AWSPOLICY add resource inventoryPrefix 'arn:aws:s3:::*{{INVENTORY_POSTFIX}}'
$AWSPOLICY add resource inventoryRCS3Path 'arn:aws:s3:::*{{INVENTORY_POSTFIX}}/rcs3/*'
$AWSPOLICY add resource reports 'arn:aws:s3:::{{REPORTS}}'
$AWSPOLICY add resource reportsContents 'arn:aws:s3:::{{REPORTS}}/*'
$AWSPOLICY add resource reportsOwner 'arn:aws:s3:::{{REPORTS}}/{{OWNER}}/*'
$AWSPOLICY add resource backupBucketPrefix 'arn:aws:s3:::{{OWNER}}-{{SYSTEM}}-{{BUCKET_POSTFIX}}'
$AWSPOLICY add resource backupBucketContents 'arn:aws:s3:::{{OWNER}}-{{SYSTEM}}-{{BUCKET_POSTFIX}}/*'
$AWSPOLICY add resource inventoryBucketPrefix 'arn:aws:s3:::{{OWNER}}-{{SYSTEM}}-{{INVENTORY_POSTFIX}}'
$AWSPOLICY add resource inventoryBucketPrefixContents 'arn:aws:s3:::{{OWNER}}-{{SYSTEM}}-{{INVENTORY_POSTFIX}}/*'
$AWSPOLICY add resource inventoryBucketRCS3Path 'arn:aws:s3:::{{OWNER}}-{{SYSTEM}}-{{INVENTORY_POSTFIX}}/rcs3/*'
$AWSPOLICY add resource snsRegionAccountAny 'arn:aws:sns:{{REGION}}:{{ACCOUNT}}:*'
$AWSPOLICY add resource snsOwnerNotify 'arn:aws:sns:{{REGION}}:{{ACCOUNT}}:{{OWNER}}-{{SYSTEM}}-{{OWNER_NOTIFY}}'
$AWSPOLICY add resource sfnFullMonty 'arn:aws:states:{{REGION}}:{{ACCOUNT}}:stateMachine:{{OWNER}}-{{SYSTEM}}-sfn-full-monty'


## Resource Groups

$AWSPOLICY addSet resource anyResource
$AWSPOLICY addToSet resource anyResource any

$AWSPOLICY addSet resource athenaResources
$AWSPOLICY addToSet resource athenaResources athenaDatacatalog
$AWSPOLICY addToSet resource athenaResources athenaWorkgroup

$AWSPOLICY addSet resource dynamodbBucket
$AWSPOLICY addToSet resource dynamodbBucket dynamodbTable

$AWSPOLICY addSet resource glueResources
$AWSPOLICY addToSet resource glueResources glueCatalog
$AWSPOLICY addToSet resource glueResources glueDatabase
$AWSPOLICY addToSet resource glueResources glueTable
$AWSPOLICY addToSet resource glueResources glueUserDefinedFunction

$AWSPOLICY addSet resource iamS3batchPermsRole
$AWSPOLICY addToSet resource iamS3batchPermsRole iamRestoreBatchPermsRole

$AWSPOLICY addSet resource backupServiceAccount
$AWSPOLICY addToSet resource backupServiceAccount backupServiceAccount 

$AWSPOLICY addSet resource lambdaFunction
$AWSPOLICY addToSet resource lambdaFunction lambdaFunction
$AWSPOLICY addToSet resource lambdaFunction lambdaFunctionMethods

$AWSPOLICY addSet resource lambdaCalcUploadBytes
$AWSPOLICY addToSet resource lambdaCalcUploadBytes lambdaCalcUploadBytes
$AWSPOLICY addToSet resource lambdaCalcUploadBytes lambdaCalcUploadBytesMethods

$AWSPOLICY addSet resource lambdaKeyAgeMetric
$AWSPOLICY addToSet resource lambdaKeyAgeMetric lambdaKeyAgeMetric
$AWSPOLICY addToSet resource lambdaKeyAgeMetric lambdaKeyAgeMetricMethods

$AWSPOLICY addSet resource lambdaCreateAthenaQueries
$AWSPOLICY addToSet resource lambdaCreateAthenaQueries lambdaCreateAthenaQueries
$AWSPOLICY addToSet resource lambdaCreateAthenaQueries lambdaCreateAthenaQueriesMethods

$AWSPOLICY addSet resource lambdaAthenaBatch
$AWSPOLICY addToSet resource lambdaAthenaBatch lambdaCreateAthenaQueries
$AWSPOLICY addToSet resource lambdaAthenaBatch lambdaCreateAthenaQueriesMethods
$AWSPOLICY addToSet resource lambdaAthenaBatch lambdaCreateS3BatchInput
$AWSPOLICY addToSet resource lambdaAthenaBatch lambdaCreateS3BatchInputMethods
$AWSPOLICY addToSet resource lambdaAthenaBatch lambdaPollCreateJobStatus
$AWSPOLICY addToSet resource lambdaAthenaBatch lambdaPollCreateJobStatusMethods

$AWSPOLICY addSet resource logsRegionAccountAny
$AWSPOLICY addToSet resource logsRegionAccountAny logsRegionAccountAny

$AWSPOLICY addSet resource restoreLoggroups
$AWSPOLICY addToSet resource restoreLoggroups loggroupCreateAthenaQueries
$AWSPOLICY addToSet resource restoreLoggroups loggroupCreateS3BatchInput
$AWSPOLICY addToSet resource restoreLoggroups loggroupPollCreateJobStatus

$AWSPOLICY addSet resource loggroupCreateAthenaQueries
$AWSPOLICY addToSet resource loggroupCreateAthenaQueries loggroupCreateAthenaQueries

$AWSPOLICY addSet resource loggroupCreateS3BatchInput
$AWSPOLICY addToSet resource loggroupCreateS3BatchInput loggroupCreateS3BatchInput

$AWSPOLICY addSet resource loggroupPollCreateJobStatus
$AWSPOLICY addToSet resource loggroupPollCreateJobStatus loggroupPollCreateJobStatus

$AWSPOLICY addSet resource loggroupPostCloudwatchMetrics
$AWSPOLICY addToSet resource loggroupPostCloudwatchMetrics loggroupPostCloudwatchMetrics

$AWSPOLICY addSet resource loggroupPrepDynamoImport
$AWSPOLICY addToSet resource loggroupPrepDynamoImport loggroupPrepDynamoImport

$AWSPOLICY addSet resource loggroupQueryS3Restore
$AWSPOLICY addToSet resource loggroupQueryS3Restore loggroupQueryS3Restore

$AWSPOLICY addSet resource loggroupUpdateDynamodb
$AWSPOLICY addToSet resource loggroupUpdateDynamodb loggroupUpdateDynamodb

$AWSPOLICY addSet resource loggroupCloudtrailArn
$AWSPOLICY addToSet resource loggroupCloudtrailArn loggroupCloudtrailArn

$AWSPOLICY addSet resource inventoryPrefix
$AWSPOLICY addToSet resource inventoryPrefix inventoryPrefix

$AWSPOLICY addSet resource inventoryRCS3Path
$AWSPOLICY addToSet resource inventoryRCS3Path inventoryRCS3Path

$AWSPOLICY addSet resource reports
$AWSPOLICY addToSet resource reports reports

$AWSPOLICY addSet resource reportsContents
$AWSPOLICY addToSet resource reportsContents reportsContents

$AWSPOLICY addSet resource reportsOwner
$AWSPOLICY addToSet resource reportsOwner reportsOwner

$AWSPOLICY addSet resource backupBucket
$AWSPOLICY addToSet resource backupBucket backupBucketPrefix
$AWSPOLICY addToSet resource backupBucket backupBucketContents

$AWSPOLICY addSet resource backupBucketPrefix
$AWSPOLICY addToSet resource backupBucketPrefix backupBucketPrefix

$AWSPOLICY addSet resource backupBucketContents
$AWSPOLICY addToSet resource backupBucketContents backupBucketContents

$AWSPOLICY addSet resource inventoryBucket
$AWSPOLICY addToSet resource inventoryBucket inventoryBucketPrefix
$AWSPOLICY addToSet resource inventoryBucket inventoryBucketPrefixContents

$AWSPOLICY addSet resource inventoryBucketContents
$AWSPOLICY addToSet resource inventoryBucketContents inventoryBucketPrefixContents

$AWSPOLICY addSet resource inventoryBucketRCS3Path
$AWSPOLICY addToSet resource inventoryBucketRCS3Path inventoryBucketRCS3Path

$AWSPOLICY addSet resource snsRegionAccountAny
$AWSPOLICY addToSet resource snsRegionAccountAny snsRegionAccountAny

$AWSPOLICY addSet resource snsOwnerNotify
$AWSPOLICY addToSet resource snsOwnerNotify snsOwnerNotify

$AWSPOLICY addSet resource sfnFullMonty
$AWSPOLICY addToSet resource sfnFullMonty sfnFullMonty

# Principals

$AWSPOLICY add principal serviceS3Batch '"Service":"batchoperations.s3.amazonaws.com"'
$AWSPOLICY add principal serviceLambda '"Service":"lambda.amazonaws.com"'
$AWSPOLICY add principal serviceS3 '"Service":"s3.amazonaws.com"'
$AWSPOLICY add principal serviceScheduler '"Service":"scheduler.amazonaws.com"'
$AWSPOLICY add principal serviceStates '"Service":"states.amazonaws.com"'

# Principal Sets
$AWSPOLICY addSet principal serviceS3Batch
$AWSPOLICY addToSet principal serviceS3Batch serviceS3Batch

$AWSPOLICY addSet principal serviceLambda
$AWSPOLICY addToSet principal serviceLambda serviceLambda

$AWSPOLICY addSet principal serviceS3
$AWSPOLICY addToSet principal serviceS3 serviceS3

$AWSPOLICY addSet principal serviceScheduler
$AWSPOLICY addToSet principal serviceScheduler serviceScheduler

$AWSPOLICY addSet principal serviceStates
$AWSPOLICY addToSet principal serviceStates serviceStates

# Conditions
$AWSPOLICY add condition arnBackupBucket '"ArnLike" : {"aws:SourceArn": "arn:aws:s3:::{{OWNER}}-{{SYSTEM}}-{{BUCKET_POSTFIX}}"}'
$AWSPOLICY add condition equalsAccount '"StringEquals" : {"aws:SourceAccount": "{{ACCOUNT}}"}'
$AWSPOLICY add condition equalsAccountAndControl '"StringEquals" :  {"aws:SourceAccount": "{{ACCOUNT}}", "s3:x-amz-acl": "bucket-owner-full-control"}'
$AWSPOLICY add condition s3PrefixOwner '"StringEquals" : {"s3:prefix": ["{{OWNER}}", "{{OWNER}}/"], "s3:delimiter": ["/"]}'
$AWSPOLICY add condition IPRestrictions "{%- if IP_ADDRESSES is defined %}\"IpAddress\": { \"aws:SourceIp\": {{IP_ADDRESSES | tojson}} } {%- endif %}"

# Condition Sets

$AWSPOLICY addSet condition arnBackupBucket
$AWSPOLICY addToSet condition arnBackupBucket arnBackupBucket

$AWSPOLICY addSet condition equalsAccountAndControl
$AWSPOLICY addToSet condition equalsAccountAndControl equalsAccountAndControl

$AWSPOLICY addSet condition equalsAccount
$AWSPOLICY addToSet condition equalsAccount equalsAccount

$AWSPOLICY addSet condition IPRestrictions
$AWSPOLICY addToSet condition IPRestrictions IPRestrictions

$AWSPOLICY addSet condition s3PrefixOwner
$AWSPOLICY addToSet condition s3PrefixOwner s3PrefixOwner
$AWSPOLICY addToSet condition s3PrefixOwner IPRestrictions

########################## Policies #########################
# This is where the rubber meets the road
# Do this existing JSON file
#     For each file
#         1. Generate policy statements needed (if it doesn't already exist) 
#         2. Generate the policy SET named as <existing file>  without the .json ending
#         3. Add the policy statements to the SET to complete the file definition
### template-policy2 component policies
$AWSPOLICY add policy writeBackupBucket Allow --actionSet backupUserPermissions --resourceSet backupBucket --conditionSet IPRestrictions 
$AWSPOLICY add policy readInventoryBucket Allow --actionSet readBucketAndAttributes --resourceSet inventoryBucket
$AWSPOLICY add policy denyDangerousOps Deny --actionSet dangerousS3Permissions --resourceSet anyResource
$AWSPOLICY add policy publishNotifications Allow --actionSet snsPublish --resourceSet snsOwnerNotify --conditionSet IPRestrictions
$AWSPOLICY add policy snsListTopics Allow --actionSet snsListTopics --resourceSet snsRegionAccountAny --conditionSet IPRestrictions
$AWSPOLICY add policy rotateAccessKey Allow --actionSet updateAccessKey --resourceSet backupServiceAccount --conditionSet IPRestrictions

# ====== template-policy2.json  =======
$AWSPOLICY addSet policy template-policy2
$AWSPOLICY addToSet policy template-policy2 writeBackupBucket
$AWSPOLICY addToSet policy template-policy2 readInventoryBucket
$AWSPOLICY addToSet policy template-policy2 denyDangerousOps
$AWSPOLICY addToSet policy template-policy2 publishNotifications
$AWSPOLICY addToSet policy template-policy2 snsListTopics 
$AWSPOLICY addToSet policy template-policy2 rotateAccessKey 


## keyAgeMetric-policy component policies
$AWSPOLICY add policy listUsersAndKeys Allow --actionSet listUserKeys --resourceSet anyResource 
$AWSPOLICY add policy createLogGroup Allow --actionSet createLogGroup --resourceSet anyResource 
$AWSPOLICY add policy createLogStream Allow --actionSet putLogEvents --resourceSet anyResource 
$AWSPOLICY add policy publishMetrics Allow --actionSet cloudwatchPutMetric --resourceSet anyResource 

## ====== keyAgeMetric-policy.json ======
$AWSPOLICY addSet policy keyAgeMetric-policy 
$AWSPOLICY addToSet policy keyAgeMetric-policy listUsersAndKeys
$AWSPOLICY addToSet policy keyAgeMetric-policy createLogGroup
$AWSPOLICY addToSet policy keyAgeMetric-policy createLogStream
$AWSPOLICY addToSet policy keyAgeMetric-policy publishMetrics


## calcUploadBytes-policy component policies
$AWSPOLICY add policy processLogEvents Allow --actionSet processLogEvents --resourceSet loggroupCloudtrailArn 
$AWSPOLICY add policy stopLogQuery Allow --actionSet stopLogQuery --resourceSet anyResource 

## ====== calcUploadBytes-policy.json ======
$AWSPOLICY addSet policy calcUploadBytes-policy 
$AWSPOLICY addToSet policy calcUploadBytes-policy processLogEvents
$AWSPOLICY addToSet policy calcUploadBytes-policy stopLogQuery
$AWSPOLICY addToSet policy calcUploadBytes-policy publishMetrics

## Generic lambdaAssumeRole-trust component policies

$AWSPOLICY add policy lambdaAssumeRole Allow --actionSet stsAssumeRole --principalSet serviceLambda

## ====== lambdaAssumeRole-trust.json ======
#
# Can be used to generate the following files:
#   calcUploadBytes-trust.json
#   createAthenaQueries-trust.json
#   createS3BatchInput-trust.json
#   keyAgeMetric-trust.json
#   pollCreateJobStatus-trust.json
#   postCloudwatchMetrics-trust.json
#   prepDynamoImport-trust.json
#   queryS3Restore-trust.json
#   restore-lambda-perms-trust.json
#   updateDynamodb-trust.json
$AWSPOLICY addSet policy lambdaAssumeRole-trust
$AWSPOLICY addToSet policy lambdaAssumeRole-trust lambdaAssumeRole

## Generic schedulerAssumeRole-trust components

$AWSPOLICY add policy schedulerAssumeRole Allow --actionSet stsAssumeRole --principalSet serviceScheduler --conditionSet equalsAccount

## ====== lambdaAssumeRole-trust.json ======
#
# Can be used to generate the following files:
#     calcUploadBytes-scheduler-invoke-trust.json 
#     keyAgeMetric-scheduler-invoke-trust.json
$AWSPOLICY addSet policy schedulerAssumeRole-trust
$AWSPOLICY addToSet policy schedulerAssumeRole-trust schedulerAssumeRole

### Generic lambdaInvoke-policy components used for scheduled lambdas
$AWSPOLICY add policy lambdaInvoke Allow --actionSet lambdaInvoke --resourceSet lambdaFunction


## ====== lambdaInvoke-policy.json ======
#
# Can be used to create  {{FUNCTION}}-scheduler-invoke-policy.json where
##   {{FUNCTION}} = [calcUploadBytes,keyAgeMetric]
$AWSPOLICY addSet policy lambdaInvoke-policy
$AWSPOLICY addToSet policy lambdaInvoke-policy lambdaInvoke

### Generic createAthenaQueries-policy c
$AWSPOLICY add policy athenaQueryLogs Allow --actionSet putLogEvents --resourceSet loggroupCreateAthenaQueries


## ====== createAthenaQueries-policy.json ======
#
# Can be used to create  {{FUNCTION}}-scheduler-invoke-policy.json where
##   {{FUNCTION}} = [calcUploadBytes,keyAgeMetric]
$AWSPOLICY addSet policy createAthenaQueries-policy
$AWSPOLICY addToSet policy createAthenaQueries-policy athenaQueryLogs

### createS3BatchInput-policy components 
$AWSPOLICY add policy retrieveETag Allow --actionSet getObject --resourceSet inventoryRCS3Path
$AWSPOLICY add policy S3BatchWriteLogEvents Allow --actionSet putLogEvents --resourceSet loggroupCreateS3BatchInput


## ====== createS3BatchInput-policy.json ======
#
$AWSPOLICY addSet policy createS3BatchInput-policy
$AWSPOLICY addToSet policy createS3BatchInput-policy retrieveETag
$AWSPOLICY addToSet policy createS3BatchInput-policy S3BatchWriteLogEvents


### pollCreateJobsStatus-policy components 
$AWSPOLICY add policy queryS3BatchJobs Allow --actionSet listS3BatchJobs --resourceSet resourceAny
$AWSPOLICY add policy pollJobsStatusWriteLogEvents Allow --actionSet putLogEvents --resourceSet loggroupPollCreateJobStatus


## == pollCreateJobsStatus-policy.json ==
#
$AWSPOLICY addSet policy pollCreateJobStatus-policy
$AWSPOLICY addToSet policy pollCreateJobStatus-policy queryS3BatchJobs
$AWSPOLICY addToSet policy pollCreateJobStatus-policy pollJobsStatusWriteLogEvents


### postCloudwatchMetrics-policy components 
$AWSPOLICY add policy logsCreateLogGroup Allow --actionSet createLogGroup --resourceSet  logsRegionAccountAny
$AWSPOLICY add policy postCloudwatchLogEvents Allow --actionSet putLogEvents --resourceSet loggroupPostCloudwatchMetrics


## == postCloudwatchMetrics-policy.json ==
#
$AWSPOLICY addSet policy postCloudwatchMetrics-policy
$AWSPOLICY addToSet policy postCloudwatchMetrics-policy logsCreateLogGroup
$AWSPOLICY addToSet policy postCloudwatchMetrics-policy postCloudwatchLogEvents
$AWSPOLICY addToSet policy postCloudwatchMetrics-policy publishMetrics


### prepDynamoImport-policy components 
$AWSPOLICY add policy listInventoryBucket Allow --actionSet listBucket --resourceSet  inventoryPrefix
$AWSPOLICY add policy deleteNonCvsObjs Allow --actionSet s3GetDeleteObjects --resourceSet inventoryRCS3Path
$AWSPOLICY add policy dynamoImportWriteLogEvents Allow --actionSet putLogEvents --resourceSet loggroupPrepDynamoImport


## == prepDynamoImport-policy.json ==
#
$AWSPOLICY addSet policy prepDynamoImport-policy
$AWSPOLICY addToSet policy prepDynamoImport-policy listInventoryBucket
$AWSPOLICY addToSet policy prepDynamoImport-policy deleteNonCvsObjs
$AWSPOLICY addToSet policy prepDynamoImport-policy dynamoImportWriteLogEvents


### queryS3Restore-policy components 
$AWSPOLICY add policy queryRestoreStatus Allow --actionSet getObjectVersion --resourceSet  inventoryAny
$AWSPOLICY add policy queryS3RestoreWriteLogEvents Allow --actionSet putLogEvents --resourceSet loggroupQueryS3Restore


## == queryS3Restore-policy.json ==
#
$AWSPOLICY addSet policy queryS3Restore-policy
$AWSPOLICY addToSet policy queryS3Restore-policy queryRestoreStatus
$AWSPOLICY addToSet policy queryS3Restore-policy queryS3RestoreWriteLogEvents

### restore-lambda-perms-policy components 
$AWSPOLICY add policy createAndWriteLogStream Allow --actionSet putLogEvents --resourceSet restoreLoggroups
$AWSPOLICY add policy getReportObject Allow --actionSet getObject --resourceSet reportsContents
$AWSPOLICY add policy queryS3BatchJobsAnyResource Allow --actionSet listS3BatchJobs --resourceSet anyResource


## == restore-lambda-perms-policy.json ==
#
$AWSPOLICY addSet policy restore-lambda-perms-policy
$AWSPOLICY addToSet policy restore-lambda-perms-policy createAndWriteLogStream
$AWSPOLICY addToSet policy restore-lambda-perms-policy getReportObject
$AWSPOLICY addToSet policy restore-lambda-perms-policy queryS3BatchJobsAnyResource


### restore-stepfunc-perms-policy components 
$AWSPOLICY add policy sfnAccessPrimary Allow --actionSet limitedS3Permissions --resourceSet backupBucket
$AWSPOLICY add policy sfnAccessInventory Allow --actionSet limitedS3Permissions --resourceSet inventoryBucket
$AWSPOLICY add policy sfnWriteToUserFolder Allow --actionSet s3ListPutDeleteObjects --resourceSet inventoryBucketRCS3Path
$AWSPOLICY add policy sfnS3BatchJobsAnyResource Allow --actionSet s3BatchJobs --resourceSet anyResource
$AWSPOLICY add policy sfnAthenaAccess Allow --actionSet athenaExecution --resourceSet athenaResources
$AWSPOLICY add policy sfnGlueAccess Allow --actionSet gluePermissions --resourceSet glueResources
$AWSPOLICY add policy sfnCloudwatchMetrics Allow --actionSet cloudwatchAlarms --resourceSet anyResource
$AWSPOLICY add policy sfnListAndPublish Allow --actionSet snsListAndPublish --resourceSet anyResource
$AWSPOLICY add policy sfnInvokeLambdas Allow --actionSet lambdaInvoke --resourceSet lambdaAthenaBatch
$AWSPOLICY add policy sfnInstanceRole Allow --actionSet iamPassRole --resourceSet iamS3batchPermsRole
$AWSPOLICY add policy sfnInvokeStepFunctionRestore Allow --actionSet sfnExecution --resourceSet sfnFullMonty


## == restore-stepfunc-perms-policy.json ==
#
$AWSPOLICY addSet policy restore-stepfunc-perms-policy


$AWSPOLICY addToSet policy restore-stepfunc-perms-policy sfnAccessPrimary
$AWSPOLICY addToSet policy restore-stepfunc-perms-policy sfnAccessInventory
$AWSPOLICY addToSet policy restore-stepfunc-perms-policy sfnWriteToUserFolder
$AWSPOLICY addToSet policy restore-stepfunc-perms-policy sfnS3BatchJobsAnyResource
$AWSPOLICY addToSet policy restore-stepfunc-perms-policy sfnAthenaAccess
$AWSPOLICY addToSet policy restore-stepfunc-perms-policy sfnGlueAccess
$AWSPOLICY addToSet policy restore-stepfunc-perms-policy sfnCloudwatchMetrics
$AWSPOLICY addToSet policy restore-stepfunc-perms-policy sfnListAndPublish
$AWSPOLICY addToSet policy restore-stepfunc-perms-policy sfnInvokeLambdas
$AWSPOLICY addToSet policy restore-stepfunc-perms-policy sfnInstanceRole
$AWSPOLICY addToSet policy restore-stepfunc-perms-policy sfnInvokeStepFunctionRestore

### restore-s3batch-perms-policy components 
$AWSPOLICY add policy restoreObject2Bucket Allow --actionSet restoreObject --resourceSet backupBucketContents
$AWSPOLICY add policy readManifestWriteReport Allow --actionSet getPutObjectVersion --resourceSet inventoryBucketRCS3Path

## == restore-s3batch-perms-policy.json ==
#
$AWSPOLICY addSet policy restore-s3batch-perms-policy

$AWSPOLICY addToSet policy restore-s3batch-perms-policy restoreObject2Bucket
$AWSPOLICY addToSet policy restore-s3batch-perms-policy readManifestWriteReport

### restore-s3batch-perms-trust components 
$AWSPOLICY add policy s3BatchAssumeRole Allow --actionSet stsAssumeRole --principalSet serviceS3Batch

## == restore-s3batch-perms-trust.json ==
#
$AWSPOLICY addSet policy restore-s3batch-perms-trust

$AWSPOLICY addToSet policy restore-s3batch-perms-trust s3BatchAssumeRole 

### updateDynamodb-policy components 
$AWSPOLICY add policy updateDynamoPrintLogs Allow --actionSet putLogEvents --resourceSet loggroupUpdateDynamodb
$AWSPOLICY add policy dynamoTableUpdate Allow --actionSet dynamoDBItems --resourceSet dynamodbBucket

## == updateDynamodb-policy.json ==
#
$AWSPOLICY addSet policy updateDynamodb-policy

$AWSPOLICY addToSet policy updateDynamodb-policy logsCreateLogGroup 
$AWSPOLICY addToSet policy updateDynamodb-policy updateDynamoPrintLogs 
$AWSPOLICY addToSet policy updateDynamodb-policy dynamoTableUpdate 

### template-policy3 components 
$AWSPOLICY add policy readInventoryBucketIPRestricted Allow --actionSet readBucketAndAttributes --resourceSet inventoryBucket --conditionSet IPRestrictions
$AWSPOLICY add policy listAllBuckets Allow --actionSet listAllBuckets --resourceSet anyResource --conditionSet IPRestrictions
$AWSPOLICY add policy viewPersonalReportsFolder Allow --actionSet listAllBuckets --resourceSet reports --conditionSet s3PrefixOwner
$AWSPOLICY add policy addFileToPersonalFolder Allow --actionSet s3ListPutDeleteObjects  --resourceSet reportsOwner --conditionSet IPRestrictions

## == template-policy3.json ==
#
$AWSPOLICY addSet policy template-policy3

$AWSPOLICY addToSet policy template-policy3 writeBackupBucket  
$AWSPOLICY addToSet policy template-policy3 readInventoryBucketIPRestricted 
$AWSPOLICY addToSet policy template-policy3 listAllBuckets 
$AWSPOLICY addToSet policy template-policy3 viewPersonalReportsFolder 
$AWSPOLICY addToSet policy template-policy3 addFileToPersonalFolder 


## == inventory-permissions components ==
$AWSPOLICY add policy inventoryPermissions Allow --actionSet putObject --resourceSet inventoryBucketContents --conditionSet equalsAccountAndControl --principalSet serviceS3

$AWSPOLICY addSet policy inventory-permissions
$AWSPOLICY addToSet policy inventory-permissions inventoryPermissions  



