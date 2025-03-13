#! /usr/bin/env python3
import sys
import json

def asList(element):
    t = type(element)
    if t is str:
        return [element,]
    if t is dict:
        return [ x for x in element.items() ]
    return element

jFile=sys.argv[1]

with open(jFile,"r") as f:
    theDoc = json.load(f)

print (theDoc)
for stmt in theDoc['Statement']:
    actVal = stmt['Action']
    for action in asList(actVal):
        (service,permission) = action.split(':')
        print(f"awspolicy.py add action {service} {permission}")
    asL = asList(actVal)
    asL.sort()
    print(f"Action Group : {asL}")
    try:
        for resource in asList(stmt['Resource']):
            print(f"awspolicy.py add resource xresourcex {resource}")
        asL = asList(stmt['Resource'])
        asL.sort()
        print(f"Resource Group : {asL}")
    except:
        pass
    try:
        for principal in asList(stmt['Principal']):
            print(f"awspolicy.py add principal xprincipalx {principal}")
        asL = asList(stmt['Principal'])
        asL.sort()
        print(f"Principal Group : {asL}")
    except:
        pass
    try:
        for condition in asList(stmt['Condition']):
            print(f"awspolicy.py add condition xconditionx {condition}")
        asL = asList(stmt['Condition'])
        asL.sort()
        print(f"Condition Group : {asL}")
    except:
        pass
