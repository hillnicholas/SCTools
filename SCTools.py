import os, subprocess, csv
import securitycenter, getpass
import sys



# unnecessary fancy stuff
def __print_status( current, total, length ):
    no_of_equs = int( ( length * current ) /total )
    bar_out = "=" * no_of_equs
    end_bar = " " * ( length - no_of_equs - 2 )
    percentage = ( 100 * current ) / total
    # last one should be 100
    if total - current == 1:
        percentage = 100
    sys.stdout.write( "\r[" + bar_out + end_bar + "]" + str(percentage) + "%" )
    sys.stdout.flush()
    if percentage == 100: print 


# combines usable and manageable unless specified otherwise, and returns
# a list.
def __combine_usable_and_manageable( raw_data, usable=True, manageable=True ):
    final_data = list()
    # first, add key fields at top
    for key in raw_data.keys():
        # check if field is asked for
        if ( key == "usable" and usable ) or \
           ( key == "manageable" and manageable ):
            # add field to show usable or managable
            nested_data = raw_data[key]
            # add to a main list
            for row in nested_data:
                row["access"] = key
                final_data.append( row )
    return final_data


# get all data, use verbose flag to show when each request completes
def get_all( session, verbose = False ):

    def status( status):
        if verbose: print status
        
    data = dict()
    status("getting scan results...")
    data["scan results"] = get_scan_results( session)
    status("getting assets..." )
    data["assets"] = get_assets( session )
    status("getting users...")
    data["users"] = get_users( session )
    status("getting repositories...")
    data["repositories"] = get_repositories( session )
    status("getting groups...")
    data["groups"] = get_groups( session )
    status("getting scans...")
    data["scans"] = get_scans( session )
    return data


# export function, which operates as a wrapper. returns a list of maps ( dict() ) for each row
def export( command, fields, session ):
    return session.get( command,  params ={"fields" : ",".join(fields) } ).json()["response"]


# returns scan results. 
def get_scan_results( session ,usable=True, manageable=True ):
    raw_data = export( "scanResult", ['canUse', 'canManage', 'owner', 'groups', \
                                              'ownerGroup', 'status', 'name', 'details', \
                                              'importStatus', 'createdTime', 'startTime', \
                                              'finishTime', 'importStart', 'importFinish', \
                                              'running', 'totalIPs', 'scannedIPs', \
                                              'completedIPs', 'completedChecks', 'totalChecks',\
                                              'downloadAvailable', 'downloadFormat', 'repository',\
                                              'resultType', 'resultSource', 'scanDuration'],
                                               session )
    return __combine_usable_and_manageable( raw_data, usable=usable, manageable=manageable )


# returns a list of dicts with all assets.
def get_assets( session, usable=True, manageable=True ):
    raw_data =  export( "asset", ["name","groups","typeFields", \
                                  "type","ipCount","tags"], session )
    return __combine_usable_and_manageable( raw_data, usable=usable, manageable=manageable )


# returns a list of dicts with all scans. Usable and managable are mixed
# together unless optional flags are raised.
def get_scans( session, usable=True, manageable=True ):
    raw_data = export( "scan", ['id', 'name','canUse', 'canManage', 'owner', 'groups', 'ownerGroup',\
                                        'status', 'createdTime', 'schedule', 'policy',\
                                        'plugin', 'type', 'repository','assets','ipList'] , session )
    return __combine_usable_and_manageable( raw_data, usable=usable, manageable=manageable )


# returns users.
def get_users( session ):
    raw_data = export( "user", ["name","username","firstname","lastname", \
                                        "group.name","role","lastLogin","canManage","canUse", \
                                        "locked","status","title","email"], session )
    return raw_data


# returns a list of dicts with all groups. 
def get_groups( session ):
    raw_data = export( "group",["name","assets","definingAssets"], session )
    return raw_data


# returns the repository data
def get_repositories( session ):
    raw_data = export( "repository", ['name', 'description', 'type', 'dataFormat', \
                                              'vulnCount', 'remoteID', 'remoteIP', 'running', \
                                              'enableTrending', 'downloadFormat', 'lastSyncTime', \
                                              'lastVulnUpdate', 'createdTime', 'modifiedTime', \
                                              'organizations', 'correlation', 'nessusSchedule', \
                                              'ipCount', 'runningNessus', \
                                              'lastGrenerateNessusTime', 'running', 'transfer', \
                                              'deviceCount', 'typeFields.ipRange'],
                                               session )
    return raw_data

'''
def get_asset_vulnerabilities( session):
    raw_data = session.post( "analysis", params = {
'''

# makes the HTTP POST request for the logs and returns the JSON response
def get_logs( session, datestring, no_of_logs=500 ):
    '''
    # severity IDs:
    # 2 - critical
    # 1 - warning
    
    JSON filter definition for severity logs:

    {"id":"severityLogs",
     "filterName":"severity",
     "operator":"=",
     "type":"scLog",
     "value":{"id" }
     
    '''
    response = session.post( "analysis", json={"query":
                                                {"name":"",
                                                 "description":"",
                                                 "context":"",
                                                 "status":-1,
                                                 "createdTime":0,
                                                 "modifiedTime":0,
                                                 "groups":[],
                                                 "type":"scLog",
                                                 "tool":"scLog",
                                                 "sourceType":"",
                                                 "startOffset":0,
                                                 "endOffset": no_of_logs,
                                                 "filters":[{"id":"date",
                                                             "filterName":"date",
                                                             "operator":"=",
                                                             "type":"scLog",
                                                             "isPredefined":True,
                                                             "value":{"id": datestring }
                                                             },
                                                            {"id":"organization",
                                                             "filterName":"organization",
                                                             "operator":"=",
                                                             "type":"scLog",
                                                             "isPredefined":True,
                                                             "value":{"id":"0"}
                                                             }],
                                                 "sortColumn":"date",
                                                 "sortDirection":"desc"
                                                 },
                                                "sourceType":"scLog",
                                                "sortField":"date",
                                                "sortDir":"desc",
                                                "columns":[],
                                                "type":"scLog",
                                                "date":201706}
                            ).json()["response"]
    logs = response["results"]
    return logs


# testing/debug
if __name__ == "__main__":
    HOST = raw_input("Host: ") if len(sys.argv) < 2 else sys.argv[1]
    session = securitycenter.SecurityCenter5( HOST )
    session.login(raw_input("username: " ), getpass.getpass() )
    data = get_all( session, verbose=True )
    



