# Updates the SDI inventory database with XMFAlerter Server status

# get the feature class
fc = "Database Connections/Connection to cogis.sde/tncgdb.SDE.sdi_nodes_current"

# get XMFAlerter data
url = 'http://hedgehog.tnc.org:11080/geoxmf/xmfalerterServices?cmd=xmlalertstatus'
response = urllib2.urlopen(url).read()
dom = parseString(response)
XMFAlerterTag = dom.getElementsByTagName('XMFALERTER')[0]
AlertTags = dom.getElementsByTagName('ALERT')

# for each Alert record update the matching feature table record
for Tag in AlertTags:
    
    # update the feature class
    query = '"XMFID" = ' + "'" + Tag.getAttribute('id') + "'"
    rows = arcpy.UpdateCursor(fc, query)
    for row in rows:
        row.XMFName = Tag.getAttribute('name')
        row.XMFTime = XMFAlerterTag.getAttribute('servertime')
        row.XMFNotifyStatus = Tag.getAttribute('notifystatus')
        row.XMFState = Tag.getAttribute('state')
        row.XMFNextRun = Tag.getAttribute('nextrun')
        rows.updateRow(row)

del row
del rows
