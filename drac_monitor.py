# tests SDI servers for DRAC connectivity
# emails result

import os
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.utils import COMMASPACE
from email.MIMEBase import MIMEBase
from email import Encoders

ips = [["10.201.33.91","cospatial"],
       ["10.23.1.21","arfoarcgis"],
       ["10.201.24.22","aztuc"],
       ["10.190.32.21","cobogospatial"],
       ["10.190.18.61","brasiliasde"],
       ["10.190.34.29","brbespatial"],
       ["10.201.29.236","carogis"],
       ["10.190.39.21","cnbejarcgis"],
       ["10.190.39.28","cnbejsde"],
       ["10.200.28.22","flfosde"],
       ["10.200.60.19","maspatial"],
       ["10.201.26.21","mnspatial"],
       ["10.200.24.29","ncspatial"],
       ["10.61.1.20","njdbospatial"],
       ["10.201.8.29","nvspatial"],
       ["10.201.8.27","nvfosim"],
       ["10.200.12.21","nyancsde"],
       ["10.200.33.21","nyspatial"],
       ["10.55.1.20","riarcgis"],
       ["10.200.43.21","scchsgis"],
       ["10.201.23.29","txfospatial"],
       ["10.201.25.26","waspatial"],
       ["10.201.33.231","costat"]]
log = "Results from pinging SDI DRAC ports\n"
log = log + "-------------------------------\n"
for ip in ips:
    response = os.system("ping -n 1 " + ip[0])
    if response == 0:
        log = log + ip[1] + ' is up\n'
    else:
        log = log + ip[1] + ' is not responding at IP address ' + ip[0] + '\n'


# build and send the email
fromaddr = "SDI@tnc.org"
toaddr = "tnc_sdi_admin@tnc.org"
msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "SDI DRAC Connectivity Status"
msg.attach(MIMEText(log, 'plain'))
server = smtplib.SMTP('smtpmail.tnc.org', 25)
text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
