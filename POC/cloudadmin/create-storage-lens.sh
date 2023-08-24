#! /bin/bash
# Create the storage lens configuration and bucket 
MYDIR=$(dirname $(realpath $0))
source $MYDIR/functions.sh

# READ in the variables in the $CONFIG_DIR/aws-settings.yaml and present as bash variables 
source  <($COMMON_DIR/aws-settings-to-bash.py)

if [ $# -ne 0 ] ; then
    echo "usage: $0" 
    exit 0
fi

outputs=$OUTPUTS_DIR
templates=$TEMPLATES_DIR

# AWS account
awsacct=$RCS3_ACCOUNTID
awsprofile=$RCS3_PROFILE
AWS="aws --profile $awsprofile"


# Create the storage lens bucket
createbucket $RCS3_LENSBUCKET "$AWS"

# create storage lens configurations configuration and upload to AWS 

localize $templates/template-lens-configuration.json $outputs/lens-configuration.json
$AWS s3control put-storage-lens-configuration --profile $awsprofile --account-id $awsacct --config-id $RCS3_LENS --region $RCS3_REGION --storage-lens-configuration file://$outputs/lens-configuration.json
