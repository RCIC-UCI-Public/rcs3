def delete_user_keys( iam_client, acctname ):
    userkeys = iam_client.list_access_keys( UserName=acctname )
    #print( userkeys )
    
    for userkey in userkeys[ "AccessKeyMetadata" ]:
        #print( userkey[ "AccessKeyId" ] )
        iam_client.delete_access_key( UserName=acctname, AccessKeyId=userkey[ "AccessKeyId" ] )


def create_user_key( iam_client, acctname ):
    newkey = iam_client.create_access_key( UserName=acctname )
    # convert datetime object to text string, our next action is to save to file and
    # datatime object is unhelpful in this context
    dateobj = newkey[ "AccessKey" ][ "CreateDate" ]
    newkey[ "AccessKey" ][ "CreateDate" ] = dateobj.isoformat()
    # drop the ResponseMetadata info, not needed
    newkey.pop( "ResponseMetadata" )
    return newkey
    