import json

def lambda_handler(event, context):
    # create the SQL queries for a specific S3 inventory in Athena
    # expects TableName, BucketName, and RestoreList as inputs
    a = []
    for request in event[ "RestoreList" ]:
        s = "select bucketname as \"{}\", filename, version_id from {} where filename like '{}'".format( event[ "BucketName" ], event[ "TableName" ], request )
        a.append( { "SearchString": s } )
    return {
        "AthenaQueries": a
    }
