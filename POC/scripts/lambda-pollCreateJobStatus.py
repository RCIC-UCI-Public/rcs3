import json
import boto3

def lambda_handler(event, context):
    # TODO implement
    listready = []
    listfail = []
    listrecheck = []
    
    s3c = boto3.client( "s3c" )
    for jobid in event:
        response = s3c.describe_job(
            AccountId=aws[ "accountid" ],
            JobId=jobid
        )
        jobstate = response[ "Job" ][ "Status" ]
        if jobstate == "Complete":
            listready.append( jobid )
        elif jobstate == "Failed":
            listfail.append( jobid )
        elif jobstate == "Cancelled":
            listfail.append( jobid )
        else:
            listrecheck.append( jobid )
    
    if len( listready ) > 0:
        # some jobs are still running, return array to sleep and retry
        return event
    else:
        # send completion message which signals quit and send to user
        for i in listready:
            sns_message += "Completed: {}\n".format( i )
        for i in listfail:
            sns_message += "Job failed: {}\n".format( i )

        return {
            'notifyUser': sns_message
        }
