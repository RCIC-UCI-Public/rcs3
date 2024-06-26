#! /bin/bash
# Create the storage bucket and inventory bucket
# Storage bucket: <user>-<host>-$RCS3_BUCKET_POSTFIX
# Inventory bucket: <user>-<host>-$RCS3_INVENTORY_POSTFIX
MYDIR=$(dirname $(realpath $0))
source $MYDIR/functions.sh
# READ in the variables in the $CONFIG_DIR/aws-settings.yaml and present as bash variables 
source  <($COMMON_DIR/aws-settings-to-bash.py)

function helptext
{
      echo "create-bucket-with-inventory.sh [-h] [-g] [-n <networks>] <user> <host>"
      echo "    -h    help"
      echo "    -d    dryrun. Just print commands that would be executed " 
      echo "    -g    tier to glacier instead of deep archive"
      echo "    -i <networks>  - valid network(s) that can access bucket"
      echo "                     e.g., 192.168.0.0/16" 
      echo "                     e.g., 192.168.0.0/16,10.10.0.1/24" 
}

OVERRIDE_NETWORKS=""
TIERCLASS="deeparchive"
DRYRUN=""

# Define options
optstring="dghi:"

while getopts ${optstring} arg; do
  case $arg in
    h)
      helptext
      exit 0
      ;;
    d)
      DRYRUN="echo"
      ;;
    g)
      TIERCLASS="glacier"
      ;;
    i)
      OVERRIDE_NETWORKS="--iprestrictions=$OPTARG"
      ;;
    ?)
      echo "Invalid option: -$OPTARG"
      exit 1
      ;;
  esac
done

# Access remaining arguments after processing options
shift $((OPTIND-1))  # Shift remaining arguments after processed options

if [ $# -ne 2 ] ; then
    helptext
    exit 1 
fi

######################  INPUTS READ, CREATE BUCKETS, APPLY POLICIES ####################
outputs=$OUTPUTS_DIR
templates=$TEMPLATES_DIR
LCD=$TEMPLATES_DIR/lifecycle

user=$1
host=$2

# AWS account
awsacct=$RCS3_ACCOUNTID
awsprofile=$RCS3_PROFILE
AWS="$DRYRUN aws --profile $awsprofile --region=$RCS3_REGION"

for bucketname in $user-$host-$RCS3_BUCKET_POSTFIX $user-$host-$RCS3_INVENTORY_POSTFIX
do
    $DRYRUN createbucket $bucketname "$AWS"
done

# put bucket policy for inventory bucket
localize $templates/template-inventory-permissions.json $outputs/$user-$host-inv-perm.json
$AWS s3api put-bucket-policy --bucket $user-$host-$RCS3_INVENTORY_POSTFIX --policy file://$outputs/$user-$host-inv-perm.json

# put the lifecycle policy into the inventory bucket to delete after 30 days deletions
$AWS s3api put-bucket-lifecycle-configuration --bucket $user-$host-$RCS3_INVENTORY_POSTFIX --lifecycle-configuration file://$LCD/lifecycle-delete-inventory.json

# put inventory configuration on the primary bucket
localize $templates/template-inventory-configuration.json $outputs/$user-$host-inv-cfg.json
$AWS s3api put-bucket-inventory-configuration --bucket $user-$host-$RCS3_BUCKET_POSTFIX --id $user-$host-daily --inventory-configuration file://$outputs/$user-$host-inv-cfg.json

# put the lifecycle policy into the bucket for storage transititions and permanent deletions
$AWS s3api put-bucket-lifecycle-configuration --bucket $user-$host-$RCS3_BUCKET_POSTFIX --lifecycle-configuration file://$LCD/lifecycle-all-$TIERCLASS.json

# create service account access policy, service account, and attach policy
$DRYRUN $MYDIR/create-service-account-policy.py $user $host $OVERRIDE_NETWORKS

$AWS iam create-user --user-name $user-$host-sa

$AWS iam attach-user-policy --user-name $user-$host-sa --policy-arn arn:aws:iam::${awsacct}:policy/$user-$host-$RCS3_POLICY_POSTFIX

# create a password for the service account, print it out and save it
# These need to be transmitted to the sysadmin in a secure fashion
$AWS iam create-access-key --user-name $user-$host-sa | tee $outputs/$user-$host.credentials
