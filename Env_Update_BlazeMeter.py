import os
import json

from cloudshell.api.cloudshell_api import CloudShellAPISession, InputNameValue

reservation = json.loads(os.environ["RESERVATIONCONTEXT"])
connectivity = json.loads(os.environ["QUALICONNECTIVITYCONTEXT"])

csapi = CloudShellAPISession(connectivity["serverAddress"], connectivity["adminUser"], connectivity["adminPass"], reservation["domain"])
resid = reservation["id"]
rd = csapi.GetReservationDetails(resid).ReservationDescription

for r in rd.Resources:
    if 'balancer' in r.Name.lower():
        for ra in csapi.GetResourceDetails(r.Name).ResourceAttributes:
            if ra.Name == 'Web Interface':
                print 'Load balancer updated to %s' % ra.Value

csapi.Logoff()
