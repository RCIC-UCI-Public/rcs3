#! /bin/sh

if [ $# -ne 2 ] ; then
    echo $0 user host
    exit 0
fi

user=$1
host=$2
# RCIC AWS account
uciawsacct=774954368688
awsprofile=774954368688_AWSAdministratorAccess

bucketname=$user-$host-uci-bkup-bucket
#aws --profile $awsprofile s3api create-bucket --bucket $bucketname --object-lock-enabled-for-bucket --region us-west-2 --create-bucket-configuration LocationConstraint=us-west-2
aws --profile $awsprofile s3api create-bucket --bucket $bucketname --region us-west-2 --create-bucket-configuration LocationConstraint=us-west-2

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


cat template-policy.json | \
sed s/xxxuserxxx/$user/ | \
sed s/xxxhostxxx/$host/ > $user-$host-policy.json

aws --profile $awsprofile iam create-policy --policy-name $user-$host-uci-bkup-policy  --policy-document file://$user-$host-policy.json

aws --profile $awsprofile iam create-user --user-name $user-$host-sa

aws --profile $awsprofile iam attach-user-policy --user-name $user-$host-sa --policy-arn arn:aws:iam::${uciawsacct}:policy/$user-$host-uci-bkup-policy

aws --profile $awsprofile iam create-access-key --user-name $user-$host-sa | tee credentials.$user-$host
