import json
import re
import boto3

def lambda_handler(event, context):
    # take an array of Athena search results and extract ETag and convert to
    # ARN string to feed to S3 Batch createJob step function
    # expected format of ResultsFile is s3://bucketname/path-to-object/object
    # requires GetObject permissions on records bucket
    # requires athena:GetQueryRuntimeStatistics to check for empty results
    # limit FileToken to 64 characters, needed for CreateJob idempotency
    l = []
    arnprefix = "arn:aws:s3:::"
    s3 = boto3.client( "s3" )
    athena = boto3.client( "athena" )
    for n in event[ "resultlist" ]:
        if n[ "State" ] == "SUCCEEDED":
            # check if we have results vs successful but empty search
            q = athena.get_query_runtime_statistics( QueryExecutionId=n[ "QueryId" ] )
            if q["QueryRuntimeStatistics"]["Rows"]["OutputRows"] > 0:
                m = re.match( '^s3://([^/]+)/(.+)', n[ "ResultsFile" ] )
                if m:
                    r = s3.head_object( Bucket=m.group(1), Key=m.group(2) )
                    l.append( {
                        'ResultsFile': arnprefix + m.group(1) + "/" + m.group(2),
                        'ETag': r[ "ETag" ].strip( '\"' ),
                        'FileToken': m.group(2)[:64]
                    } )
                else:
                    # unable to get ETag, cannot process file
                    pass
            else:
                # we have an empty result, no need to process file
                pass
        else:
            # search was not successful, drop for now
            pass
    # return list files for processing
    return { 'CreateJobItems': l }