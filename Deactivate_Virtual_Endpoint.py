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

sv_start_ur2 = resource['attributes']['Web Interface']

sv_stop_url = sv_start_ur2.replace('start', 'stop')

sv_ip = re.search(r'://([^:/]*)[/:]', sv_stop_url).groups()[0]

r = requests.post(sv_stop_url, auth=(sv_user, sv_password))
# if r.status_code >= 400:
#     raise Exception('Failed to stop virtual service %s: %d: %s' % (sv_stop_url, r.status_code, r.text))

csapi.Logoff()

print 'Deactivated virtualized endpoint: %s' % sv_ip
