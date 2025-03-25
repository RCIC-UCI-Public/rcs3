#! /usr/bin/env python3
# Create a role with the defined policy
# This is uses the rcs3_awsperms.py database generate the json for 
#     Trust: <policy>-trust
#     Policy: <policy>-policy
#
#  Creates:
#      IAM policy
#      Create role <policy>-role
#      Add <policy>-trust to the created role
#
#  Simplest Example:
#      create-role-with-policy restore-s3batch-perms
#         o restore-s3batch-perms-[policy,trust] must exist in the local policy DB
#         o Creates the policy restore-s3batch-perms-policy in AWS
#         o Creates the role   restore-s3batch-perms-role in AWS
#         o Attaches the policy to the role
#         o Attaches the trust defined in restore-s3batch-perms-trust to the role 
#  
#  Optional arguments: 
#  [-p policy ]
#       Overrides the lookup of <policy>-trust in the database and instead looks up the
#       <policy>
#
#  [-t trust]
#       Overrides the lookup of <policy>-trust in the database and instead looks up the
#       <trust>
#
#  [-V <string rep of variable dictionary> ]
#       Jinja2 variables to add to (and/or overwrite) the default variables 
#
# Example of creating a particular role for the scheduler to invoke a lambda (common)
#         create-role-with-policy keyAgeMetric-scheduler -p lambdaInvoke-policy -t schedulerAssumeRole-trust \
#                     -V '{"FUNCTION":"keyAgeMetric"} 
#
#
#         o Creates the policy keyAgeMetric-scheduler-policy
#         o Creates the role   keyAgeMetric-scheduler-role
#         o Attaches the policy to the role
#         o Attaches schedulerAssumeRole-trust trust document to the role. 
#             This allows scheduler.amazonaws.com to assume the rrole defined
#     
import argparse
import botocore
import boto3
import json
import os
import sys
import yaml
from jinja2 import Template

execdir = os.path.dirname(os.path.abspath(__file__))
basedir = os.path.dirname( execdir )
sys.path.append( os.path.join(basedir,"common" ))
sys.path.append( os.path.join(basedir, "sqlperms"))
import rcs3_awsperms

with open( basedir + "/config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )

usage="Create or update IAM policy with access to specific resources determined by name."
p = argparse.ArgumentParser( description=usage )
p.add_argument( "entity",
        help="basename of <entity>-role and <entity>-policy to create in AWS" )
p.add_argument( "-p", "--policy", dest="policydoc", default=None,
        help="Use DB policy instead of <entity>-policy" )
p.add_argument( "-t", "--trust", dest="trustdoc", default=None,
        help="Use DB trust instead of <entity>-trust" )
p.add_argument( "-V", "--variables", dest="variables", default="",
        help="String rep of variable dictionary to add-to/override defaults" )
p.add_argument( "-v", "--verbose", action="store_true",
        help="optional print statements for more detail" )
args = p.parse_args()

# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

# when run from AWS services, profile is not used
if "profile" in aws:
    session = boto3.Session( profile_name=aws[ "profile" ] )
else:
    session = boto3

if "region" in aws:
    iam = session.client( "iam", region_name=aws[ "region" ] )
else:
    iam = session.client( "iam" )

# load the policy template 
db = rcs3_awsperms.rcs3awsdb()
input_policy = args.entity + "-policy" if args.policydoc is None else args.policydoc
input_trust = args.entity + "-trust" if args.trustdoc is None else args.trustdoc

jinja2vars = {
    "ACCOUNT": aws[ "accountid" ],
    "REGION": aws[ "region" ],
    "IP_ADDRESSES": aws[ "iprestrictions" ] 
}

for k,v in json.loads(args.variables).items():
    jinja2vars[k] = v

# Read the policy and trust statements from the database
# These might have jinja2 variables and might not parse as json
policydocGeneric = db.document(setView="policy",setName=input_policy)
trustdocGeneric = db.document(setView="policy",setName=input_trust)

# Render the docs using jinja2
policydoc=Template(policydocGeneric).render(jinja2vars)
trustdoc= Template(trustdocGeneric).render(jinja2vars)

# Make sure we have valid json before proceeding
policyjson=json.loads(policydoc)
trustjson=json.loads(trustdoc)
if args.verbose:
   print("=== Generated policy JSON ===")
   print(json.dumps(policyjson,indent=4))
   print("=== Generated trust JSON ===")
   print(json.dumps(trustjson,indent=4))

sys.exit(0)

# 1. Lookup Policy, Delete versions if too many, Create a new policy version OR create a new non-existing policy 
try:
    policy_arn = "arn:aws:iam::{}:policy/{}-policy"\
        .format( aws[ "accountid" ],args.entity )
    response = iam.list_policy_versions( PolicyArn=policy_arn )
    if args.verbose:
        print( response )
    if len( response[ "Versions" ] ) > 4:
        vid = response[ "Versions" ][ 4 ][ "VersionId" ]
        response = iam.delete_policy_version( PolicyArn=policy_arn, VersionId=vid )
    response = iam.create_policy_version(
        PolicyArn=policy_arn,
        PolicyDocument=policyjson,
        SetAsDefault=True
    )
except iam.exceptions.NoSuchEntityException:
    print( "Creating policy: {}".format( policy_arn ) )
    response = iam.create_policy(
        PolicyName="{}-policy".format( args.entity ),
        PolicyDocument=policyjson,
        Description="Allow {} access".format( args.entity )
    )
except Exception as error:
    print( type(error).__name__ )
    print( error )
    sys.exit( -1 )

if args.verbose:
    print( response )

# 2. Create the Role

# lookup an existing policy
try:
    role_name = "{}-role".format( args.entity )
    try:
        response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=trustjson,
            Description="Allow {} to process requests".format( args.entity )
        )
    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] == 'EntityAlreadyExists':
            policies = iam.list_attached_role_policies(RoleName=role_name)
            for policy in policies['AttachedPolicies']:
                iam.detach_role_policy(RoleName=role_name,PolicyArn=policy['PolicyArn'])
            if ( args.verbose ):
                print(policies)
                
    if args.verbose:
        print( response )

    response = iam.attach_role_policy(
        RoleName=role_name,
        PolicyArn=policy_arn
    )
    if args.verbose:
        print( response )
except Exception as error:
    print( type(error).__name__ )
    print( error )
    sys.exit( -1 )
