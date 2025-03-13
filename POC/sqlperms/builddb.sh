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
