import os
import json

from cloudshell.api.cloudshell_api import CloudShellAPISession, InputNameValue

# print os.environ


reservation = json.loads(os.environ["RESERVATIONCONTEXT"])
connectivity = json.loads(os.environ["QUALICONNECTIVITYCONTEXT"])

csapi = CloudShellAPISession(connectivity["serverAddress"], connectivity["adminUser"], connectivity["adminPass"], reservation["domain"])
resid = reservation["id"]
rd = csapi.GetReservationDetails(resid).ReservationDescription

for r in rd.Resources:
    if 'salesforce' in r.Name.lower():
    # for ra in csapi.GetResourceDetails(r.Name).ResourceAttributes:
    #     if ra.Name == 'Web Interface':
    #         if ra.Value == '':
        csapi.ExecuteCommand(resid, r.Name, 'Resource', 'Activate_Virtual_Endpoint', [
            # InputNameValue('Endpoint', 'http://%s:%s' % (sv_ip, port)),
        ], True)

csapi.Logoff()
