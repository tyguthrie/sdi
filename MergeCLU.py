# Merges CLU feature classes and CRP tables

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
