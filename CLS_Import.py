# Loads CLS data into secured areas dataset

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
