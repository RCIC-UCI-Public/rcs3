import json
import datetime

def lambda_handler(event, context):
    # create the SQL query to load a specific S3 inventory
    # expects TableName, BucketName, and HiveDir as inputs
    hivedate = datetime.date.today()
    hivedir = event[ "HiveDir" ].format( str( hivedate ) )
    # it is possible today's inventory run has not completed yet
    # add test if hivedir/symlink.txt does not exist, then use previous day's inventory run
    loadschema = "CREATE EXTERNAL TABLE {} ( bucketname string, filename string, version_id string, is_latest boolean, is_delete_marker boolean, filesize bigint, last_modified_date string, storage_class string ) ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde' STORED AS INPUTFORMAT 'org.apache.hadoop.hive.ql.io.SymlinkTextInputFormat' OUTPUTFORMAT  'org.apache.hadoop.hive.ql.io.IgnoreKeyTextOutputFormat' LOCATION 's3://{}/{}' ;"
    QuerySchema=loadschema.format( event[ "TableName" ], event[ "BucketName" ], hivedir )
    return {
        "QuerySchema": QuerySchema
    }
