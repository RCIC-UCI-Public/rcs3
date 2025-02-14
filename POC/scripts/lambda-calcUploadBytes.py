import boto3
import time
import json
import math
from datetime import datetime, timedelta
def setMetricData(client,namespace,timestamp,bytes,ops):
    """ Publish how many bytes,ops uploaded in timeframe """
    metricData = [ { 'MetricName': 'bytes_upload', 'Value': bytes, 'Unit': 'Bytes', 'Timestamp': timestamp }]
    client.put_metric_data(Namespace=namespace, MetricData= metricData)
    metricData = [ { 'MetricName': 'operations_upload', 'Value': ops, 'Timestamp': timestamp }]
    client.put_metric_data(Namespace=namespace, MetricData= metricData)   

def lambda_handler(event, context):
    # Initialize CloudWatch Logs client
    client = boto3.client('logs')
    client_cw = boto3.client('cloudwatch')
    
    # Read Parameters from event
    #log_group_name = 'aws-cloudtrail-logs-xiangmix-cncm2'  # Replace with your log group name
    log_group_name = event['logGroup']
    namespace = event['namespace']

    # Calculate the time range ( previous full 5 minute interval)
    ts = datetime.now()
    pIEnd = ts.replace(minute=(math.floor(ts.minute/5)*5),second=0,microsecond=0)
    pIBegin = pIEnd - timedelta(minutes=5)
    start_time = int(pIBegin.timestamp()*1000)
    end_time = int(pIEnd.timestamp()*1000)
 
    # Using filter_log_events (no filter defined, but could in future)
    # Read events, and compute bytes uploaded.  May have to call multiple times to process
    # all events in the time range

    next_token = None
    nevents = 0
    totBytesIn = 0
    nparts = 0 
    try:
        while True:
            if next_token:
                # have a next token from previous call 
                response = client.filter_log_events(
                    logGroupName=log_group_name,
                    startTime=start_time,
                    endTime=end_time,
                    nextToken=next_token
                )
            else:
                response = client.filter_log_events(
                    logGroupName=log_group_name,
                    startTime=start_time,
                    endTime=end_time
                )
            events = response.get('events')        
            next_token = response.get('nextToken')

            neventsPartial = len(events)
            nevents += neventsPartial
            nparts += 1


            for event in events:
                eventJson = json.loads(event['message'])
                bytesIn = eventJson['additionalEventData']['bytesTransferredIn']
                totBytesIn += bytesIn 
                eventName = eventJson['eventName']
                # print (eventJson.keys())
                # print(f"Timestamp: {event['timestamp']}, bytesIn: {bytesIn}, eventName: {eventName}")

            # Done if no next_token or we retrieved no events
            if not next_token:
                break
           
        # Publish metric data
        setMetricData(client_cw, namespace, pIEnd, totBytesIn, nevents)

        return {
            'statusCode': 200,
            'body': f"Retrieved {nevents} events in {nparts} retrieval. {totBytesIn} bytes during {pIBegin} - {pIEnd}. startTime: {start_time}  endTime: {end_time}"
        }
    
    except Exception as e:
        print(f"Error fetching logs: {e}")
        return {
            'statusCode': 500,
            'body': f"Error fetching logs: {e}"
        }


