import boto3
import datetime


def lambda_handler(event, context):
    bucket = event['detail']['bucket']['name']
    filename = event['detail']['object']['key']
    version_id = event['detail']['object']['version-id']
    request_id = event['detail']['request-id']
    eventtime = event['time']
    eventid = event['id']
    
    epochmilliseconds = int( datetime.datetime.fromisoformat( eventtime ).timestamp() ) * 1000
    #epochmilliseconds = int( datetime.datetime.now().timestamp() ) * 1000

    cloudwatch = boto3.client( "cloudwatch" )
    response = cloudwatch.put_metric_data(
        MetricData = [
            {
                'MetricName': 'transition',
                'Dimensions': [
                    {
                        'Name': 'BUCKET',
                        'Value': bucket
                    },
                    {
                        'Name': 'JOB',
                        'Value': request_id
                    }
                ],
                'Unit': 'None',
                'Value': 1
            },
        ],
        Namespace='UCIRestore'
    )
    
    log = boto3.client( 'logs' )
    try:
        response = log.create_log_stream(
            logGroupName='/aws/lambda/postCloudwatchMetrics',
            logStreamName=eventid
        )
    except log.exceptions.ResourceAlreadyExistsException:
        # okay if already exists
        pass
    message = "bucket: {} key: {} version_id: {}".format( bucket, filename, version_id )
    response = log.put_log_events(
        logGroupName='/aws/lambda/postCloudwatchMetrics',
        logStreamName=eventid,
        logEvents=[
            {
                'timestamp': epochmilliseconds,
                'message': message
            }
        ]
    )
