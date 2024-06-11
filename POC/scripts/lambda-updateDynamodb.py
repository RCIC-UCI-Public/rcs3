import boto3
import datetime


def lambda_handler(event, context):
    bucket = event['detail']['bucket']['name']
    filename = event['detail']['object']['key']
    versionId = event['detail']['object']['version-id']
    eventtime = event['time']

    dynamodb = boto3.resource( "dynamodb" )
    # assumes table name is also bucket name
    table = dynamodb.Table( bucket )

    get_response = table.get_item(
        Key={ 'filename': filename, 'versionId': versionId},
        )
        
    if len(get_response) == 1:
        print("object does not exist")
    else:
        restore_starttime = datetime.datetime.strptime(get_response['Item']['restore_init_time'], '%Y-%m-%dT%H:%M:%S%fZ')
        restore_finishtime = datetime.datetime.strptime(eventtime, '%Y-%m-%dT%H:%M:%S%fZ')
        restore_delta = restore_finishtime - restore_starttime
        restore_duration = restore_delta.total_seconds()/60

        update_response =  table.update_item(
            Key={ 'filename': filename, 'versionId': versionId},
            UpdateExpression="set restore_completed = :s, restore_comp_time = :c, restore_duration = :e, object_accessible = :val1",
            ExpressionAttributeValues={':s': "yes", ':c': eventtime, ':e': int(restore_duration), ':val1': "yes"},
            ConditionExpression='attribute_exists(filename) and attribute_exists(versionId)',
            ReturnValues="UPDATED_NEW")
