#! /bin/bash
# Create the storage bucket and inventory bucket
# Storage bucket: <user>-<host>-$RCS3_BUCKET_POSTFIX
# Inventory bucket: <user>-<host>-$RCS3_INVENTORY_POSTFIX
MYDIR=$(dirname $(realpath $0))
TEMPLATES_DIR=$MYDIR/../templates
CONFIG_DIR=$MYDIR/../config
OUTPUTS_DIR=$MYDIR/../outputs

# READ in the variables in the $CONFIG_DIR/aws-settings.yaml and present as bash variables 
source  <($MYDIR/aws-settings-to-bash.py)

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

function localize {
# need to replace patterns in generic files to localize
# localize <inputputfile> <outputfile>
   local input=$1
   local output=$2
   cat $input | \
   sed s/xxxawsacctxxx/$awsacct/ | \
   sed -e s/xxxbucketxxx/$RCS3_BUCKET_POSTFIX/g -e s/xxxinventoryxxx/$RCS3_INVENTORY_POSTFIX/g | \
   sed -e s/xxxpolicyxxx/RCS3_POLICY_POSTFIX/g | \
   sed s/xxxuserxxx/$user/ | \
   sed s/xxxhostxxx/$host/ > $output
}

for bucketname in $user-$host-$RCS3_BUCKET_POSTFIX $user-$host-$RCS3_INVENTORY_POSTFIX
do
    #aws --profile $awsprofile s3api create-bucket --bucket $bucketname --object-lock-enabled-for-bucket --region $RCS3_REGION --create-bucket-configuration LocationConstraint=$RCS3_REGION
    aws --profile $awsprofile s3api create-bucket --bucket $bucketname --region $RCS3_REGION --create-bucket-configuration LocationConstraint=$RCS3_REGION

    aws --profile $awsprofile s3api put-bucket-encryption --bucket $bucketname --server-side-encryption-configuration '{
    "Rules": [
        {
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            }
        }
    ]
}'

    # redundant with object locking
    aws --profile $awsprofile s3api put-bucket-versioning --bucket $bucketname --versioning-configuration Status=Enabled

    aws --profile $awsprofile s3api put-public-access-block --bucket $bucketname --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
done

# put bucket policy for inventory bucket
localize $templates/template-inventory-permissions.json $outputs/$user-$host-inv-perm.json

aws --profile $awsprofile s3api put-bucket-policy --bucket $user-$host-$RCS3_INVENTORY_POSTFIX --policy file://$outputs/$user-$host-inv-perm.json

# put inventory configuration on the primary bucket
localize $templates/template-inventory-configuration.json $outputs/$user-$host-inv-cfg.json

aws --profile $awsprofile s3api put-bucket-inventory-configuration --bucket $user-$host-$RCS3_BUCKET_POSTFIX --id $user-$host-daily --inventory-configuration file://$outputs/$user-$host-inv-cfg.json

# put the lifecycle policy into the bucket for storage transititions and permanent deletions

aws --profile $awsprofile s3api put-bucket-lifecycle-configuration --bucket $user-$host-$RCS3_BUCKET_POSTFIX --lifecycle-configuration file://$templates/lifecycle-all.json

# create service account access policy
localize $templates/template-policy2.json $outputs/$user-$host-policy.json

aws --profile $awsprofile iam create-policy --policy-name $user-$host-$RCS3_POLICY_POSTFIX  --policy-document file://$outputs/$user-$host-policy.json

aws --profile $awsprofile iam create-user --user-name $user-$host-sa

aws --profile $awsprofile iam attach-user-policy --user-name $user-$host-sa --policy-arn arn:aws:iam::${awsacct}:policy/$user-$host-$RCS3_POLICY_POSTFIX

aws --profile $awsprofile iam create-access-key --user-name $user-$host-sa | tee $outputs/$user-$host.credentials
