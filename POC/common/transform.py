#! /usr/bin/env python3


# convert contents of template file name and write to output file name
# e.g.
# template_to_file( "templates/template-policy-write.json", "outputs/policy-write.json" )

def template_to_file( tname, oname ):
    with open( tname, "r" ) as fp:
        tf = fp.read()
        tf = tf.replace( "xxxuserxxx", "lopez" )
        tf = tf.replace( "xxxhostxxx", "fedaykin" )
        tf = tf.replace( "xxxbucketxxx", "uci-bkup-bucket")
    with open( oname, "w" ) as fp:
        fp.write( tf )


# convert contents of template file name to json format using an associative array
# e.g.
# mytable = {
#    "xxxuserxxx": "lopez",
#    "xxxhostxxx": "fedaykin",
#    "xxxbucketxxx": "uci-bkup-bucket"
# }
# jp = template_to_string( "templates/template-policy-write.json", mytable )

def template_to_string(tname, mytable ):
    with open( tname, "r" ) as fp:
        tf = fp.read()
    for k in mytable.keys():
        tf = tf.replace( k, mytable[ k ] )
    return tf


# create condition statement for policy from supplied list of IP addresses
# "IpAddress": { "aws:SourceIp": [ "d.d.d.d/d", "d.d.d.d/d" ] }
def createPolicyIpCondition( ipList ):
    condPrefix = "\"IpAddress\": { \"aws:SourceIp\": [ \""
    count = 0
    for ip in ipList:
        if count > 0:
            condPrefix += "\", \""
        condPrefix += ip
        count += 1
    condPrefix += "\" ] }"
    return condPrefix

