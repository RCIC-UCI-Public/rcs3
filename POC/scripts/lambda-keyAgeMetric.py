import json
import boto3
from datetime import datetime,timedelta
from dateutil.tz import *
session = boto3.Session()
cw_client = session.client( "cloudwatch" )
iam_client = session.client( "iam")

def lambda_handler(event, context):

    # Get the list of users
    try:
        users = iam_client.list_users()
    except Exception as m:
        print( "Invalid call  {}".format( m ) )

    # Filter the users whose name only ends with '-sa' (Service Account)
    allusers = filter(lambda y: y.endswith('-sa'),[ x['UserName'] for x in users['Users'] ] )
    today=datetime.now(tzlocal())
    alarmstr = ""
    for u in allusers:
        response = iam_client.list_access_keys( UserName=u)
        keys=[ (x['AccessKeyId'],x['CreateDate'],x['Status']) for x in response['AccessKeyMetadata'] ]
        for (key,created,status) in keys:
            delta = today - created
            hours = delta.days*24.0 + delta.seconds/3600.0
            # Process only active keys
            if status == 'Active':
                alarmstr = alarmstr + f"{u} ({key},{delta},{hours}) : "
                if delta > timedelta(days=2):
                    alarmstr = alarmstr + "ALARM\n"
                else:
                    alarmstr  = alarmstr + "OK\n"
                setMetricData(u,today,hours)
    return {
        'statusCode': 200,
        'body': json.dumps(alarmstr) }

def setMetricData(sa,now,hours):
    """ Publish how many hours old an active access key is for a particular owner-system """
    namespace="rcs3"
    comps = sa.split('-')
    owner = comps[0]
    system = comps[1]
    metricName = f"{owner}_{system}_key_age"
    metricData = [ { 'MetricName': metricName, 'Value': hours, 'Timestamp': now }]
    ## Publish the age of the key in hours
    cw_client.put_metric_data(Namespace=namespace, MetricData= metricData)
