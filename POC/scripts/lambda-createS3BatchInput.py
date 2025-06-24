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
    delObjs = []
    arnprefix = "arn:aws:s3:::"
    s3 = boto3.client( "s3" )
    athena = boto3.client( "athena" )
    for n in event[ "resultlist" ]:
        if n[ "State" ] == "SUCCEEDED":
            q = athena.get_query_runtime_statistics( QueryExecutionId=n[ "QueryId" ] )
            m = re.match( '^s3://([^/]+)/(.+)', n[ "ResultsFile" ] )
            # check if we have results vs successful but empty search
            if q["QueryRuntimeStatistics"]["Rows"]["OutputRows"] > 0:
                if m:
                    r = s3.head_object( Bucket=m.group(1), Key=m.group(2) )
                    l.append( {
                        'ResultsFile': arnprefix + m.group(1) + "/" + m.group(2),
                        'ETag': r[ "ETag" ].strip( '\"' ),
                        'FileToken': m.group(2)[:64]
                    } )
                    # delete associated metadata file to avoid DynamoDB import error
                    md = m.group(2) + ".metadata"
                    delObjs.append( { "Key": md } )
                else:
                    # unable to parse results file, cannot process file
                    pass
            else:
                # we have an empty result, delete results and metadata files
                delObjs.append( { "Key": m.group(2) } )
                md = m.group(2) + ".metadata"
                delObjs.append( { "Key": md } )
        else:
            # search was not successful, drop for now
            pass
    if delObjs:
        # should we have an option to copy the files before deleting?
        s3.delete_objects( Bucket=m.group(1), Delete={ 'Objects': delObjs, 'Quiet': True } )

    # return list files for processing
    return { 'CreateJobItems': l }