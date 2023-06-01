#! /bin/sh
MYDIR=$(dirname $(realpath $0))
CONFIG_DIR=$MYDIR/../config 
TEMPLATES_DIR=$MYDIR/../templates


if [ $# -ne 2 ] ; then
    echo $0 user host
    exit 0
fi

user=$1
host=$2
# RCIC AWS account
uciawsacct=774954368688
awsprofile=774954368688_AWSAdministratorAccess

# AWS cli and common options
AWSCLI=/usr/bin/aws
AWS="$AWSCLI --profile $awsprofile"
## USE the aws-admin config file in the config directory
export AWS_CONFIG_FILE=$CONFIG_DIR/aws-admin

#echo $AWS_CONFIG_FILE
#echo $AWS

bucketname=$user-$host-uci-bkup-bucket
#aws --profile $awsprofile s3api create-bucket --bucket $bucketname --object-lock-enabled-for-bucket --region us-west-2 --create-bucket-configuration LocationConstraint=us-west-2
$AWS s3api create-bucket --bucket $bucketname --region us-west-2 --create-bucket-configuration LocationConstraint=us-west-2

$AWS s3api put-bucket-encryption --bucket $bucketname --server-side-encryption-configuration '{
    "Rules": [
        {
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            }
        }
    ]
}'

# redundant with object locking
$AWS s3api put-bucket-versioning --bucket $bucketname --versioning-configuration Status=Enabled

$AWS s3api put-public-access-block --bucket $bucketname --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"


cat $TEMPLATES_DIR/template-policy2.json | \
sed s/xxxuserxxx/$user/ | \
sed s/xxxhostxxx/$host/ > $user-$host-policy.json

$AWS iam create-policy --policy-name $user-$host-uci-bkup-policy  --policy-document file://$user-$host-policy.json

$AWS iam create-user --user-name $user-$host-sa

$AWS iam attach-user-policy --user-name $user-$host-sa --policy-arn arn:aws:iam::${uciawsacct}:policy/$user-$host-uci-bkup-policy

$AWS iam create-access-key --user-name $user-$host-sa | tee credentials.$user-$host
