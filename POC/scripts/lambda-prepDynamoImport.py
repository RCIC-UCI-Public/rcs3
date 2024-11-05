import re
import boto3

def lambda_handler(event, context):
    # remove .txt and .metadata files from directory
    # remaining .cvs files will be imported by DynamoDB
    b = event[ "Bucket" ]
    p = event[ "DataDir" ]
    k = []
    d = []
    s3 = boto3.client( "s3" )
    response = s3.list_objects_v2( Bucket=b, Prefix=p )
    for obj in response[ "Contents" ]:
        key = obj[ "Key" ]
        if re.search( "\.csv$", key ):
            # keep this file
            k.append( { "Key": key } )
        else:
            # delete this file
            d.append( { "Key": key } )
    
    #s3.delete_objects( Bucket=b, Delete={ 'Objects': d, 'Quiet': True } )
    
    return { "KeepFiles": k, "DeleteFiles": d }
