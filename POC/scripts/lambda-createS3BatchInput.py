import json
import re
import boto3

def lambda_handler(event, context):
    # take an array of Athena search results and extract ETag and convert to
    # ARN string to feed to S3 Batch createJob step function
    # remove metadata file before dynamodb import
    # expected format of ResultsFile is s3://bucketname/path-to-object/object
    # requires GetObject permissions on records bucket
    # limit FileToken to 64 characters, needed for CreateJob idempotency
    l = []
    arnprefix = "arn:aws:s3:::"
    d = event[ "ExpireDays" ]
    s3 = boto3.client( "s3" )
    for n in event[ "taskresult" ]:
        if n[ "State" ] == "SUCCEEDED":
            m = re.match( '^s3://([^/]+)/(.+)', n[ "ResultsFile" ] )
            if m:
                r = s3.head_object( Bucket=m.group(1), Key=m.group(2) )
                l.append( {
                    'ResultsFile': arnprefix + m.group(1) + "/" + m.group(2),
                    'ETag': r[ "ETag" ].strip( '\"' ),
                    'FileToken': m.group(2)[:64],
                    'ExpireDays': d
                } )
                metadata = m.group(2) + ".metadata"
                r = s3.delete_object( Bucket=m.group(1), Key=metadata )
            else:
                l.append( {
                    'ResultsFile': n[ "ResultsFile" ],
                    'ETag': "",
                    'FileToken': "",
                    'ExpireDays': d
                } )
        else:
            # build list of problem files. drop for now
            pass
    return { 'CreateJobItems': l }