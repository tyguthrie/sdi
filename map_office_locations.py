# Maps TNC office location data

# Parameters
textfile = "c:/temp/officedata.txt"
csvfile = "c:/temp/officedata.csv"
dbffile = "c:/temp/officedata.dbf"
gp.workspace = "Database Connections/SDELOADER.COSDE.DEFAULT.sde"
url = "http://home.tnc/staffdirectory/LoadAllintoExcel"
today = strftime("%Y%m%d")

# Retrieve the online source dataset
src = urllib.urlretrieve(url,textfile)

# Convert the html file to csv format by replacing html tags
# also remove spaces from field names, assumed to be first line
txtstr = ""
txtline = ""
firstline = True
readfile = open(textfile,'r')
writefile = open(csvfile,'w')
char = readfile.read(1)
while char:
    if not (firstline and char == " "):
        txtstr = txtstr + char
    if txtstr.find("<td>") > -1:
        txtstr = ""
        txtline = txtline + '"'
    elif txtstr.find("</td>") > -1:
        txtstr = txtstr.replace("</td>",'",')
        txtline = txtline + txtstr
        txtstr = ""
    elif txtstr.find("</tr>") > -1:
        txtline = txtline.rstrip(",")
        txtline = txtline + "\r"
        writefile.write(txtline)
        txtline = ""
        txtstr = ""
        firstline = False
    char = readfile.read(1)

# close and delete these objects, otherwise geoprocessing will be unable to access
readfile.close
del readfile
writefile.close
del writefile

# copy csvfile to dbf file
gp.CopyRows_management(csvfile, dbffile)

# Add numeric fields to represent lat and long, staff size and date stamp
gp.AddField_management(dbffile, "lat", "DOUBLE")
gp.AddField_management(dbffile, "long", "DOUBLE")
gp.AddField_management(dbffile, "staff", "DOUBLE")
gp.AddField_management(dbffile, "updated", "TEXT")

# copy lat long values to numeric fields
gp.CalculateField_management(dbffile, "lat", "[Latitude]")
gp.CalculateField_management(dbffile, "long", "[Longitude]")
gp.CalculateField_management(dbffile, "staff", "[staffsize]")
gp.CalculateField_management(dbffile, "updated", today)

# Make XY Event Layer
gp.MakeXYEventLayer_management(dbffile, "long", "lat", "lyr")

# convert to feature class
gp.FeatureclassToFeatureclass_conversion("lyr", gp.workspace, "TNCOffices")

# set the coordinate
coordsys = "Coordinate Systems\Geographic Coordinate Systems\World\WGS 1984.prj"
gp.DefineProjection_management("TNCOffices", coordsys)

# assign privileges
gp.ChangePrivileges_management("TNCOffices", "TNC_VIEWER", "GRANT")
