import os
import json

from cloudshell.api.cloudshell_api import CloudShellAPISession, InputNameValue

reservation = json.loads(os.environ["RESERVATIONCONTEXT"])
connectivity = json.loads(os.environ["QUALICONNECTIVITYCONTEXT"])

csapi = CloudShellAPISession(connectivity["serverAddress"], connectivity["adminUser"], connectivity["adminPass"], reservation["domain"])
resid = reservation["id"]
rd = csapi.GetReservationDetails(resid).ReservationDescription

for r in rd.Resources:
    if 'blaze' in r.Name.lower():
        csapi.ExecuteCommand(resid, r.Name, 'Resource', 'Start_Traffic', [], True)
        break

csapi.Logoff()
