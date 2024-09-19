import json
import boto3

def lambda_handler(event, context):
    s3 = boto3.client( "s3" )
    
    key = event[ "tasks" ][0][ "s3Key" ]
    versionId = event[ "tasks" ][0][ "s3VersionId" ]
    bucketArn = event[ "tasks" ][0][ "s3BucketArn" ] 
    
    myresults = {}
    myresults[ "taskId" ] = event[ "tasks" ][0][ "taskId" ]
    if key == "filename" and versionId == "version_id":
        myresults[ "resultCode" ] = "Succeeded"
        myresults[ "resultString" ] = "ignore table header"
    else:
        ( s_arn, s_aws, s_s3, s_region, s_acct, bucketName ) = bucketArn.split( ":" )
        filechk = s3.head_object( Bucket=bucketName, Key=key, VersionId=versionId )
        if filechk[ "StorageClass" ] == "GLACIER":
            myresults[ "resultCode" ] = "PermanentFailure"
        else:
            myresults[ "resultCode" ] = "Succeeded"
        myresults[ "resultString" ] = ""
    
    response = {
            "invocationSchemaVersion": event[ "invocationSchemaVersion" ],
            "treatMissingKeysAs" : "PermanentFailure",
            "invocationId" : event[ "invocationId" ],
            "results": [ myresults ]
        }
    
    return response

  

# input
#{
#    "invocationSchemaVersion": "1.0",
#    "invocationId": "YXNkbGZqYWRmaiBhc2RmdW9hZHNmZGpmaGFzbGtkaGZza2RmaAo",
#    "job": {
#        "id": "f3cc4f60-61f6-4a2b-8a21-d07600c373ce"
#    },
#    "tasks": [
#        {
#            "taskId": "dGFza2lkZ29lc2hlcmUK",
#            "s3Key": "customerImage1.jpg",
#            "s3VersionId": "1",
#            "s3BucketArn": "arn:aws:s3:::amzn-s3-demo-bucket"
#        }
#    ]  
#}

# response
#{
#  "invocationSchemaVersion": "1.0",
#  "treatMissingKeysAs" : "PermanentFailure",
#  "invocationId" : "YXNkbGZqYWRmaiBhc2RmdW9hZHNmZGpmaGFzbGtkaGZza2RmaAo",
#  "results": [
#    {
#      "taskId": "dGFza2lkZ29lc2hlcmUK",
#      "resultCode": "Succeeded",
#      "resultString": "[\"Alice\", \"Bob\"]"
#    }
#  ]
#}
  
