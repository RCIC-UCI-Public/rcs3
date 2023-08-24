## Common Functions used in Shell Scripts
## These reference RCS3_ environment variables, assumed to be set
## Some expect user/host to be defined also.

# Set Some Variables
SCRIPTDIR=$(dirname $(realpath $0))

TEMPLATES_DIR=$SCRIPTDIR/../templates
CONFIG_DIR=$SCRIPTDIR/../config
OUTPUTS_DIR=$SCRIPTDIR/../outputs
COMMON_DIR=$SCRIPTDIR/../common

## Localize
function localize {
# need to replace patterns in generic files to localize
# localize <inputputfile> <outputfile>
   local input=$1
   local output=$2
   cat $input | \
   sed s/xxxawsacctxxx/$RCS3_ACCOUNTID/ | \
   sed -e s/xxxbucketxxx/$RCS3_BUCKET_POSTFIX/g -e s/xxxinventoryxxx/$RCS3_INVENTORY_POSTFIX/g | \
   sed -e s/xxxpolicyxxx/$RCS3_POLICY_POSTFIX/g  | \
   sed -e s/xxxlensxxx/$RCS3_LENS/g -e s/xxxlensbucketxxx/$RCS3_LENSBUCKET/g | \
   sed -e s/xxxregionxxx/$RCS3_REGION/g  | \
   sed s/xxxuserxxx/$user/ | \
   sed s/xxxhostxxx/$host/ > $output
}

function createbucket {

# call as createbucket <bucketname> <AWS>
# AWS is aws command usually with --profile 
   local bucketname=$1
   local AWS=$2
   $AWS s3api create-bucket --bucket $bucketname --region $RCS3_REGION --create-bucket-configuration LocationConstraint=$RCS3_REGION

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
}
