import boto3
import datetime


def lambda_handler(event, context):
    bucket = event['detail']['bucket']['name']
    filename = event['detail']['object']['key']
    version_id = event['detail']['object']['version-id']
    eventtime = event['time']
    
    dynamodb = boto3.client( "dynamodb" )
    # assumes table name is also bucket name
    table = bucket
    
    try:
        get_response = dynamodb.get_item(
            TableName=table,
            Key={ 'filename': { 'S': filename }, 'version_id': { 'S': version_id } }
        )
        
        if not 'Item' in get_response:
            print("object does not exist")
        else:
            #restore_starttime = datetime.datetime.strptime(get_response['Item']['restore_init_time'], '%Y-%m-%dT%H:%M:%S%fZ')
            #restore_finishtime = datetime.datetime.strptime(eventtime, '%Y-%m-%dT%H:%M:%S%fZ')
            #restore_delta = restore_finishtime - restore_starttime
            #restore_duration = restore_delta.total_seconds()/60
            #
            #update_response =  table.update_item(
            #    Key={ 'filename': filename, 'version_id': version_id},
            #    UpdateExpression="set restore_completed = :s, restore_comp_time = :c, restore_duration = :e, object_accessible = :val1",
            #    ExpressionAttributeValues={':s': "yes", ':c': eventtime, ':e': int(restore_duration), ':val1': "yes"},
            #    ConditionExpression='attribute_exists(filename) and attribute_exists(version_id)',
            #    ReturnValues="UPDATED_NEW")
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
        pass