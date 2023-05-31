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

for bucketname in $user-$host-uci-bkup-bucket $user-$host-uci-inventory
do
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
done

# put bucket policy for inventory bucket
cat template-inventory-permissions.json | \
sed s/xxxuserxxx/$user/ | \
sed s/xxxhostxxx/$host/ > $user-$host-inv-perm.json

aws --profile $awsprofile s3api put-bucket-policy --bucket $user-$host-uci-inventory --policy file://$user-$host-inv-perm.json

# put inventory configuration on the primary bucket
cat template-inventory-configuration.json | \
sed s/xxxuciawsacctxxx/$uciawsacct/ | \
sed s/xxxuserxxx/$user/ | \
sed s/xxxhostxxx/$host/ > $user-$host-inv-cfg.json

aws --profile $awsprofile s3api put-bucket-inventory-configuration --bucket $user-$host-uci-bkup-bucket --id 1 --inventory-configuration file://$user-$host-inv-cfg.json

# create service account access policy
cat template-policy2.json | \
sed s/xxxuciawsacctxxx/$uciawsacct/ | \
sed s/xxxuserxxx/$user/ | \
sed s/xxxhostxxx/$host/ > $user-$host-policy.json

aws --profile $awsprofile iam create-policy --policy-name $user-$host-uci-bkup-policy  --policy-document file://$user-$host-policy.json

aws --profile $awsprofile iam create-user --user-name $user-$host-sa

aws --profile $awsprofile iam attach-user-policy --user-name $user-$host-sa --policy-arn arn:aws:iam::${uciawsacct}:policy/$user-$host-uci-bkup-policy

aws --profile $awsprofile iam create-access-key --user-name $user-$host-sa | tee credentials.$user-$host
