import os
import json
from time import sleep

from cloudshell.api.cloudshell_api import CloudShellAPISession, InputNameValue
import requests

if 'RESOURCECONTEXT' in os.environ:
    env = os.environ
    resource = json.loads(env["RESOURCECONTEXT"])
    reservation = json.loads(env["RESERVATIONCONTEXT"])
    connectivity = json.loads(env["QUALICONNECTIVITYCONTEXT"])
else:
    # env = {
        # 'TEST_ID': '5591046',
        # 'TARGET_URL': 'https://chat.eggma.org/2.html',
        # 'BLAZEMETER_KEY': '070fc2852f06cd1c3edd6fb9',
        # 'BLAZEMETER_SECRET': 'bdfcc5fddebb01593bc36bcf7de1dcc46111a092fee62f456aff5863917041fad9ba954f',
    # }
    connectivity = {
        'serverAddress': 'localhost',
        'adminUser': 'admin',
        'adminPass': 'admin',
    }
    reservation = {
        'domain': 'Global',
    }

csapi = CloudShellAPISession(connectivity["serverAddress"], connectivity["adminUser"], connectivity["adminPass"], reservation["domain"])
resid = reservation["id"]
res = csapi.GetReservationDetails(resid).ReservationDescription

csapi.WriteMessageToReservationOutput(resid, '1')


a2b = {}
for conn in res.Connectors:
    if conn.Source not in a2b:
        a2b[conn.Source] = []
    a2b[conn.Source].append(conn.Target)
    if conn.Target not in a2b:
        a2b[conn.Target] = []
    a2b[conn.Target].append(conn.Source)

# csapi.WriteMessageToReservationOutput(resid, 'a2b=%s' % str(a2b))

targetname2url = {}
for conn in res.Connectors:
    target = ''
    if resource['name'] == conn.Source:
        target = conn.Target
    if resource['name'] == conn.Target:
        target = conn.Source
    if target:
        targetname2url[target] = [a.Value for a in csapi.GetResourceDetails(target).ResourceAttributes if a.Name == 'Web Interface'][0]

key = '070fc2852f06cd1c3edd6fb9'
secret = 'bdfcc5fddebb01593bc36bcf7de1dcc46111a092fee62f456aff5863917041fad9ba954f'

# csapi.WriteMessageToReservationOutput(resid, 'key=%s target2url=%s' % (key, str(targetname2url)))


jtests = requests.get('https://a.blazemeter.com/api/latest/tests', auth=(key, secret)).text
dtests = json.loads(jtests)

# csapi.WriteMessageToReservationOutput(resid, 'tests: %s' % jtests)

sessionid2targetname = {}

for dtest in dtests['result']:
    for targetname in targetname2url:
        if targetname in dtest['name'] or dtest['name'] in targetname:
            testid = dtest['id']

            csapi.WriteMessageToReservationOutput(resid, 'Located test %s matching resource %s; getting test details...' % (testid, targetname))
            jtest = requests.get('https://a.blazemeter.com/api/latest/tests/%s' % testid, auth=(key, secret)).text
            # csapi.WriteMessageToReservationOutput(resid, 'Details: %s' % jtest)
            dtest = json.loads(jtest)
            dtest['result']['configuration']['plugins']['http']['pages'][0]['url'] = targetname2url[targetname]
            dtest2 = {
                'name': dtest['result']['name'],
                'configuration': dtest['result']['configuration'],
            }
            csapi.SetResourceLiveStatus(targetname, 'Error', 'Server overloaded')

            csapi.WriteMessageToReservationOutput(resid, 'Target: %s' % targetname)

            for b in a2b[targetname]:
                # csapi.WriteMessageToReservationOutput(resid, 'Considering %s' % b)
                if b != resource['name'] and not b.endswith('/' + resource['name']):
                    # csapi.WriteMessageToReservationOutput(resid, 'Connected to %s' % b)
                    csapi.SetResourceLiveStatus(b, 'Error', 'Server overloaded')


            csapi.WriteMessageToReservationOutput(resid, 'Writing URL %s to test %s' % (targetname2url[targetname], testid))
            rp = requests.put('https://a.blazemeter.com/api/latest/tests/%s' % testid,
                              auth=(key, secret),
                              headers={'Content-Type': 'application/json'},
                              data=json.dumps(dtest2))

            jlaunch = requests.post('https://a.blazemeter.com/api/latest/tests/%s/start' % testid, auth=(key, secret)).text
            dlaunch = json.loads(jlaunch)
            sessionid = dlaunch['result']['sessionsId'][0]
            sessionid2targetname[sessionid] = targetname

            jstat = requests.get('https://a.blazemeter.com/api/latest/sessions/%s' % sessionid, auth=(key, secret)).text
            dstat = json.loads(jstat)
            csapi.WriteMessageToReservationOutput(resid, 'BlazeMeter session %s status 2: %s' % (sessionid, dstat['result']['status']))

            projectid = dstat['result']['projectId']
            masterid = dstat['result']['masterId']
            juser = requests.get('https://a.blazemeter.com/api/latest/user', auth=(key, secret)).text
            duser = json.loads(juser)
            accountid = duser['defaultProject']['accountId']
            workspaceid = duser['defaultProject']['workspaceId']

            jtoken = requests.post('https://a.blazemeter.com/api/v4/masters/%s/public-token' % masterid, auth=(key, secret)).text
            dtoken = json.loads(jtoken)
            publictoken = dtoken['result']['publicToken']

            reporturl = 'https://a.blazemeter.com/app/?public-token=%s#/accounts/%s/workspaces/%s/projects/%s/masters/%s/summary' % (publictoken, accountid, workspaceid, projectid, masterid)
            csapi.WriteMessageToReservationOutput(resid, 'Report: %s' % reporturl)
            print sessionid + ':' + targetname

# for rsrc in res.Resources:
#     if 'SalesForce' in rsrc.Name:
#         for _ in range(10):
#             csapi.ExecuteCommand(resid, rsrc.Name, 'Resource', 'Add_User_to_SalesForce', [
#                 InputNameValue('First_Name', 'Blaze'),
#                 InputNameValue('Last_Name', 'Meter'),
#                 InputNameValue('Company', 'CA'),
#             ], True)


csapi.Logoff()
