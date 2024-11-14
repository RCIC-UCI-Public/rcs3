import json
import boto3

def lambda_handler(event, context):
    # run through array checking the job status of each JobId
    # if all jobs have stopped (complete, failed, cancelled status)
    # then pass back the userNotify object to signal end of loop
    # otherwise, pass pack the input array
    listready = []
    listfail = []
    listcancel = []
    listrecheck = []
    
    s3c = boto3.client( "s3control" )
    jobs = event[ "CreateJobItems" ]
    for n in jobs:
        jobid = n[ "JobId" ]
        accountid = n[ "AccountId" ]
        response = s3c.describe_job(
            AccountId=accountid,
            JobId=jobid
        )
        jobstate = response[ "Job" ][ "Status" ]
        if jobstate == "Complete":
            listready.append( jobid )
        elif jobstate == "Failed":
            listfail.append( jobid )
        elif jobstate == "Cancelled":
            listcancel.append( jobid )
        else:
            listrecheck.append( jobid )
    
    if len( listrecheck ) > 0:
        # some jobs are still running, return array to sleep and retry
        return event
    else:
        # send completion message which signals quit and send to user
        sns_message = ""
        for i in listready:
            sns_message += "Submission accepted: {}\n".format( i )
        for i in listfail:
            sns_message += "Submission failed: {}\n".format( i )
        for i in listcancel:
            sns_message += "Submission cancelled: {}\n".format( i )

        return {
            'notifyUser': sns_message,
            'CarryForward': event[ "CarryForward" ]
        }

