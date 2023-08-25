#! /bin/bash
# Create the storage bucket and inventory bucket
# Storage bucket: <user>-<host>-$RCS3_BUCKET_POSTFIX
# Inventory bucket: <user>-<host>-$RCS3_INVENTORY_POSTFIX
MYDIR=$(dirname $(realpath $0))
source $MYDIR/functions.sh
# READ in the variables in the $CONFIG_DIR/aws-settings.yaml and present as bash variables 
source  <($COMMON_DIR/aws-settings-to-bash.py)

if [ $# -ne 2 ] ; then
    echo $0 user host
    exit 0
fi

outputs=$OUTPUTS_DIR
templates=$TEMPLATES_DIR

user=$1
host=$2

# AWS account
awsacct=$RCS3_ACCOUNTID
awsprofile=$RCS3_PROFILE
AWS="aws --profile $awsprofile"

for bucketname in $user-$host-$RCS3_BUCKET_POSTFIX $user-$host-$RCS3_INVENTORY_POSTFIX
do
    createbucket $bucketname "$AWS"
done

# put bucket policy for inventory bucket
localize $templates/template-inventory-permissions.json $outputs/$user-$host-inv-perm.json
$AWS s3api put-bucket-policy --bucket $user-$host-$RCS3_INVENTORY_POSTFIX --policy file://$outputs/$user-$host-inv-perm.json

# put inventory configuration on the primary bucket
localize $templates/template-inventory-configuration.json $outputs/$user-$host-inv-cfg.json
$AWS s3api put-bucket-inventory-configuration --bucket $user-$host-$RCS3_BUCKET_POSTFIX --id $user-$host-daily --inventory-configuration file://$outputs/$user-$host-inv-cfg.json

# put the lifecycle policy into the bucket for storage transititions and permanent deletions
$AWS s3api put-bucket-lifecycle-configuration --bucket $user-$host-$RCS3_BUCKET_POSTFIX --lifecycle-configuration file://$templates/lifecycle-all.json

# create service account access policy, service account, and attach policy
localize $templates/template-policy2.json $outputs/$user-$host-policy.json
$AWS iam create-policy --policy-name $user-$host-$RCS3_POLICY_POSTFIX  --policy-document file://$outputs/$user-$host-policy.json

$AWS iam create-user --user-name $user-$host-sa

$AWS iam attach-user-policy --user-name $user-$host-sa --policy-arn arn:aws:iam::${awsacct}:policy/$user-$host-$RCS3_POLICY_POSTFIX

# create a password for the service account, print it out and save it
# These need to be transmitted to the sysadmin in a secure fashion
$AWS iam create-access-key --user-name $user-$host-sa | tee $outputs/$user-$host.credentials
