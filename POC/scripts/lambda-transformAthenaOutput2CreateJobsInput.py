import json
import re
import boto3

def lambda_handler(event, context):
    # take an array of Athena search results and extract ETag and convert to
    # ARN string to feed to S3 Batch createJob step function
    # expected format of ResultsFile is s3://bucketname/path-to-object/object
    # requires GetObject permissions on records bucket
    l = []
    arnprefix = "arn:aws:s3:::"
    s3 = boto3.client( "s3" )
    for n in event:
        m = re.match( '^s3://([^/]+)/(.+)', n[ "ResultsFile" ] )
        if m:
            r = s3.head_object( Bucket=m.group(1), Key=m.group(2) )
            l.append( {
                'ResultsFile': arnprefix + m.group(1) + "/" + m.group(2),
                'ETag': r[ "ETag" ].strip( '\"' )
            } )
        else:
            l.append( {
                'ResultsFile': n[ "ResultsFile" ],
                'ETag': ""
            } )
    return { 'CreateJobItems': l }