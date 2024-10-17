#!/bin/bash
# Enable monitoring at the Global level
# This script can be run multiple times 
#
# 1. Install the keyAgeMetric Lambda
# 2. Install the "Cron-like" scheduled task to invoke the keyAgeMetric hourly
# 3. Install the cloudwatch overview dashsboard(s)

MYDIR=$(dirname $(realpath $0))
source $MYDIR/functions.sh


# READ in the variables in the $CONFIG_DIR/aws-settings.yaml and present as bash variables 
source  <($COMMON_DIR/aws-settings-to-bash.py)

if [ $# -ne 0 ] ; then
    echo "usage: $0" 
    exit 0
fi

# 1. Install keyAgeMetric
echo "Installing Key Age Metric lambda function"
$MYDIR/create-service-account-restore-lambda.py lambda generic keyAgeMetric

# 2. Schedule the keyAgeMetric Lambda
echo "Create role/policy/trust that allows Scheduler to call the keyAgeMetric"
$MYDIR/create-role-with-policy.py --templatedir templates/keyAge keyAgeMetric-scheduler-invoke 
echo "Create/Update the scheduler (cron-like) entry to regularly invoke the keyAgeMetric lambda"
$MYDIR/create-keyAgeMetric-cron.py

# 3. Enable cloudwatch overview dashboard(s)
echo "Installing Cloudwatch overview Dashboards" 
$MYDIR/set-cloudwatch-dashboards.py
