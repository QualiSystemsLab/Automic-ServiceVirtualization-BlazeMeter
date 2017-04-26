import os
import json

from cloudshell.api.cloudshell_api import CloudShellAPISession, InputNameValue

reservation = json.loads(os.environ["RESERVATIONCONTEXT"])
connectivity = json.loads(os.environ["QUALICONNECTIVITYCONTEXT"])

csapi = CloudShellAPISession(connectivity["serverAddress"], connectivity["adminUser"], connectivity["adminPass"], reservation["domain"])
resid = reservation["id"]
rd = csapi.GetReservationDetails(resid).ReservationDescription

for r in rd.Resources:
    if 'apache' in r.Name.lower():
        a = '192.168.1.5'
        b = '192.168.1.90'
        for ra in csapi.GetResourceDetails(r.Name).ResourceAttributes:
            if ra.Name == 'Web Interface':
                a = ra.Value
            if 'comm' in ra.Name.lower():
                b = ra.Value
        print 'Configured application server Leads Core to use endpoint %s' % b.replace('http://', '')
        break

csapi.Logoff()
