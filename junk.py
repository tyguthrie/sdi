# -*- coding: cp1252 -*-
# A collection of custom python classes and functions
# use as templates, or import the whole thing into your python project
################
# Tips:
# Use “feature layer” input to select layers within arcmap
# Filters can be used for validating parameters
# Multivalues - use python split function to create list
# do projection on the fly with search cursor using the spatial reference parameter
# Use testSchemaLock when updating features
# Use objects to set parameters where really long strings required such as spatial reference
# Use a value table instead of a long string for multivalue parameters
# Addfielddelimiters will create the appropriate delimiters for a workspace/fc/fieldname
# Use describe shapefieldname rather than [shape] in case it has a different name
# In services: use feature sets and record sets instead of feature classes
# In script use addToolbox to add the url of the services
# ArcSDESQLExecute object can access the database directly
# Write to scratch workspace when using services
# to see layer's data source: print arcpy.mapping.ListLayers(arcpy.mapping.MapDocument("CURRENT"))[i].dataSource
##################
# Essential GIS modules
# GDAL is a translator library with Python bindings that allows access to raster data using a unified abstract layer. Bundled with it is OGR, which provides similar functionality for vector data.
import gdal
from gdal const import* 
#Open the raster dataset
dataset=gdal.Open(filename,GA_ReadOnly)
#Print the projection of the data 
print dataset.GetProjection()    - 
# Using OGR
import ogr
# Get the driver
driver=ogr.GetDriverByName('ESRIShapefile')
#Open a shapefile
dataset=driver.Open(shapefileName,0)

# numpy is a package that enables n-dimensional array manipulation
from numpy import * 
#Sample IO Table data
ioSample=[[1,2],[3,4]]
#Turn into a numpy array
ioMatrix=array(ioSample)
#Find the inverse of ioMatrix
ioMatrixInv=linalg.inv(ioMatrix)

# NetworkX is a Python package for the creation, manipulation, and study of the structure, dynamics, and functions of complex networks
import networkx as nx
#Create a graph
g=nx.Graph()
#Populate the graph
g.add_node(1)
g.add_node(2)
g.add_node(3)
 
#Createedges
g.add_edge(1,2)
g.add_edge(1,3) 
#Print the neighbors of node 1(returns 2)
print g.neighbors(1)

#  xlrd is a Python module that allows one to read Excel files without the need of Microsoft Excel or Windows
import xlrd
#Open the Excel file
bok=xlrd.open_workbok("excelFile.xls")
#Read the first sheet in the Excel workbook
shet=bok.sheet_by_index(0)
#Read the first row from column A to E 
rowValues=shet.row_values(0,start_colx=0,end_colx=4)
#Print the row values
for value in row Values: print value

#  xlwt is a Python module that allows for cross platform Excel file creation without the need of Microsoft Office.
impor txlwt
#Create a new workbok
bok=xlwt.Workbok()
#Add a new sheet
shet=bok.ad_sheet("MySheet")
#Write the number 5 in the first row,first column
shet.write(0,0,5)
#Savethefile
bok.save("myExcelFile.xls")

# -----------------Prepare python and arcpy environment----------------------
# Import system modules
import arcpy, os, sys, string, zipfile, glob, urllib, os.path, xml.dom.minidom
from time import strftime
from xml.dom.minidom import parseString
from arcpy import env
env.overwriteOutput = True
gp.CheckOutExtension("Spatial")



def CLSImport(): # Loads CLS data into secured areas dataset

    # --------------------------Get input parameters-----------------------------
    cls = sys.argv[1]                               # CLS feature class
    cls_type = sys.argv[2]                          # type of CLS data ("TRACT" or "MA")
    safd = sys.argv[3]                              # SA feature dataset
    safc = sys.argv[4]                              # SA feature class
    xy_tolerance = str(sys.argv[5]) + " METERS"     # tolerance for geometry comparison

    # ----------------------Initialize datasets and variables--------------------
    x = 0
    geo_mismatch = 0
    match = 0
    new = 0
    update_IFMS = 0
    compare_file = gp.GetSystemEnvironment("temp") + "\\compare.txt"

    # create import error feature class (0)
    fc_error = safd + "\\import_errors"
    if not gp.exists(fc_error):
        gp.CreateFeatureClass_management(safd, "import_errors", "Polygon")
        gp.AddField_management(fc_error, "IFMS_ID", "LONG")
        gp.AddField_management(fc_error, "MOD_DATE", "DATE")
        gp.AddField_management(fc_error, "CLSTRANSDA", "DATE")
        gp.AddField_management(fc_error, "CLS_TYPE", "TEXT", "#", "#", 5)

    # load CLS feature class into secured areas feature
    # dataset so that same coordinate space is used (1)
    fc_temp = safd + "\\clsTemp"
    if gp.exists(fc_temp):
        gp.delete_management(fc_temp)
    gp.CopyFeatures_management(cls, fc_temp)
    total = gp.GetCount_management(fc_temp)
    gp.SetProgressor("step", "Processing record...", 0, total, 1)

    # populate with the current date and cls type
    gp.AddField_management(fc_temp, "MOD_DATE", "DATE")
    gp.AddField_management(fc_temp, "CLS_TYPE", "TEXT", "#", "#", 5)
    gp.CalculateField_management(fc_temp, "MOD_DATE", "now()")
    gp.CalculateField_management(fc_temp, "CLS_TYPE", '"' + cls_type + '"')

    # Open CLS feature class and go to first record (2)
    cur_cls = gp.SearchCursor(fc_temp)
    row_cls = cur_cls.Next()

    # ----------------------processing loop----------------------------------
    try:
        # for each record in the CLS feature class...
        while row_cls:
            gp.SetProgressorLabel("Processing record " + str(x+1) + " of " + str(total))
            gp.SetProgressorPosition(x+1)
            
            # create a selection from the CLS feature class (4)
            qry = '"IFMS_ID" = ' + str(int(row_cls.IFMS_ID)) + ' AND "CLS_TYPE" = '
            qry = qry + "'" + cls_type + "'"
            gp.MakeFeatureLayer_management(fc_temp, "lyrCLS", qry, safd)
            # if the IFMS_ID and type exists in SA... (5)
            gp.MakeFeatureLayer_management(safc, "lyrSA", qry, safd)
            if gp.GetCount_management("lyrSA"):
                # compare geometry of both selections
                gp.FeatureCompare_management("lyrSA", "lyrCLS", "IFMS_ID",
                                             "GEOMETRY_ONLY", "IGNORE_M;IGNORE_Z",
                                             xy_tolerance, 0, 0, "#", "#",
                                             "CONTINUE_COMPARE", compare_file)
                # if output table shows that the geometries match...(7)
                qry2 = '"Message"'
                qry2 = qry2 + " LIKE 'Geometries are different%'"
                gp.MakeTableView_management(compare_file, "tbl", qry2)
                if not gp.GetCount_management("tbl"):
                    gp.addmessage("Geometry, type and IFMS_ID match. No update needed")
                    match = match + 1
                else:
                    # copy features from CLS layer file to import error feature class (8)
                    gp.addmessage("Geometries do not match! Adding feature to import_errors.")
                    gp.Append_management("lyrCLS", fc_error, "NO_TEST")
                    geo_mismatch = geo_mismatch + 1
            # else update the SA feature class
            else:
                # create a layer from the entire SA
                gp.MakeFeatureLayer_management(safc, "lyrSA", "#", safd)
                # if there is an identical spatial match anywhere in SA... (9)
                gp.SelectLayerByLocation_management("lyrSA", "ARE_IDENTICAL_TO",
                                                    "lyrCLS", "#", "NEW_SELECTION")
                if gp.GetCount_management("lyrSA"):
                    # add IFMS_ID and CLS transaction date to the existing SA feature (10)
                    cur_sa = gp.UpdateCursor("lyrSA")
                    row_sa = cur_sa.Next()
                    gp.addmessage("Spatial match found. Updating IFMS_ID from "
                                  + str(row_sa.IFMS_ID) + " to " + str(row_cls.IFMS_ID))
                    row_sa.IFMS_ID = row_cls.IFMS_ID
                    if gp.ListFields(fc_temp,"CLSTRANSDA").Next():
                        if row_cls.CLSTRANSDA: row_sa.CLSTRANSDA = row_cls.CLSTRANSDA
                    row_sa.MOD_DATE = row_cls.MOD_DATE
                    row_sa.CLS_TYPE = cls_type
                    cur_sa.UpdateRow(row_sa)
                    update_IFMS = update_IFMS + 1
                # else copy entire feature to the SA feature class (11)
                else:
                    gp.addmessage("Feature not found in SA. Copying new feature from CLS")
                    gp.Append_management("lyrCLS", safc, "NO_TEST")
                    new = new + 1
            # move on to the next CLS record (3)
            x = x + 1
            row_cls = cur_cls.Next()
    except:
        gp.addmessage("Error encountered: stopping execution")
        gp.addmessage(gp.getmessages())

    # -----------------------report results (12)----------------------------------
    gp.addmessage("****** Finished! *********")
    gp.addmessage(str(x) + " CLS feature(s) processed.")
    if match: gp.addmessage(str(match) + " feature(s) already exist in SA feature class.")
    if update_IFMS: gp.addmessage(str(update_IFMS) + " SA feature(s) updated with new IFMS_ID.")
    if new: gp.addmessage(str(new) + " new feature(s) added to SA feature class.")
    if geo_mismatch: gp.addmessage(str(geo_mismatch) + " feature(s) not added due to geometry mismatch. See import_error feature class.")

    # -------------------------clean up (13)---------------------------------------
    gp.Delete_management(fc_temp)



def TNC_Lands_Sync(): # Syncs TNC lands data

    # get current date
    today = strftime("%Y%m%d")

    # parameters
    gp.workspace = 'D:/Ty/tooldata/TNC Lands Domains.mdb' # workspace and location of domains database
    tbl = "Database Connections/SDE.COSDE.DEFAULT.sde/replicas_fc" # replicas table
    gdb1 = "Database Connections/SDELOADER.COSDE.QA.sde" # parent geodatabase
    constring = "http://tncgis:zapata!@twitter.com/statuses/update.json" #twitter connection string


    # get the domains tables
    domains = gp.listtables()
    # open the replicas table
    uc = gp.UpdateCursor(tbl)
    row = uc.Next()

    while row:
        
        try: # synchronize datasets
            if row.sync == "X":
                # set the child default protection to public
                gp.AlterVersion_management(row.sde, "DEFAULT", "#", "#", "PUBLIC")
                # synch
                
                message = "synching " + row.replica
                tweet = urllib.urlencode({"status":message})
                f = urllib.urlopen(constring, tweet)
                gp.addmessage(message)
                
                gp.SynchronizeChanges_management(gdb1, row.replica, row.gdb2, row.direction, row.policy, row.definition)
                #set the child default protection to protected
                #gp.AlterVersion_management(row.sde, "DEFAULT", "#", "#", "PROTECTED")
                row.setvalue("result","pass")
                row.setvalue("syncdate",today)
        except:
            row.setvalue("result","fail")
            message = "Sync failed for " + row.replica
            tweet = urllib.urlencode({"status":message})
            f = urllib.urlopen(constring, tweet)
            gp.addmessage(message)
        
        try: # synchronize domains
            if row.sync == "X":
                for domain in domains:
                    message = "Synchronizing Domain " + domain
                    gp.addmessage(message)
                    gp.TableToDomain_management(domain, "code", "field", row.gdb2, domain, "#", "REPLACE")

        except:
            message = "Domain Sync Failed for domain: " + domain
            tweet = urllib.urlencode({"status":message})
            f = urllib.urlopen(constring, tweet)
            gp.addmessage(message)

        try: # reconcile and post for local editor versions
            if row.recpost == "X":
                # rec and post
                message = "reconcile and post " + row.version
                tweet = urllib.urlencode({"status":message})
                f = urllib.urlopen(constring, tweet)
                gp.addmessage(message)
                gp.reconcileversion_management(row.gdb2, row.version, "SDELOADER.QA", row.definition, "FAVOR_EDIT_VERSION", "NO_LOCK_AQUIRED","NO_ABORT", "POST")
                row.setvalue("result","pass")
                row.setvalue("syncdate",today)
        except:
            row.setvalue("result","fail")
            message = "rec and post failed for " + row.version
            tweet = urllib.urlencode({"status":message})
            f = urllib.urlopen(constring, tweet)
            gp.addmessage(message)

        try: # get count for gdb1
            result = gp.GetCount_management(gdb1+ "\\SDELOADER.TNC_LANDS")
            record_count = int(result.GetOutput(0))
            row.setvalue("GDB1_count",record_count)
        except:
            row.setvalue("GDB1_count","-1")

        try: # get count for gdb2
            result = gp.GetCount_management(row.gdb2+ "\\SDELOADER.TNC_LANDS")
            record_count = int(result.GetOutput(0))
            row.setvalue("GDB2_count",record_count)
        except:
            row.setvalue("GDB2_count","-1")

        uc.UpdateRow(row)
        row = uc.Next()

def ETL_synch(): # Runs ETL for TNC Lands

    # profile parameters
    gp.workspace = "Database Connections\\SDEDEV_SA_STEWARD.sde"
    gdb1 = "Database connections\\sdedev_sa_steward.sde"
    gdb2 = "Database connections\\cosde_rmnode.sde"
    replica = "SA_STEWARD.CA_TNC_LANDS"
    direction = "FROM_GEODATABASE2_TO_1"
    policy = "IN_FAVOR_OF_GDB2"
    definition = "BY_ATTRIBUTE"
    in_dataset = "SA_STEWARD.CA_TNC_INTEREST"
    out_dataset = "SA_STEWARD.TEMP"
    out_coor_system = "C:\\Program Files\\ArcGIS\\Coordinate Systems\\Geographic Coordinate Systems\\World\\WGS 1984.prj"
    transform_method = "NAD_1983_To_WGS_1984_1"
    sourceDataset = "wosdedev"
    destDataset = "not_used"

    # synchronize the replica
    gp.SynchronizeChanges_management(gdb1, replica, gdb2, direction, policy, definition)
    gp.addmessage("Synchronization completed successfully")

    # reproject the dataset
    gp.Project_management(in_dataset, out_dataset, out_coor_system, transform_method)
    gp.addmessage("Reprojection completed successfully")

    # create a temporary version
    gp.CreateVersion_management(gp.workspace, "sde.DEFAULT", "TempETL", "PRIVATE")
    gp.addmessage("Temporary version successfully created")

    # run the ETL transformation
    gp.CARO2RMProfile(sourceDataset, destDataset)
    gp.addmessage("ETL transformation completed successfully")

    # rec and post the edits to default
    gp.reconcileversion_management(gp.workspace, "TempETL", "DEFAULT", "BY_ATTRIBUTE", "FAVOR_EDIT_VERSION", "NO_LOCK_AQUIRED","NO_ABORT", "POST")
    gp.addmessage("Data reconciled and posted successfully")

    # delete the temporary version
    gp.DeleteVersion_management(gp.workspace, "TempETL")
    gp.addmessage("Temporary version successfully deleted")

    gp.addmessage(gp.getmessages)

def Feature2KML(): # Converts features to KML with extruded height
    fc = sys.argv[1]                        # input feature class
    kml = sys.argv[2]                       # path and name of kml file
    name_field = sys.argv[3]                # field containing name for element
    extrude_field = sys.argv[4]             # field containing extrusion height
    info_string = sys.argv[5]               # string to be added to information points

    # Create the xml document
    doc = xml.dom.minidom.Document()

    # Create and insert the kml root using google kml namespace
    kml = doc.createElementNS("http://earth.google.com/kml/2.1", "kml")
    doc.appendChild(kml)

    # Create and insert the kml placemark element
    Placemark = doc.createElement("Placemark")
    kml.appendChild(Placemark)

    # create a name element
    name = doc.createElement("name")
    Placemark.appendChild(name)
    name_text = doc.createTextNode(fc)
    name.appendChild(name_text)

    # create kml elements for each row in the feature class:
    cur_fc = gp.SearchCursor(fc)
    row_fc = cur_fc.Next()
    new_name = 1

    while row_fc:
        Polygon = doc.createElement("Polygon") # create a polygon element
        Placemark.appendChild(Polygon)
#        if extrude_field:
#            extrude = doc.createElement("extrude")
#            Polygon.appendChild(extrude)
#            extrude_text = doc.createTextNode(str(row_fc.getvalue(extrude_field))
#            extrude.appendChild(extrude_text)
#            altitudeMode = doc.createElement("altitudeMode")
#            Polygon.appendChild(altitudeMode)
#            altitudeMode_text = doc.createTextNode("relativeToGround")
#            altitudeMode.appendChild(altitudeMode_text)
    
        # create an outerBoundaryIs element
        outerBoundaryIs = doc.createElement("outerBoundaryIs")
        Polygon.appendChild(outerBoundaryIs)
                                  
        # create a LinearRing element
        LinearRing = doc.createElement("LinearRing")
        outerBoundaryIs.appendChild(LinearRing)
                                  
        # get the polygon coordinates
        geom = row_fc.shape

        # create a coordinates element
        coordinates = doc.createElement("coordinates")
        LinearRing.appendChild(coordinates)
        coordinates_text = doc.createTextNode(coordinates)
        coordinates.appendChild(coordinates_text)
        row_fc = cur_fc.Next()

def FindRoutes(): # Finds map documents containing routes

    scanfolder = arcpy.GetParameterAsText(0)

    logfile = open(os.path.join(scanfolder,"brokenSDEConnections.txt"),"w")
    sdetotal = 0
    brokentotal = 0
    pct = 0
    for root, dirs, files in os.walk(scanfolder):
        for name in files:
            filename = os.path.join(root, name)
            basename, extension = os.path.splitext(name)
            if extension.lower() == ".mxd" or extension.lower() == ".lyr":
                if extension.lower() == ".mxd":obj = arcpy.mapping.MapDocument(filename)
                elif extension.lower() == ".lyr":obj = arcpy.mapping.Layer(filename)
                BrokenDataSources = arcpy.mapping.ListBrokenDataSources(obj)
                brokenSet = set()
                for s in BrokenDataSources:
                    brokenSet.add(s.name)
                layers = arcpy.mapping.ListLayers(obj)
                for lyr in layers:
                    try:
                        if not lyr.isGroupLayer:
                            sdetotal = sdetotal + 1
                            if lyr.name in brokenSet:
                                brokentotal = brokentotal + 1
                                msg = filename + "," + lyr.datasetName
                                arcpy.AddMessage(msg)
                                logfile.write(msg + "\n")
                            pct = float(brokentotal)/sdetotal * 100
                            arcpy.SetProgressorLabel(str(brokentotal) + " out of " +
                                                     str(sdetotal) + " broken     " +
                                                     "{0:.2f}%".format(pct) +
                                                     "    " +  filename)
                    except:
                        pass
                del obj

    logfile.write(str(brokentotal) + " out of " +
                  str(sdetotal) + " broken     " +
                  "{0:.2f}%".format(pct))
    logfile.close()



def GridArea(): # Tabulate grid areas from input raster layer files
    # parameters
    layerfiles = r"C:\arcgisserver\Maps\AWWI"    # location of the input raster layer files
    fset = sys.argv[1]                           # feature set from user interactively
    gp.workspace = "in_memory"
    table = "in_memory/table"

    # create the results table
    gp.CreateTable_management("in_memory", "table")
    gp.AddField(table,"name","text", "50")
    gp.AddField(table,"area","double")
    gp.AddField(table,"total","double")
    gp.AddField(table,"pct","double")
    ic = gp.InsertCursor(table)

    # loop through the layers
    for name in os.listdir(layerfiles):
        if len(name.split(".")) == 2 and name.split(".")[1] == "lyr":  # filter for the layer files only
            try:
                # tabulate Area
                success = gp.TabulateArea_sa(fset, "OBJECTID", layerfiles + "\\" + name, "VALUE", "tbl")
                
                # open the temp table created by tabulate area
                sc = gp.SearchCursor("tbl")
                row = sc.Next()
                
                # check for valid data in the results of tabulate area
                if row:
                    for anything in gp.listFields("tbl", "value_1"):
                        # convert to acres
                        area = row.value_1 * 0.000247
                        totalarea = area + row.value_0 * 0.000247
                        # add results to table
                        newdata = ic.NewRow()
                        newdata.name = name.split(".")[0]
                        newdata.area = round(area,1)
                        newdata.total = round(totalarea,1)
                        newdata.pct = round(area / totalarea * 100,2)
                        ic.InsertRow(newdata)
            
            except:
                gp.addwarning("No data for " + name.split(".")[0])

        recset = gp.createobject("recordset")
        recset.load(table)
        gp.setparameter(1,recset)

def SuitableLandcover(): # Calculates percentage of suitable landcover

    env.workspace = arcpy.GetParameter(0)
    env.extent = arcpy.GetParameter(1)
    env.cellSize = '30'
    n200 = Raster("n200")
    n800 = Raster("n800")
    n1600 = Raster("n1600")
    n5000 = Raster("n5000")

    # for each year.....
    rasters = arcpy.ListRasters("wgalcv1_2010")
    for raster in rasters:
        arcpy.AddMessage("Processing " + raster)
        year = string.split(raster,"_")[1]
        
        # reclass to suitable
        arcpy.AddMessage("Reclassifying native " + year)
        reclass1 = Reclassify(raster, "Value", RemapValue([[5301,1],[7302,1],[7309,1],[7310,1],[7311,1],[9999,1]]))
        reclass2 = Reclassify(reclass1, "Value", RemapRange([[2,9999,0]]))
        reclass2.save("suitable_" + year)
        suitgrid = Raster("suitable_" + year)
        
        # reclass to CRP
        arcpy.AddMessage("Reclassifying CRP " + year)
        reclass1 = Reclassify(raster, "Value", RemapValue([[1431,1]]))
        reclass2 = Reclassify(reclass1, "Value", RemapRange([[2,9999,0]]))
        reclass2.save("crp_" + year)
        crpgrid = Raster("crp_" + year)
        
        # reclass to potential
        arcpy.AddMessage("Reclassifying Potential " + year)
        reclass1 = Reclassify(raster, "Value", RemapValue([[7310,1],[7399,1]]))
        reclass2 = Reclassify(reclass1, "Value", RemapRange([[2,9999,0]]))
        reclass2.save("pot_" + year)
        potgrid = Raster("pot_" + year)
        
        # create patch grid
        arcpy.AddMessage("Creating patches for " + year)
        patch = RegionGroup(suitgrid, "EIGHT")
        patch.save("patch_" + year)
        patch = Raster("patch_" + year)
        
        # calculate and save percent suitable native at 200m
        neighborhood = NbrCircle(200, "MAP")
        arcpy.AddMessage("Calculating percent suitable native for " + year + ",200m")
        result = FocalStatistics(suitgrid, neighborhood, "SUM","")
        result1 = (Float(result) / Float(n200)) * 100.0
        result1.save("ps200_" + year)

        # calculate and save percent suitable native at 800m and aggregate to 210m
        neighborhood = NbrCircle(800, "MAP")
        arcpy.AddMessage("Calculating percent suitable native for " + year + ",800m")
        result = FocalStatistics(suitgrid, neighborhood, "SUM","")
        result1 = (Float(result) / Float(n800)) * 100.0
        result1.save("ps800_" + year)
        arcpy.AddMessage("Aggregating 210m window")
        agg = Aggregate(result1, 7, "MEAN")
        agg.save("m_ps_800_" + year)
        
        # calculate and save percent suitable native at 1600m and aggregate to 210m
        neighborhood = NbrCircle(1600, "MAP")
        arcpy.AddMessage("Calculating percent suitable native for " + year + ",1600m")
        result = FocalStatistics(suitgrid, neighborhood, "SUM","")
        result1 = (Float(result) / Float(n1600)) * 100.0
        result1.save("ps1600_" + year)
        arcpy.AddMessage("Aggregating 210m window")
        agg = Aggregate(result1, 7, "MEAN")
        agg.save("m_ps_1600_" + year)

        # calculate and save percent suitable native at 5000m and aggregate to 210m
        neighborhood = NbrCircle(5000, "MAP")
        arcpy.AddMessage("Calculating percent suitable native for " + year + ",5000m")
        result = FocalStatistics(suitgrid, neighborhood, "SUM","")
        result1 = (Float(result) / Float(n5000)) * 100.0
        result1.save("ps5000_" + year)
        arcpy.AddMessage("Aggregating 210m window")
        agg = Aggregate(result1, 7, "MEAN")
        agg.save("m_ps_5000_" + year)
        
        # calculate and save percent suitable CRP at 200m
        neighborhood = NbrCircle(200, "MAP")
        arcpy.AddMessage("Calculating percent suitable CRP for " + year + ",200m")
        result = FocalStatistics(crpgrid, neighborhood, "SUM","")
        result1 = (Float(result) / Float(n200)) * 100.0
        result1.save("psc200_" + year)
        
        # calculate and save percent suitable CRP at 800m and aggregate to 210m
        neighborhood = NbrCircle(800, "MAP")
        arcpy.AddMessage("Calculating percent suitable CRP for " + year + ",800m")
        result = FocalStatistics(crpgrid, neighborhood, "SUM","")
        result1 = (Float(result) / Float(n800)) * 100.0
        result1.save("psc800_" + year)
        arcpy.AddMessage("Aggregating 210m window")
        agg = Aggregate(result1, 7, "MEAN")
        agg.save("mpsc800_" + year)
        
        # calculate and save percent suitable CRP at 1600m and aggregate to 210m
        neighborhood = NbrCircle(1600, "MAP")
        arcpy.AddMessage("Calculating percent suitable CRP for " + year + ",1600m")
        result = FocalStatistics(crpgrid, neighborhood, "SUM","")
        result1 = (Float(result) / Float(n1600)) * 100.0
        result1.save("psc1600_" + year)
        arcpy.AddMessage("Aggregating 210m window")
        agg = Aggregate(result1, 7, "MEAN")
        agg.save("mpsc1600_" + year)
        
        # calculate and save percent suitable CRP at 5000m and aggregate to 210m
        neighborhood = NbrCircle(5000, "MAP")
        arcpy.AddMessage("Calculating percent suitable CRP for " + year + ",5000m")
        result = FocalStatistics(crpgrid, neighborhood, "SUM","")
        result1 = (Float(result) / Float(n5000)) * 100.0
        result1.save("psc5000_" + year)
        arcpy.AddMessage("Aggregating 210m window")
        agg = Aggregate(result1, 7, "MEAN")
        agg.save("mpsc5000_" + year)

def LandscapeSignature(): # Creates landscape fragmentation signature
    # ----------------------------------Description---------------------------------
    # Generates landscape signatures for each polygon of a zonal feature class as
    # an output feature class. A grid of polygons is created centered on the centroid
    # of each input zone. This x-y grid represents the 2 dimensions: scale and
    # histogram class, for further use as the 'footprint' of a histogram graphic which
    # can be placed in the center of the zone in a GIS or 3D globe viewer. The database
    # can also be used for other analyses of the landscape signature distribution.
    #
    # A landscape signature represents the combined histograms of the proportion
    # of natural area surrounding a pixel, as measured at multiple scales.

    # ------------------------------Get input parameters-----------------------------
    gp.workspace = sys.argv[1]              # workspace
    zone_fc = sys.argv[2]                   # zone feature class
    id_field = sys.argv[3]                  # id field in the zone feature class
    in_raster = sys.argv[4]                 # land cover grid
    scale_range_min = float(sys.argv[5])    # scale range minimum
    scale_range_max = float(sys.argv[6])    # scale range maximum
    scale_range_step = float(sys.argv[7])   # scale range interval
    total_scale = int((scale_range_max - scale_range_min)/scale_range_step + 1)
    number_classes = int(sys.argv[8])       # number of histogram classes
    output_fc = sys.argv[9]                 # name of output feature class
    v_scale = float(sys.argv[10])           # vertical scale factor for output graphics
    h_scale = float(sys.argv[11])           # horizontal scale factor for output graphics

    # ----------------------execute the script in try/except--------------------------
    try:
        # create a new output feature class and add fields
        gp.CreateFeatureClass_management(gp.workspace, output_fc, "POLYGON")
        gp.AddField(output_fc,"name","text", "100")
        gp.AddField(output_fc,"scale","float", "9")
        gp.AddField(output_fc,"total_scal","long", "9")
        gp.AddField(output_fc,"bin","float", "9")
        gp.AddField(output_fc,"total_bin","long", "9")
        gp.AddField(output_fc,"bin_label","text", "20")
        gp.AddField(output_fc,"count","long", "15")
        gp.AddField(output_fc,"total_cnt","long", "15")
        gp.AddField(output_fc,"proportion","float", "9")
        
        # define the output projection from input zone feature class
        gp.DefineProjection_management(output_fc, zone_fc)
        
        # create a cursor to access the table
        cur_out = gp.InsertCursor(output_fc)
        
        # determine the overall analysis extent by buffering the zone dataset
        gp.Buffer_analysis(zone_fc, "buffer.shp", scale_range_max)
        
        # focal mean processing and extraction of statistics at each scale
        for window_size in range(scale_range_min,scale_range_max+1,scale_range_step):
            # create the overall source grid
            gp.extent = gp.describe("buffer.shp").extent # reset the overall extent
            window_type = "CIRCLE " + str(window_size) + " MAP"
            scale_raster = in_raster + str(window_size)
            gp.addmessage("Creating source grid: " + scale_raster)
            gp.FocalStatistics_sa(in_raster, scale_raster, window_type, "MEAN", "NODATA")
            
            # generate statistics for each zone of the input zonal feature class
            cur_zone = gp.SearchCursor(zone_fc)
            row_zone = cur_zone.Next()
            while row_zone:
                poly_id = row_zone.getValue(id_field)
                geom = row_zone.shape
                gp.addmessage("Extracting statistics for scale: " +str(window_size)+ " and polygon: " + poly_id)
                
                # get the zone centroid and adjust so that output graphic will be centered
                lstValues = string.split(geom.centroid)
                centroid_x = float(lstValues[0]) - (float(number_classes) * h_scale)/2
                centroid_y = float(lstValues[1]) - (float(total_scale) * h_scale)/2
                
                # extract zone polygon to temporary feature class
                where_clause = '"' + id_field + '" = '+"'"+poly_id +"'"
                tempMask = poly_id + ".shp"
                gp.Select_analysis(zone_fc, tempMask, where_clause)
                
                # set the analysis extent to the shape extent
                gp.extent = geom.extent
                
                # perform the raster extraction and delete temporary inputs
                gp.ExtractByMask_sa(scale_raster, tempMask, "extract")
                if gp.exists(tempMask): gp.delete(tempMask)
                
                # slice grid to match histogram breaks and delete temporary inputs
                gp.Slice_sa("extract", "slice", number_classes, "EQUAL_INTERVAL","1")
                if gp.exists("extract"): gp.delete("extract")
                
                # create table using zonal statistics and delete temporary inputs
                gp.ZonalStatisticsAsTable_sa("slice", "Value", "slice", "zonestats.dbf")
                if gp.exists("slice"): gp.delete("slice")
                
                # get the total count from the zonal stats table
                gp.Statistics_analysis("zonestats.dbf", "total_count.dbf", "count sum")
                cur_sum = gp.SearchCursor("total_count.dbf")
                row_sum = cur_sum.Next()
                total_count = row_sum.sum_count
                if gp.exists("total_count.dbf"): gp.delete("total_count.dbf")
                del cur_sum
                
                # for each row of the zonestats.dbf table:
                cur_stats = gp.SearchCursor("zonestats.dbf")
                row_stats = cur_stats.Next()
                while row_stats:
                    # create coordinates based on zone centroid and analysis window size
                    min_x = centroid_x + (h_scale * (row_stats.value - 1))
                    min_y = centroid_y + ((window_size - scale_range_min)/scale_range_step) * h_scale
                    max_x = min_x + h_scale
                    max_y = min_y + h_scale
                    # create polygon
                    polyArray = gp.createObject("Array")
                    pnt = gp.createObject("Point")
                    pnt.x = min_x
                    pnt.y = min_y
                    polyArray.add(pnt)          # lower left
                    pnt.x = min_x
                    pnt.y = max_y
                    polyArray.add(pnt)          # upper left
                    pnt.x = max_x
                    pnt.y = max_y
                    polyArray.add(pnt)          # upper right
                    pnt.x = max_x
                    pnt.y = min_y
                    polyArray.add(pnt)          # lower right
                    pnt.x = min_x
                    pnt.y = min_y
                    polyArray.add(pnt)          # lower left again
                    
                    # create a row in the output table and populate it
                    row_out = cur_out.NewRow()
                    row_out.shape = polyArray
                    row_out.name = poly_id
                    row_out.scale = window_size
                    row_out.total_scal = total_scale
                    row_out.bin =  row_stats.Value
                    row_out.total_bin = number_classes
                    row_out.bin_label = str(float(row_stats.Value-1)/float(number_classes)*100) + " - " + \
                        str(float(row_stats.Value)/float(number_classes)*100) + " %"
                    
                    row_out.count = row_stats.count
                    row_out.total_cnt = total_count
                    row_out.proportion = float(row_stats.count)/float(total_count) * v_scale
                    cur_out.InsertRow(row_out)
                    row_stats = cur_stats.Next() # end of loop through the zonestats.dbf
                del cur_stats
                if gp.exists("zonestats.dbf"): gp.delete("zonestats.dbf")
                row_zone = cur_zone.Next()       # end of loop through the rows of the input zone file
            del cur_zone  # delete the zone file cursor
        del cur_out  # delete the output file cursor
        if gp.exists("buffer.shp"): gp.delete("buffer.shp") # delete the temporary buffer file
    except:
        # get the traceback object
        tb = sys.exc_info()[2]
        # tbinfo contains the line number that the code failed on and the code from that line
        tbinfo = traceback.format_tb(tb)[0]
        # concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n    " + \
            str(sys.exc_type)+ ": " + str(sys.exc_value) + "\n"
        # generate a message string for any geoprocessing tool errors
        msgs = "GP ERRORS:\n" + gp.GetMessages(2) + "\n"
        
        # return gp messages for use with a script tool
        gp.AddError(msgs)
        gp.AddError(pymsg)



def SaveAsVersion10_0(): # Saves MXDs as version 10.0

    # walk through the directory structure beginning with the
    # folder supplied by the user as a run time parameter
    for root, dirs, files in os.walk(arcpy.GetParameterAsText(0)):
        
        # iterate through each file
        for name in files:
            filename = os.path.join(root, name)
            basename, extension = os.path.splitext(name)
            
            # if the extension identifies it as an MXD
            # then assign it to the obj variable.
            if extension.lower() == ".mxd":
                obj = arcpy.mapping.MapDocument(filename)
                
                # save the file as version 10.0
                arcpy.SetProgressorLabel("Saving " + filename)
                obj.saveACopy("temp_" + name,"10.0")
                
                # delete the mxd object
                del obj
                
                # delete the original and rename the copy
                # but only if the copy was successfully saved
                if os.path.isfile(os.path.join(root,"temp_" + name)):
                    os.remove(filename)
                    os.rename(os.path.join(root,"temp_" + name), filename)

def SaveLayerAsVersion10_0(): # Saves Layer files to version 10

    # walk through the directory structure beginning with the
    # folder supplied by the user as a run time parameter
    for root, dirs, files in os.walk(arcpy.GetParameterAsText(0)):
        
        # iterate through each file
        for name in files:
            filename = os.path.join(root, name)
            basename, extension = os.path.splitext(name)
            
            # if the extension identifies it as an LYR
            # then assign it to the obj variable.
            if extension.lower() == ".lyr":
                
                # save the file as version 10.0
                arcpy.SetProgressorLabel("Saving " + filename)
                arcpy.SaveToLayerFile_management(filename, filename, "ABSOLUTE", "10")



def TNC_Offices(): # Maps TNC office location data

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

def RasterStatsOverlapping(): # Tabulates zonal stats in overlapping polygon zones

    # User defined parameters (set these in the geoprocessing tool dialog)
    zones = arcpy.GetParameterAsText(0)
    zfield = arcpy.GetParameterAsText(1)
    raster = arcpy.GetParameterAsText(2)

    count = arcpy.GetCount_management(zones)

    # create temporary table to hold results
    arcpy.CreateTable_management("in_memory", "temp")
    outTable = "in_memory/temp"

    # add a field to zone table, if necessary to hold final result
    fieldList = arcpy.ListFields(zones,"ZSTAT")
    if not fieldList: arcpy.AddField_management(zones, "ZSTAT", "SHORT")

    # step through the zones dataset
    rows = arcpy.SearchCursor(zones)
    row = rows.next()
    x = 1

    while row:
        arcpy.AddMessage("Processing feature " + str(x) + " of " + str(count[0]))
        
        # create a feature layer from the zones feature class that just includes the current feature
        arcpy.MakeFeatureLayer_management(zones,"zones_lyr", '"OBJECTID" = ' + str(row.OBJECTID))
        
        # calculate zonal stats for feature
        outZSaT = ZonalStatisticsAsTable("zones_lyr", zfield, raster, outTable, "DATA", "MAJORITY")
        
        # join zone feature class to zonal stat output
        arcpy.AddJoin_management("zones_lyr", zfield, outTable, zfield, "KEEP_COMMON")
        
        # update zone feature class
        arcpy.CalculateField_management("zones_lyr", "ZSTAT", "[temp.MAJORITY]")
        
        # remove join
        arcpy.RemoveJoin_management("zones_lyr", "temp")
        
        row = rows.next()
        x = x + 1



def XMFAlerter(): # Updates the SDI inventory database with XMFAlerter Server status

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

def SpeciesRasterValue(): # Zonal statistics for species in AWWI

    env.workspace = "Database Connections\\sdetest_awwi_owner.sde"

    # set local variables
    rasters = arcpy.ListRasters("AWWI_OWNER.ABNNF14010")
    fc = "AWWI_OWNER.US_STATES_GEN48"
    sptbl = "AWWI_OWNER.spcRasterValues"
    spid = "AWWI_OWNER.SPECIES_ID"
    fid = "STATE_NAME"
    lyr = "layer1"
    tbl = "table1"

    for raster in rasters:
        
        # Extract the raster name to use as field name identifier (idx)
        idx = raster.split(".")[1]
        arcpy.AddMessage("Starting " + idx)
        
        #Create search cursor
        sc = arcpy.SearchCursor("AWWI_OWNER.SPECIES_ID", "AWWI_OWNER.SPECIES_ID.GAP LIKE '" + idx + "%'")
        row = sc.next()
        if row:
            # Make Feature Layer...
            arcpy.MakeFeatureLayer_management(fc, lyr)
            
            # Check out extension and start Zonal Statistics as Table...
            arcpy.AddMessage("Zonal stats started")
            arcpy.CheckOutExtension("Spatial")
            outZSaT = ZonalStatisticsAsTable(lyr, fid, raster, tbl, "DATA")
            arcpy.AddMessage("Zonal stats completed")
            
            # Add field to tbl
            arcpy.AddField_management(tbl, "SPECIES", "TEXT")
            arcpy.AddMessage("Added SPECIES field")
            arcpy.DeleteField_management(tbl, "AWWI_OWNER.table1.AREA")
            arcpy.AddMessage("Deleted Area field")
            
            # Expressions for calculate field...
            exp1 = "\"" + idx + "\""
            
            # Calculate Field...
            arcpy.AddMessage("Calculating values")
            arcpy.CalculateField_management(tbl, "SPECIES", exp1, "VB", "")
            
            # Append rows to spcRasterValues table
            arcpy.AddMessage("Appending rows")
            arcpy.Append_management(tbl, sptbl)
            arcpy.AddMessage("Wohooo " + idx + " completed!")
        
        else:
            arcpy.AddMessage("*************** " + idx + " not found in species ID table")


 
def MergeCLU(): # Merges CLU feature classes and CRP tables

    import arcpy
    from arcpy import env
    import os
    import string
    import sys

    env.overwriteOutput = True

    # User defined parameters (set these in the geoprocessing tool dialog)
    OutPath = arcpy.GetParameterAsText(0)
    outName = arcpy.GetParameterAsText(1)
    fcSource = arcpy.GetParameterAsText(2)
    tblSource = arcpy.GetParameterAsText(3)
    env.workspace = fcSource
    fcList = arcpy.ListFeatureClasses()


    arcpy.AddMessage("Merging workspace: " + outName)
    # set coordinate system
    Coordinate_System = "PROJCS['NAD_1983_Albers',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Albers'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-96.0],PARAMETER['Standard_Parallel_1',29.5],PARAMETER['Standard_Parallel_2',45.5],PARAMETER['Latitude_Of_Origin',23.0],UNIT['Meter',1.0]];-16901100 -6972200 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision"
    # Create output gdb
    arcpy.CreateFileGDB_management(OutPath, outName)
    # create output feature class with defined coordinate system
    arcpy.CreateFeatureclass_management(OutPath + "/" + outName + ".gdb", "CLU", "POLYGON", fcList[0], "DISABLED", "DISABLED", Coordinate_System)

    # For each shapefile add source file IDs:
    arcpy.SetProgressor("step", "adding source file IDs...", 0, len(fcList), 1)

    for fc in fcList:
        arcpy.SetProgressorPosition()
        # Check if the SourceFile field exists, if not add it
        fieldList = arcpy.ListFields(fc,"SourceFile")
        if not fieldList: arcpy.AddField_management(fc, "SourceFile", "text", "", "", "20")
        
        # Calculate SourceFile from the shapefile name.
        # The shapefile name contains a string identifying
        # the county. It will be used later to determine whether
        # duplicate features should be kept or discarded.
        fcName = str(fc)[8:11]
        arcpy.CalculateField_management(fc, "SourceFile", '"'+fcName+'"', "PYTHON_9.3")

    # Merge all feature classes in the shapefile source workspace
    arcpy.SetProgressor("default", "merging feature classes...")
    arcpy.Merge_management(fcList, OutPath + "/" + outName + ".gdb/CLU")

    # Merge all tables in the table source workspace
    arcpy.SetProgressorLabel("merging tables...")
    env.workspace = tblSource
    tblList = arcpy.ListTables("","dBASE")
    arcpy.Merge_management(tblList, OutPath + "/" + outName + ".gdb/CRP")

    # Reset workspace to the output geodatabase
    env.workspace = OutPath + "/" + outName + ".gdb"

    # Add new fields
    arcpy.SetProgressorLabel("adding new fields...")
    arcpy.AddField_management("CLU", "CRP_FIELD", "SHORT")
    arcpy.AddField_management("CLU", "EXP_YEAR", "TEXT",4)
    arcpy.AddField_management("CLU", "CONTRACT", "TEXT",12)
    arcpy.AddField_management("CLU", "ACRES", "DOUBLE")
    arcpy.AddField_management("CLU", "PRAC_NBR", "TEXT",5)

    # create an index on CLUID on both tables
    arcpy.SetProgressorLabel("creating attribute index...")
    arcpy.AddIndex_management("CLU", "CLUID", "CLU_CLUID_IDX")
    arcpy.AddIndex_management("CRP", "CLUID", "CRP_CLUID_IDX")

    # step through the CRP table
    # Note: Its done this way because of inconsistency with the AddJoin geoprocessing tool in ArcGIS 10.0
    count = arcpy.GetCount_management("CRP")
    arcpy.SetProgressor("step", "adding CRP data to CLU...", 0, int(count[0]), 1)
    CRP_rows = arcpy.SearchCursor("CRP")
    for CRP_row in CRP_rows:
        # update matching records in CLU
        query = '"CLUID" = ' + "'" + CRP_row.CLUID + "'"
        arcpy.SetProgressorPosition()
        CLU_rows = arcpy.UpdateCursor("CLU",query)
        for CLU_row in CLU_rows:
            CLU_row.CRP_FIELD = 1
            CLU_row.EXP_YEAR = CRP_row.EXPDATE[0:4]
            CLU_row.CONTRACT = CRP_row.CONTRACT
            CLU_row.ACRES = CRP_row.ACRES
            CLU_row.PRAC_NBR = CRP_row.PRAC_NBR
            CLU_rows.updateRow(CLU_row)

    # remove cursor locks
    del CLU_row
    del CRP_row
    del CLU_rows
    del CRP_rows

def SummarizeConnections(): # Summarizes SDE connections in all map documents

    scanfolder = arcpy.GetParameterAsText(0)
    #scanfolder = r"D:\AZGISFiles"
    exceptions = ["VENTYX_VIEWER on SDETEST.DEFAULT.sde",
                  "VENTYX_STEWARD on SDETEST.default.sde",
                  "WOSDE_TNC_VIEWER.sde"]
    logfile = open(os.path.join(scanfolder,"brokenSDEConnections.txt"),"w")
    sdetotal = 0
    brokentotal = 0
    pct = 0
    for root, dirs, files in os.walk(scanfolder):
        for name in files:
            filename = os.path.join(root, name)
            basename, extension = os.path.splitext(name)
            if extension.lower() == ".mxd" or extension.lower() == ".lyr":
                if extension.lower() == ".mxd":obj = arcpy.mapping.MapDocument(filename)
                elif extension.lower() == ".lyr":obj = arcpy.mapping.Layer(filename)
                BrokenDataSources = arcpy.mapping.ListBrokenDataSources(obj)
                brokenSet = set()
                for s in BrokenDataSources:
                    brokenSet.add(s.name)
                layers = arcpy.mapping.ListLayers(obj)
                for lyr in layers:
                    try:
                        if ".sde\\" in lyr.dataSource and not lyr.isGroupLayer:
                            connection = lyr.dataSource.rsplit(".sde\\",1)[0] + ".sde"
                            connection = os.path.basename(connection)
                            if connection not in exceptions:
                                sdetotal = sdetotal + 1
                                if lyr.name in brokenSet:
                                    brokentotal = brokentotal + 1
                                    msg = filename + "," + lyr.datasetName
                                    arcpy.AddMessage(msg)
                                    logfile.write(msg + "\n")
                                pct = float(brokentotal)/sdetotal * 100
                            arcpy.SetProgressorLabel(str(brokentotal) + " out of " +
                                                     str(sdetotal) + " broken     " +
                                                     "{0:.2f}%".format(pct) +
                                                     "    " +  filename)
                    except:
                        pass
                del obj

    logfile.write(str(brokentotal) + " out of " +
                  str(sdetotal) + " broken     " +
                  "{0:.2f}%".format(pct))
    logfile.close()

def ResetConnections(): # Updates SDE connections for all map docs in directory tree

    # use the following variable to store the path to an existing
    # connection file with connection parameters for the new database
    newSource = r"D:\AZGISFiles\__AZTUC_NEW_SERVER__\sdeloader@aztuc.sde"

    # use the following list variable to store any known connection
    # strings that should not be updated

    exceptions = ["VENTYX_VIEWER on SDETEST.DEFAULT.sde",
                  "VENTYX_STEWARD on SDETEST.default.sde",
                  "WOSDE_TNC_VIEWER.sde"]

    # walk through the directory structure beginning with the
    # folder supplied by the user as a run time parameter
    for root, dirs, files in os.walk(arcpy.GetParameterAsText(0)):
        
        # iterate through each file
        for name in files:
            filename = os.path.join(root, name)
            basename, extension = os.path.splitext(name)
            
            # if the extension identifies it as an MXD or LYR file
            # then assign it to the obj variable. Note different syntax
            # required for MXD and LYR files
            if extension.lower() == ".mxd" or extension.lower() == ".lyr":
                if extension.lower() == ".mxd":obj = arcpy.mapping.MapDocument(filename)
                elif extension.lower() == ".lyr":obj = arcpy.mapping.Layer(filename)
                
                # get a list of broken data sources so that we do not waste
                # time trying to update the ones that are not broken
                BrokenDataSources = arcpy.mapping.ListBrokenDataSources(obj)
                brokenSet = set()
                for s in BrokenDataSources:
                    brokenSet.add(s.name)
                
                # also get a list of layers in the document
                layers = arcpy.mapping.ListLayers(obj)
                
                # begin processing the file
                arcpy.SetProgressorLabel("Processing " + filename)
                savecopy = False
            
                #iterate through each layer in the file
                for lyr in layers:
                    
                    # use exception handling to continue in case of error
                    # comment this out for debugging
                    try:
                        
                        # if the layer is broken, its an SDE layer, and the
                        # connection is not in the exception list....
                        if (lyr.name in brokenSet and ".sde\\" in lyr.dataSource):
                            connection = lyr.dataSource.rsplit(".sde\\",1)[0] + ".sde"
                            connection = os.path.basename(connection)
                            if connection not in exceptions:
                                
                                # get the original dataset name. Because it may be part of
                                # a feature dataset,we only want the rightmost part of the
                                # string, after the final ".". Also, in case there is no
                                # separator, we need to assign the whole string. Therefore
                                # we use the array length - 1 to determine the last position
                                # in the array
                                dn = lyr.datasetName.rsplit(".",1)
                                dataset = dn[len(dn)-1]
                                
                                # now attempt to replace the datasource. Validate is set to FALSE
                                # to improve performance
                                arcpy.AddMessage("Updating " + connection + "    Dataset:" + dataset)
                                lyr.replaceDataSource(newSource, "SDE_WORKSPACE", dataset, False)
                                
                                # since at least one layer has been updated, the  file is flagged
                                # to be saved
                                savecopy = True
                    except:
                        pass
        
                # if the file needs to be saved...
                if savecopy:
                    arcpy.SetProgressorLabel("Saving " + filename)
                    obj.save()
                
                # clean up memory
                del obj

def replace_text(): # replaces text in all files defined by extension

import os, sys, string, os.path
InFolder = "D:/arcgisserver/config-store/services"
ext = ".json"
original = 'minInstancesPerNode": 1'
replacement = 'minInstancesPerNode": 0'
for root, dirs, files in os.walk(InFolder):
    for name in files:
        basename, extension = os.path.splitext(name)
        if extension.lower() == ext:
            theFile = open(os.path.join(root, name),'r')
            old = theFile.read()
            theFile.close()
            new = old.replace(original, replacement)
            theFile = open(os.path.join(root, name),'w')
            theFile.write(new)
            theFile.close()
            print name + " complete"
          
input("Press ENTER to continue...")

def publish_map_services(): # Publish services from mxds or msds 
import arcpy, os, sys, string, os.path
scanfolder = "d:\\services101"
con = "d:\\services101\\stratus_publisher.ags"
arcpy.env.workspace = scanfolder
print "Executing..."

for root, dirs, files in os.walk(scanfolder):
    for name in files:
        basename, extension = os.path.splitext(name)
        if extension.lower() == ".mxd":
            path = string.split(root,"\\")
            folder = path[2]
            service = string.split(path[3],".")[0]
            filename = os.path.join(root,name)
            mapDoc = arcpy.mapping.MapDocument(filename)
            print "Publishing " + service + " in folder " + folder + " from " + filename + "\n"

            try:

                # Create service definition draft
                sddraft = folder + service + ".sddraft"
                arcpy.mapping.CreateMapSDDraft(mapDoc, sddraft, service, "", con, "", folder)
                print "Draft created \n"

                # Analyze the service definition draft
                analysis = arcpy.mapping.AnalyzeForSD(sddraft)
                print "Service successfully analyzed \n"

                # Stage and upload the service if the sddraft analysis did not contain errors
                if analysis['errors'] == {}:
                    sd = folder + service + ".sd"
                    # Execute StageService.
                    arcpy.StageService_server(sddraft, sd)
                    print "Service successfully staged \n"
                    # Execute UploadServiceDefinition. 
                    arcpy.UploadServiceDefinition_server(sd, con)
                    print "Service successfully published \n"

            except:
                print "Service could not be published \n"
                print arcpy.GetMessages(2)
                

input("Press ENTER to continue...")


i


# this is a quickie script that I wrote to update the photo EXIF
# metadata on image files in the folder in which its run
# It updates the datetime metadata to be the same as the first 8 digits
# of the filename, which represent the data in YYYYMMDD format

import pyexiv2, datetime, os
dir = os.getcwd()
for name in os.listdir(dir):
    basename, extension = os.path.splitext(name)
    if (extension.lower() == ".jpg"
     or extension.lower() == ".png"
     or extension.lower() == ".tif"):
        year = int(name[0:4])
        month = int(name[4:6])
        day = int(name[6:8])
        if month == 0: month = 1
        if day == 0: day = 1
        photoDate = datetime.datetime(year, month, day)
        metadata = pyexiv2.ImageMetadata(name)
        metadata.read()
        for key in ["Exif.Image.DateTime","Exif.Photo.DateTimeOriginal","Exif.Photo.DateTimeDigitized"]:
            if key in metadata.exif_keys:
                print "Updating key", key, metadata[key].value, "to", photoDate
                metadata[key].value = photoDate
            else:
                print "Adding key", key, "with value", photoDate
                metadata[key] = pyexiv2.ExifTag(key, photoDate)
            metadata.write()






















