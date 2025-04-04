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
#  [--function=<lambda function> ]
#       Syntactic sugar to replace  -V '{ "FUNCTION": "<lambda function>" }'
# Example of creating a particular role for the scheduler to invoke a lambda (common)
#         create-role-with-policy keyAgeMetric-scheduler -p lambdaInvoke-policy -t schedulerAssumeRole-trust \
#                     -V '{"FUNCTION":"keyAgeMetric"} 
#         OR
#         create-role-with-policy keyAgeMetric-scheduler -p lambdaInvoke-policy -t schedulerAssumeRole-trust \
#                     --function=keyAgeMetric 
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

execdir = os.path.dirname(os.path.abspath(__file__))
basedir = os.path.dirname( execdir )
sys.path.append( os.path.join(basedir,"common" ))
sys.path.append( os.path.join(basedir, "sqlperms"))
import rcs3_awsperms
from rcs3functions import *

aws = read_aws_settings()
# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

usage="Create or update IAM policy with access to specific resources determined by name."
p = argparse.ArgumentParser( description=usage )
p.add_argument( "entity",
        help="basename of <entity>-role and <entity>-policy to create in AWS" )
p.add_argument("--function", dest="function", default=None,
        help="use to name a lambda function." )
p.add_argument( "-p", "--policy", dest="policydoc", default=None,
        help="Use DB policy instead of <entity>-policy" )
p.add_argument( "-t", "--trust", dest="trustdoc", default=None,
        help="Use DB trust instead of <entity>-trust" )
p.add_argument( "-V", "--variables", dest="variables", default=None,
        help="String rep of variable dictionary to add-to/override defaults" )
p.add_argument( "-v", "--verbose", action="store_true",
        help="optional print statements for more detail" )
args = p.parse_args()


# load the policy template 
db = rcs3_awsperms.rcs3awsdb(verbose=args.verbose)
input_policy = args.entity + "-policy" if args.policydoc is None else args.policydoc
input_trust = args.entity + "-trust" if args.trustdoc is None else args.trustdoc

j2vars = {
    "ACCOUNT": aws[ "accountid" ],
    "REGION": aws[ "region" ],
    "IP_ADDRESSES": aws[ "iprestrictions" ] 
}

if args.function is not None:
    j2vars["FUNCTION"] = args.function

if args.variables is not None:
    for k,v in json.loads(args.variables).items():
        j2vars[k] = v

# Read the policy and trust statements from the database, want jsonFormat
policyjson = db.document(setView="policy",setName=input_policy,j2Vars=j2vars,jsonFormat=True)
trustjson = db.document(setView="policy",setName=input_trust,j2Vars=j2vars, jsonFormat=True)
# Need string versions of JSON objects.
# Boto3 seems to be pedantic and not like additional whitespace. It really is simplest to have
# the db.document returned as a JSON object and then have json re-format it as string

policytxt = json.dumps(policyjson)
trusttxt = json.dumps(trustjson)

if args.verbose:
   print("=== Generated policy JSON ===")
   print(json.dumps(policyjson,indent=4))
   print("=== Generated trust JSON ===")
   print(json.dumps(trustjson,indent=4))

## Create boto3Clients. 
b3 = boto3Clients()
try:
    policy_arn = "arn:aws:iam::{}:policy/{}-policy"\
        .format( aws[ "accountid" ],args.entity )
    response = b3.IAM.list_policy_versions( PolicyArn=policy_arn )
    if args.verbose:
        print( response )
    if len( response[ "Versions" ] ) > 4:
        vid = response[ "Versions" ][ 4 ][ "VersionId" ]
        response = b3.IAM.delete_policy_version( PolicyArn=policy_arn, VersionId=vid )
    response = b3.IAM.create_policy_version(
        PolicyArn=policy_arn,
        PolicyDocument=policytxt,
        SetAsDefault=True
    )
except b3.IAM.exceptions.NoSuchEntityException:
    print( "Creating policy: {}".format( policy_arn ) )
    response = b3.IAM.create_policy(
        PolicyName="{}-policy".format( args.entity ),
        PolicyDocument=policytxt,
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
        response = b3.IAM.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=trusttxt,
            Description="Allow {} to process requests".format( args.entity )
        )
    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] == 'EntityAlreadyExists':
            policies = b3.IAM.list_attached_role_policies(RoleName=role_name)
            for policy in policies['AttachedPolicies']:
                b3.IAM.detach_role_policy(RoleName=role_name,PolicyArn=policy['PolicyArn'])
            if ( args.verbose ):
                print(policies)
                
    if args.verbose:
        print( response )

    response = b3.IAM.attach_role_policy(
        RoleName=role_name,
        PolicyArn=policy_arn
    )
    if args.verbose:
        print( response )
except Exception as error:
    print( type(error).__name__ )
    print( error )
    sys.exit( -1 )
