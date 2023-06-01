#! /bin/sh

if [ $# -ne 2 ] ; then
    echo $0 user host
    exit 0
fi

outputs="outputs"
templates="templates"

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
cat $templates/template-inventory-permissions.json | \
sed s/xxxuserxxx/$user/ | \
sed s/xxxhostxxx/$host/ > $outputs/$user-$host-inv-perm.json

aws --profile $awsprofile s3api put-bucket-policy --bucket $user-$host-uci-inventory --policy file://$outputs/$user-$host-inv-perm.json

# put inventory configuration on the primary bucket
cat $templates/template-inventory-configuration.json | \
sed s/xxxuciawsacctxxx/$uciawsacct/ | \
sed s/xxxuserxxx/$user/ | \
sed s/xxxhostxxx/$host/ > $outputs/$user-$host-inv-cfg.json

aws --profile $awsprofile s3api put-bucket-inventory-configuration --bucket $user-$host-uci-bkup-bucket --id $user-$host-daily --inventory-configuration file://$outputs/$user-$host-inv-cfg.json

# put the lifecycle policy into the bucket for storage transititions and permanent deletions

aws --profile $awsprofile s3api put-bucket-lifecycle-configuration --bucket $user-$host-uci-bkup-bucket --lifecycle-configuration file://$templates/lifecycle-all.json

# create service account access policy
cat $templates/template-policy2.json | \
sed s/xxxuciawsacctxxx/$uciawsacct/ | \
sed s/xxxuserxxx/$user/ | \
sed s/xxxhostxxx/$host/ > $outputs/$user-$host-policy.json

aws --profile $awsprofile iam create-policy --policy-name $user-$host-uci-bkup-policy  --policy-document file://$outputs/$user-$host-policy.json

aws --profile $awsprofile iam create-user --user-name $user-$host-sa

aws --profile $awsprofile iam attach-user-policy --user-name $user-$host-sa --policy-arn arn:aws:iam::${uciawsacct}:policy/$user-$host-uci-bkup-policy

aws --profile $awsprofile iam create-access-key --user-name $user-$host-sa | tee $outputs/$user-$host.credentials
