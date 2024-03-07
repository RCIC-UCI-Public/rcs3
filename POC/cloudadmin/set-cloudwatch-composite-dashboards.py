#! /usr/bin/env python3
# This is similar to  set-cloudwatch-dashboards.py but the dashboard structure 
# has an outer and inner (iterative) part.

# The inner part is repeated a variable number of times - since there is no real structure in AWS to
# define something from a list, we have to build out the full JSON in "klutzy/kludgey" way.
# The inner iteration is driven from the quotas csv file used to set quotas.
 
import argparse
import boto3
import os
import sys
import yaml
import json
import csv

scriptdir=os.path.realpath(os.path.dirname(__file__))
sys.path.append(os.path.join(scriptdir,"..","common"))
import rcs3functions as rcs3

def main(argv):
    scriptdir=os.path.realpath(os.path.dirname(__file__))
    configdir=os.path.normpath(os.path.join(scriptdir, "..","config"))
    templatedir=os.path.normpath(os.path.join(scriptdir, "..","templates","dashboards"))

    aws=rcs3.read_aws_settings()
    
    usage="Create Composite dashboards"
    helpquotafile = "Override default quota file (quotas.csv)"
    p = argparse.ArgumentParser( description=usage )
    p.add_argument("-f", "--file",   dest="quotafile", default="quotas.csv", help=helpquotafile)
    p.add_argument("-d", "--dry-run",   dest="dryrun",  default=False, action='store_true')
    args = p.parse_args()

    if len(os.path.dirname(args.quotafile)) == 0:
        qfile = os.path.join(configdir,args.quotafile)
    else:
        qfile = args.quotafile

    # Read the quotas file and just retrieving owner,system
    with rcs3.TextIgnoreCommentsWrapper(qfile) as fw:
        csv_reader = csv.reader(fw,skipinitialspace=True)
        header = next(csv_reader)
        systems = [ row[0:2] for row in csv_reader]
    systems.sort()
   
    # override location of .aws/config
    if "configfile" in aws:
        os.environ[ "AWS_CONFIG_FILE" ] = aws[ "configfile" ]
    
    session = boto3.Session( profile_name=aws[ "profile" ] )
    cw_client = session.client( "cloudwatch" )

    ## Construct each composite dashboard
    for dashboard in aws["cloudwatch_dashboard_array"]:
        wrapper = dashboard["wrapper"]
        inner = dashboard["inner"]
        replacevar = dashboard["replacevar"]
        try:
            height = dashboard["height"]
        except:
            height = 1
        try:
            height2 = dashboard["height2"]
        except:
            height2 = 0
        systemplates = '{ "type":"text", "height": 1, "x": 0, "y": 0, "properties": { "markdown" : "**Systems Protected: %COUNT%**" }},\n'
        # Iterate through the system to build out the array of inner templates
        nsys = 0
        curY = 1

        for [owner,system] in systems:
            nsys += 1
            # HEIGHT and HEIGHT2 are how "tall" two different widgets are
            # The Y-location is computed
            #     Y first widget = curY
            #     Y of second widget = curY + height
            # curY += height+height2 after each iteration
            rvalues = { 
                "%LENS%" : aws["lens"],
                "%REGION%" : aws["region"],
                "%ACCOUNT%" : aws["accountid"],
                "%BUCKET%" :  aws["bucket_postfix"],
                "%OWNER%" : owner,
                "%SYSTEM%" : system,
                "%HEIGHT%" : str(height),
                "%HEIGHT2%" : str(height2),
                "%YLOC%" : str(curY),
                "%YLOC2%" : str(curY + height) }
  
            curY += height2 + height
            # read the inner template file and string replace using the rvalues dictionary
            # Append to the systemplates  string

            with open(os.path.join(templatedir,inner),"r") as ifile:
                 replaced = [ rcs3.replace_all(x,rvalues) for x in ifile.readlines()] 
                 s = "".join(replaced)
                 systemplates += s[:-1]
                 systemplates += ",\n"
                
        ## Now read the wrapper file and insert the iterated data above
        ## cut out the final ',\n' chars from the iteration above
        rvalues["%COUNT%"] = str(nsys)
        replaced = rcs3.replace_all(systemplates,rvalues)
        rvalues[replacevar] = replaced[:-2]

        with open(os.path.join(templatedir,wrapper),"r") as ofile:
             fullfile = [ rcs3.replace_all(x,rvalues) for x in ofile.readlines()] 

        ## String replacements done, convert to json and upload the dashboard
        fulljson = json.loads("".join(fullfile))
        if args.dryrun:
           for x in fullfile:
               print (x)
        else:
           put_dashboard(cw_client,fulljson)
 
def put_dashboard(cw,DASH):
    print("Putting Dashboard: ",DASH['DashboardName'], "into cloudwatch")
    # Common arguments (ignores anything superfluous in the MA dictionary) 
    dashargs = {
         'DashboardName' : DASH['DashboardName'],
         'DashboardBody' : json.dumps(DASH) } 
    
    
    cw.put_dashboard(**dashargs)


if __name__ == "__main__":
    main(sys.argv[1:])

