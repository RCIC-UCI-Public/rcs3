#! /usr/bin/env python3

import argparse
import boto3
import json
import os
import sys
import yaml
import zipfile

execdir = os.path.dirname(os.path.abspath(__file__))
basedir = os.path.dirname( execdir )
sys.path.append( os.path.join( basedir, "common" ) )

with open( os.path.join( basedir, "config", "aws-settings.yaml" ), "r" ) as f:
    aws = yaml.safe_load( f )

usage="Create or update lambda restore function"
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
p.add_argument( "purpose",
        help="which permissions to apply" )
p.add_argument( "-v", "--verbose", action="store_true",
        help="optional print statements for more detail" )
p.add_argument( "-t", "--timeout",
        help="override global timeout in aws-settings.yaml (seconds)" )
g = p.add_mutually_exclusive_group()
g.add_argument( "-p", "--policy_postfix",
        help="override policy postfix, substitute for purpose" )
g.add_argument( "-n", "--policy_name",
        help="override policy name, ignoring user, host, and purpose" )
args = p.parse_args()

scriptName = os.path.join( basedir, "scripts", "lambda-{}.py".format( args.purpose ) )
if not os.path.isfile( scriptName ):
    print( "Missing script: {}".format( scriptName ) )
    sys.exit( 1 )

if args.timeout is None:
    timeout = aws['lamba_timeout']
else:
    timeout = int(args.timeout)

# create zip file from script file
zipName = os.path.join( basedir, "outputs", args.purpose + ".zip" )
with zipfile.ZipFile( zipName, "w" ) as z:
    z.write( scriptName, "lambda_function.py" )

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
    lambda_client = session.client( "lambda", region_name=aws[ "region" ] )
    logs = session.client( "logs", region_name=aws[ "region" ] )
else:
    iam = session.client( "iam" )
    lambda_client = session.client( "lambda" )
    logs = session.client( "logs" )

# verify role has been created
if args.policy_name is None:
    if args.policy_postfix is None:
        roleName = "{}-{}-{}-role".format( args.user, args.host, args.purpose )
    else:
        roleName = "{}-{}-{}-role".format( args.user, args.host, args.policy_postfix )
else:
    roleName = args.policy_name
try:
    response = iam.get_role(
        RoleName = roleName
    )
    roleArn = response[ "Role" ][ "Arn" ]
    if args.verbose:
        print( response )
except iam.exceptions.NoSuchEntityException:
    print( "Create missing role: {}".format( roleName ) )
    sys.exit( 1 )
except Exception as error:
    print( type(error).__name__ )
    print( error )
    sys.exit( -1 )

# check for existing lambda function
try:
    with open( zipName, 'rb' ) as zipBinary:
        response = lambda_client.create_function(
            FunctionName="{}".format( args.purpose ),
            Description="{}-{}-{}".format( args.user, args.host, args.purpose ),
            Timeout=timeout,
            Runtime=aws[ "lambda_runtime" ],
            Role=roleArn,
            Handler=aws[ "lambda_handler" ],
            Code={ "ZipFile": zipBinary.read() },
            Publish=True,
            Tags={ 'rcs3user': args.user, 'rcs3host': args.host }
        )
    if args.verbose:
        print( response )
    try:
        logsGroupName = aws[ "lambda_log_nameprefix" ] + args.purpose
        logs.create_log_group( logGroupName=logsGroupName )
        logs.put_retention_policy(
            logGroupName=logsGroupName,
            retentionInDays=aws[ "lambda_log_retention" ]

        )
    except logs.exceptions.ResourceAlreadyExistsException:
        # not an error if CloudWatch log group already exists
        if args.verbose:
            print( "Using existing log group without changes: {}".format( logsGroupName ) )
        pass
    except Exception as error:
        print( type(error).__name__ )
        print( error )
        print( "CloudWatch log group not created: {}".format( logsGroupName ) )
except lambda_client.exceptions.ResourceConflictException:
    if args.verbose:
        print( "Updating lambda code" )
    try:
        with open( zipName, 'rb' ) as zipUpdate:
            response = lambda_client.update_function_code(
                FunctionName="{}".format( args.purpose ),
                ZipFile=zipUpdate.read(),
                Publish=True
            )
    except Exception as error:
        print( type(error).__name__ )
        print( error )
        sys.exit( -1 )
    if args.verbose:
        print( response )
except Exception as error:
    print( type(error).__name__ )
    print( error )
    sys.exit( -1 )

# clean up the temporary zip file
try:
    os.remove( zipName )
except OSError:
    pass
