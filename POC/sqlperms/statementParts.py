# Various Templates for creating an AWS Policy 

## Components that make up a single statement in list of statements for a policy 

spartTemplate= '''            
         {{
            "Sid": "{SID}",
            "Effect": "{EFFECT}",
            "Action": [
                {ACTIONLIST}
            ]
            {RESOURCE}
            {PRINCIPAL}
            {CONDITION}
         }}
'''

## These are parts of a single statement
resourceTemplate = '''
            ,
            "Resource" : [
                    {RESOURCELIST}
            ] 
'''
conditionTemplate = '''
            ,
            "Condition" : [ 
                    {CONDITIONLIST}
            ]
'''
principalTemplate = '''
            ,
            "Principal" : [ 
                    [ {PRINCIPALLIST} ]
            ] 
'''            
## This is the template for the JSON policy
## STATEMENTLIST is a comma-joined string of filled statement Parts
jsonTemplate = '''
{{
    "Version": "2012-10-17",
    "Statement": [
        {STATEMENTLIST}
    ]
}}
'''
