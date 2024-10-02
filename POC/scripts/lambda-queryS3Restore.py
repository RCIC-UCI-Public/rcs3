from urllib.parse import unquote_plus
import json
import botocore
import boto3

def lambda_handler(event, context):
    s3 = boto3.client( "s3" )
    
    key = unquote_plus( event[ "tasks" ][0][ "s3Key" ] )
    versionId = event[ "tasks" ][0][ "s3VersionId" ]
    schemaVersion = event[ "invocationSchemaVersion" ]
    if schemaVersion == "1.0":
        bucketArn = event[ "tasks" ][0][ "s3BucketArn" ]
        bucketName = bucketArn.split(":")[-1]
    elif schemaVersion == "2.0":
        bucketName = event[ "tasks" ][0][ "s3Bucket" ]
    else:
        print( "unknown invocationSchemaVersion {}".format( schemaVersion ) )
        return {}
    
    myresults = {}
    myresults[ "taskId" ] = event[ "tasks" ][0][ "taskId" ]
    if key == "filename" and versionId == "version_id":
        myresults[ "resultCode" ] = "Succeeded"
        myresults[ "resultString" ] = "ignore table header"
    else:
        try:
            filechk = s3.head_object( Bucket=bucketName, Key=key, VersionId=versionId )
            filemeta = filechk[ 'ResponseMetadata' ][ 'HTTPHeaders' ]
            sclass = filemeta[ 'x-amz-storage-class' ]
            if sclass in [ 'GLACIER', 'DEEP_ARCHIVE' ]:
                if 'x-amz-restore' in filemeta:
                    if 'ongoing-request="false"' in filemeta[ 'x-amz-restore' ]:
                        myresults[ "resultCode" ] = "Succeeded"
                        myresults[ "resultString" ] = "Restore ready"
                    else:
                        myresults[ "resultString" ] = "PermanentFailure"
                        myresults[ "resultString" ] = "Restore in progress"
                else:
                    myresults[ "resultCode" ] = "PermanentFailure"
                    myresults[ "resultString" ] = sclass
            else:
                # file already available for restore
                myresults[ "resultCode" ] = "Succeeded"
                myresults[ "resultString" ] = sclass
        except botocore.exceptions.ClientError as error:
            myresults[ "resultCode" ] = "PermanentFailure"
            myresults[ "resultString" ] = 'Error Message: {}'.format(error.response['Error']['Message'])
    
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

