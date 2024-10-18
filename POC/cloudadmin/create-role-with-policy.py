#! /usr/bin/env python3
# Create a role with the defined policy
# input files:
#     Trust: <policy>-trust.json
#     Policy: <policy>-policy.json
#
#  Creates:
#      IAM policy
#      Create role <policy>-role
#      Add <policy>-trust to the created role
#
#  Example:
#      create-role-with-policy -d templates/keyAge  keyAgeMetric-scheduler-invoke
#
#   Creates the policy keyAgeMetric-scheduler-invoke-policy
#   Creates the role keyAgeMetric-scheduler-invoke-role
#   Attach policy keyAgeMetric-scheduler-invoke-policy to keyAgeMetric-scheduler-invoke-role
#   Add trust statement to the role so that it can be assumed by specific entities 
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
sys.path.append( basedir  + "/common" )
import transform

with open( basedir + "/config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )

usage="Create or update IAM policy with access to specific resources determined by name."
p = argparse.ArgumentParser( description=usage )
p.add_argument( "policy",
        help="which permissions to apply" )
p.add_argument( "-d", "--templatedir", dest="templatedir", default="templates/self-service",
        help="optional print statements for more detail" )
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
input_policy = basedir + "/{}/{}-policy.json".format( args.templatedir,args.policy )
if not os.path.isfile( input_policy ):
    print( "Not found: {}".format( input_policy ) )
    sys.exit( -1 )

input_trust = basedir + "/{}/{}-trust.json".format( args.templatedir,args.policy )
if not os.path.isfile( input_trust ):
    print( "Not found: {}".format( input_trust ) )
    sys.exit( -1 )

my_vars = {
    "%ACCOUNT%": aws[ "accountid" ],
    "%REGION%": aws[ "region" ],
    "%IPRESTRICTIONS%": transform.createPolicyIpCondition( aws[ "iprestrictions" ] )
}
json_policy = transform.template_to_string( input_policy, my_vars )
json_trust = transform.template_to_string( input_trust, my_vars )


# 1. Lookup Policy, Delete versions if too many, Create a new policy version OR create a new non-existing policy 
try:
    policy_arn = "arn:aws:iam::{}:policy/{}-policy"\
        .format( aws[ "accountid" ],args.policy )
    response = iam.list_policy_versions( PolicyArn=policy_arn )
    if args.verbose:
        print( response )
    if len( response[ "Versions" ] ) > 4:
        vid = response[ "Versions" ][ 4 ][ "VersionId" ]
        response = iam.delete_policy_version( PolicyArn=policy_arn, VersionId=vid )
    response = iam.create_policy_version(
        PolicyArn=policy_arn,
        PolicyDocument=json_policy,
        SetAsDefault=True
    )
except iam.exceptions.NoSuchEntityException:
    print( "Creating policy: {}".format( policy_arn ) )
    response = iam.create_policy(
        PolicyName="{}-policy".format( args.policy ),
        PolicyDocument=json_policy,
        Description="Allow {} access".format( args.policy )
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
    role_name = "{}-role".format( args.policy )
    try:
        response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json_trust,
            Description="Allow {} to process requests".format( args.policy )
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
