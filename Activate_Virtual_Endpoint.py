import os
import json
import re

from cloudshell.api.cloudshell_api import CloudShellAPISession, InputNameValue
import requests

resource = json.loads(os.environ["RESOURCECONTEXT"])
reservation = json.loads(os.environ["RESERVATIONCONTEXT"])
connectivity = json.loads(os.environ["QUALICONNECTIVITYCONTEXT"])

csapi = CloudShellAPISession(connectivity["serverAddress"], connectivity["adminUser"], connectivity["adminPass"], reservation["domain"])
resid = reservation["id"]
rd = csapi.GetReservationDetails(resid).ReservationDescription

sv_user = 'admin'
sv_password = 'admin'

sv_start_url = resource['attributes']['Web Interface']
sv_ip = re.search(r'://([^:/]*)[/:]', sv_start_url).groups()[0]

sv_base_url = sv_start_url.replace('actions/start', '')
r = requests.get(sv_base_url, auth=(sv_user, sv_password))

if r.status_code >= 400:
    raise Exception('Failed to query virtual service %s: %d: %s' % (sv_base_url, r.status_code, r.text))

port = re.search(r'<ResourceName>(\d+)', r.text).groups()[0]

r = requests.post(sv_start_url, auth=(sv_user, sv_password))
# if r.status_code >= 400:
#     raise Exception('Failed to start virtual service %s: %d: %s' % (sv_start_url, r.status_code, r.text))

for r in rd.Resources:
    if 'Apache' in r.Name:
    # for ra in csapi.GetResourceDetails(r.Name).ResourceAttributes:
    #     if ra.Name == 'Web Interface':
    #         if ra.Value == '':
        csapi.ExecuteCommand(resid, r.Name, 'Resource', 'Configure_Service_Endpoint', [
            InputNameValue('Endpoint', 'http://%s:%s' % (sv_ip, port)),
        ], True)

csapi.Logoff()

print 'Virtualized SalesForce endpoint: %s:%s' % (sv_ip, port)
