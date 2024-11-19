import boto3


def lambda_handler(event, context):
    bucket = event['detail']['bucket']['name']
    filename = event['detail']['object']['key']
    version_id = event['detail']['object']['version-id']
    
    dynamodb = boto3.client( "dynamodb" )
    # generate table name by prepending rcs3 prefix to bucket name
    table = "rcs3-{}".format( bucket )
    
    try:
        get_response = dynamodb.get_item(
            TableName=table,
            Key={ 'filename': { 'S': filename }, 'version_id': { 'S': version_id } }
        )
        
        if not 'Item' in get_response:
            print( "object not in table" )
            print( "table: {}".format( table ) )
            print( "key: {}".format( filename ) )
            print( "version_id: {}".format( version_id ) )
        else:
            update_response =  dynamodb.update_item(
                TableName=table,
                Key={ 'filename': { 'S': filename }, 'version_id': { 'S': version_id } },
                UpdateExpression="set #RC = :s",
                ExpressionAttributeNames={ '#RC': bucket },
                ExpressionAttributeValues={ ':s': { "S": "yes" } },
                ConditionExpression='attribute_exists(filename) and attribute_exists(version_id)',
                ReturnValues="UPDATED_NEW"
            )
    except dynamodb.exceptions.ResourceNotFoundException:
        # okay if table does not exist
        print( "Table not found: {}".format( table ) )