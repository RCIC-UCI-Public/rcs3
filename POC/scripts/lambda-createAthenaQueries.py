import boto3
import json
import datetime

def lambda_handler(event, context):
    # create the SQL query to load a specific S3 inventory
    # expects TableName, BackupBucket, InventoryBucket, and HiveDir as inputs
    hivedate = datetime.date.today()
    hivedir = event[ "HiveDir" ].format( str( hivedate ) )
    # it is possible today's inventory run has not completed yet
    # if hivedir/symlink.txt does not exist, then use previous day's inventory run
    hivesym = "{}symlink.txt".format( hivedir )
    s3 = boto3.client( "s3" )
    try:
        s3.head_object(
            Bucket=event[ "InventoryBucket" ],
            Key=hivesym
        )
    except s3.exceptions.ClientError:
        yesterday = hivedate - datetime.timedelta( days=1 )
        hivedir = event[ "HiveDir" ].format( str( yesterday ) )
    
    loadschema = "CREATE EXTERNAL TABLE {} ( bucketname string, filename string, version_id string, is_latest boolean, is_delete_marker boolean, filesize string, last_modified_date string, storage_class string ) ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde' STORED AS INPUTFORMAT 'org.apache.hadoop.hive.ql.io.SymlinkTextInputFormat' OUTPUTFORMAT  'org.apache.hadoop.hive.ql.io.IgnoreKeyTextOutputFormat' LOCATION 's3://{}/{}' ;"
    QuerySchema=loadschema.format( event[ "TableName" ], event[ "InventoryBucket" ], hivedir )
    
    # create the SQL queries for a specific S3 inventory in Athena
    # expects TableName, BackupBucket, and RestoreList as inputs
    a = []
    for request in event[ "RestoreList" ]:
        s = "select bucketname as \"{}\", filename, version_id from {} where filename like '{}' and (storage_class = 'GLACIER' or storage_class = 'DEEP_ARCHIVE')".format( event[ "BackupBucket" ], event[ "TableName" ], request )
        a.append( { "SearchString": s } )
    
    return {
        "QuerySchema": QuerySchema,
        "QueryInventory": a
    }
