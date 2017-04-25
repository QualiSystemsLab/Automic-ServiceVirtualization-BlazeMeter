import os
import json
from random import randint
from time import sleep

from cloudshell.api.cloudshell_api import CloudShellAPISession

env = os.environ
resource = json.loads(env["RESOURCECONTEXT"])
reservation = json.loads(env["RESERVATIONCONTEXT"])
connectivity = json.loads(env["QUALICONNECTIVITYCONTEXT"])

csapi = CloudShellAPISession(connectivity["serverAddress"], connectivity["adminUser"], connectivity["adminPass"], reservation["domain"])
resid = reservation["id"]
res = csapi.GetReservationDetails(resid).ReservationDescription

s1 = 'POST %s {"FirstName":"%s","LastName":"%s","Company":"%s"}' % (resource['attributes']['Web Interface'], env['FIRST_NAME'], env['LAST_NAME'], env['COMPANY'])
csapi.WriteMessageToReservationOutput(resid, s1)
sleep(3)
s2 = 'Virtualized result: {"id":"%d","success":true,"errors":[]}' % randint(0, 1000000000)
csapi.WriteMessageToReservationOutput(resid, s2)

csapi.Logoff()

print s1+'\n'+s2