#! /usr/bin/python3

import argparse
import boto3
import os
import sys
import yaml

with open( "config/aws-settings.yaml", "r" ) as f:
    aws = yaml.safe_load( f )


usage=""
p = argparse.ArgumentParser( description=usage )
p.add_argument( "user",
        help="user UCInetID" )
p.add_argument( "host",
        help="hostname" )
args = p.parse_args()

# override location of .aws/config
if "configfile" in aws:
    os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]

session = boto3.Session( profile_name=aws[ "profile" ] )

athena_client = session.client( "athena" )
# create the work group
try:
    response = athena_client.create_work_group(
        Name=args.user,
        Configuration={
            'ResultConfiguration': {
                'OutputLocation': aws[ "reports" ] + "/" + args.user
            },
            'EnforceWorkGroupConfiguration': False,
            'PublishCloudWatchMetricsEnabled': True
        }
    )
except athena_client.exceptions.InvalidRequestException:
    pass

# create database in default collection
response = athena_client.start_query_execution( 
    QueryString="create database if not exists {}".format( args.user ),
    WorkGroup=args.user
)

loadschema = "CREATE EXTERNAL TABLE cncm( \
  bucketname string, \
  filename string, \
  version_id string, \
  is_latest boolean, \
  is_delete_marker boolean, \
  filesize bigint, \
  last_modified_date string, \
  storage_class string \
) \
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde' \
STORED AS INPUTFORMAT 'org.apache.hadoop.hive.ql.io.SymlinkTextInputFormat' \
OUTPUTFORMAT  'org.apache.hadoop.hive.ql.io.IgnoreKeyTextOutputFormat' \
LOCATION 's3://awxu-cncm-uci-inventory/awxu-cncm-uci-bkup-bucket/awxu-cncm-daily/hive/dt=2023-07-04-01-00/' ;"

#print( schema )
# load hive schema into table
response = athena_client.start_query_execution( 
    QueryString=loadschema,
    QueryExecutionContext={
        'Database': args.user
    },
    WorkGroup=args.user
)
print( response[ "QueryExecutionId" ] )