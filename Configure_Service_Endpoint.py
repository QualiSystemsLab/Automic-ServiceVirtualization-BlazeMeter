import os
import json

from cloudshell.api.cloudshell_api import CloudShellAPISession

resource = json.loads(os.environ["RESOURCECONTEXT"])
reservation = json.loads(os.environ["RESERVATIONCONTEXT"])
connectivity = json.loads(os.environ["QUALICONNECTIVITYCONTEXT"])

csapi = CloudShellAPISession(connectivity["serverAddress"], connectivity["adminUser"], connectivity["adminPass"], reservation["domain"])
resid = reservation["id"]
rd = csapi.GetReservationDetails(resid).ReservationDescription

url = resource['attributes']['Web Interface']

if 'salesforce' in os.environ['ENDPOINT']:
    url = url.replace('5002', '5001')
else:
    url = url.replace('5001', '5002')

csapi.SetAttributeValue(resource['name'], 'Web Interface', url)
csapi.SetAttributeValue(resource['name'], 'Comm_IP', os.environ['ENDPOINT'])

# print 'Endpoint of %s set to %s' % (resource['name'], os.environ['ENDPOINT'])

csapi.Logoff()