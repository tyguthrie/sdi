def AddSourceID(): # Loads IDs from a source dataset based on matching geometry
    
    # load source feature class into target feature dataset
    temp = fd + "\\temp"
    gp.CopyFeatures_management(sfc, temp)
    total = gp.GetCount_management(temp)
    
    # Open source feature class and go to first record
    sc = gp.SearchCursor(temp)
    row = sc.Next()
    x = 1
    match = 0
    try:
        # for each record in the source feature class...
        while row:
            gp.addmessage("Processing record " + str(x) + " of " + str(total))
            # create a layer for the source feature class (4)
            source_id = str(row.getvalue(sid))
            qry = '"' + sid + '" = ' + source_id
            gp.MakeFeatureLayer_management(temp, "lyrSource", qry, fd)
            # create a layer for the target feature class
            gp.MakeFeatureLayer_management(tfc, "lyrTarget", "#", fd)
            # see if there is an identical spatial match (5)
            gp.SelectLayerByLocation_management("lyrTarget", "ARE_IDENTICAL_TO", "lyrSource", "#", "NEW_SELECTION")
            # if there is a spatial match
            if gp.GetCount_management("lyrTarget"):
                gp.addmessage("Spatial match found. Updating ID = " + source_id)
                match = match + 1
                # add source ID to target (6)
                uc = gp.UpdateCursor("lyrTarget")
                urow = uc.Next()
                urow.setvalue(tid,source_id)
                uc.UpdateRow(urow)
            # move on to the next source record (3)
            x = x + 1
            row = sc.Next()
    except:
        gp.addmessage("Error encountered: stopping execution")
        gp.addmessage(gp.getmessages())

def FindDuplicates(): # Finds and deletes duplicate features in feature class

    # User defined parameters (set these in the geoprocessing tool dialog)

    workspaceList = arcpy.GetParameter(0)
    for i in range(workspaceList.rowCount):
        workspace = string.strip(workspaceList.getRow(i),"'")
        arcpy.AddMessage("Batch Processing: " + workspace)
        
        env.workspace = workspace
        searchradius = "20" # how close do the features' centroids need to be in order to be selected as intersecting
        arcpy.SetProgressor("default", "Finding duplicates for: " + env.workspace)
        
        # if there are any missing CLUIDs add a unique ID based on object id
        arcpy.SetProgressor("default", "Fixing missing CLUIDs...")
        fieldList = arcpy.ListFields("CLU","","OID")
        ObjField = fieldList[0].name
        arcpy.MakeFeatureLayer_management("CLU", "temp", '"CLUID" IS NULL OR "CLUID" = ' + "''")
        arcpy.CalculateField_management("temp", "CLUID", '"PLJV" + str(!' + ObjField + '!)', "PYTHON")
        
        # Add a field to indicate records to be deleted, make sure its empty
        arcpy.SetProgressor("default", "Adding temporary field...")
        fieldList = arcpy.ListFields("CLU","DEL")
        if not fieldList: arcpy.AddField_management("CLU", "DEL", "SHORT")
        arcpy.CalculateField_management("CLU", "DEL", '0')
        
        # Open update cursors. Need two cursors for pairwise comparison.
        # The cursors must also be sorted by CLUID order for correct comparison.
        arcpy.SetProgressor("default", "Sorting features by CLUID...")
        rows_lead = arcpy.UpdateCursor("CLU","","","","CLUID A")
        rows_lag = arcpy.UpdateCursor("CLU","","","","CLUID A")
        
        # point lead and lag cursors to starting positions
        row_lead = rows_lead.next()
        row_lag = rows_lag.next()
        row_lead = rows_lead.next()
        
        # step through dataset comparing each lead/lag pair for CLUID
        count = arcpy.GetCount_management("CLU")
        arcpy.SetProgressor("step", "Evaluating duplicate CLUID sets...", 0, int(count[0]), 1)
        while row_lead:
            if row_lead.CLUID == row_lag.CLUID  and row_lead.CLUID is not None: # a matching pair
                arcpy.AddMessage("duplicate CLUID found: " + row_lead.CLUID)
                if row_lead.SourceFile == row_lead.COUNTYCD or row_lead.SourceFile == row_lead.ADMNCOUNTY: row_lag.DEL = 1 # lead is correct, or both are correct, so delete lag
                elif row_lag.SourceFile == row_lag.COUNTYCD or row_lag.SourceFile == row_lag.ADMNCOUNTY: row_lead.DEL = 1 # lag is correct, so delete lead
                else: row_lag.DEL = 1 # neither are correct so delete lag
                rows_lead.updateRow(row_lead)
                rows_lag.updateRow(row_lag)
            row_lead = rows_lead.next()
            row_lag = rows_lag.next()
            arcpy.SetProgressorPosition()
        
        # clean up
        del rows_lead
        del rows_lag
        del row_lead
        del row_lag
        
        # Find duplicate polygons by spatial join of center points
        arcpy.SetProgressor("default", "Finding intersecting centroids...")
        arcpy.FeatureToPoint_management("CLU", "CLU_POINTS1", "INSIDE")
        arcpy.CopyFeatures_management("CLU_POINTS1", "CLU_POINTS2")
        arcpy.SpatialJoin_analysis("CLU_POINTS1","CLU_POINTS2","SPATIAL_DUPLICATES","JOIN_ONE_TO_MANY", "","","INTERSECT", searchradius +" METERS")
        
        # Add a field to hold spatial duplicate IDs
        arcpy.SetProgressor("default", "Adding temporary field...")
        fieldList = arcpy.ListFields("CLU","SPATIALID")
        if not fieldList: arcpy.AddField_management("CLU", "SPATIALID", "TEXT", 36)
        
        # step through the SPATIAL_DUPLICATES table, adding IDs to CLU
        # Note: Its done this way because of inconsistency with the AddJoin geoprocessing tool in ArcGIS 10.0
        count = arcpy.GetCount_management("SPATIAL_DUPLICATES")
        arcpy.SetProgressor("step", "adding spatial matches to CLU...", 0, int(count[0]), 1)
        SD_rows = arcpy.SearchCursor("SPATIAL_DUPLICATES")
        for SD_row in SD_rows:
            # update matching records in CLU
            query = '"CLUID" = ' + "'" + SD_row.CLUID + "'"
            arcpy.SetProgressorPosition()
            CLU_rows = arcpy.UpdateCursor("CLU",query)
            for CLU_row in CLU_rows:
                CLU_row.SPATIALID = SD_row.CLUID_1
                CLU_rows.updateRow(CLU_row)

        # clean up
        del CLU_row
        del SD_row
        del CLU_rows
        del SD_rows

        # Open update cursors. Need two cursors for pairwise comparison.
        # The cursors must also be sorted by SPATIAL ID order for correct comparison.
        arcpy.SetProgressor("default", "Sorting features by SPATIAL ID...")
        rows_lead = arcpy.UpdateCursor("CLU","","","","SPATIALID A")
        rows_lag = arcpy.UpdateCursor("CLU","","","","SPATIALID A")

        # point lead and lag cursors to starting positions
        row_lead = rows_lead.next()
        row_lag = rows_lag.next()
        row_lead = rows_lead.next()

        # step through dataset again comparing each lead/lag pair for SPATIAL ID
        count = arcpy.GetCount_management("CLU")
        arcpy.SetProgressor("step", "Evaluating duplicate spatial sets...", 0, int(count[0]), 1)
        while row_lead:
            if row_lead.SPATIALID == row_lag.SPATIALID and row_lead.SPATIALID is not None: # a matching pair
                arcpy.AddMessage("duplicate geometry found at: " + row_lead.SPATIALID)
                if row_lead.CRP_FIELD == 1 and row_lag.CRP_FIELD <> 1: row_lag.DEL = 1 # lead is correct, so delete lag
                elif row_lag.CRP_FIELD == 1 and row_lead.CRP_FIELD <> 1: row_lead.DEL = 1 # lag is correct, so delete lead
                elif row_lead.SourceFile == row_lead.COUNTYCD or row_lead.SourceFile == row_lead.ADMNCOUNTY: row_lag.DEL = 1 # lead is correct, or both are correct, so delete lag
                elif row_lag.SourceFile == row_lag.COUNTYCD or row_lag.SourceFile == row_lag.ADMNCOUNTY: row_lead.DEL = 1 # lag is correct, so delete lead
                else: row_lag.DEL = 1 # neither are correct so delete lag
                rows_lead.updateRow(row_lead)
                rows_lag.updateRow(row_lag)
            row_lead = rows_lead.next()
            row_lag = rows_lag.next()
            arcpy.SetProgressorPosition()

        # clean up
        del rows_lead
        del rows_lag
        del row_lead
        del row_lag

        # clean up fields, now that all the joins have been completed. Uses a hardcoded
        # list of fields to keep. The list should be modified if the CLU schema changes.
        fieldList = arcpy.ListFields("CLU")
        arcpy.SetProgressor("step", "Dropping extra fields...", 0, len(fieldList), 1)
        keepFieldList = ["OBJECTID","OBJECTID_1","Shape","COMMENTS","ADMNSTATE","ADMNCOUNTY",
                         "STATECD","COUNTYCD","CLUNBR","CALCACRES","HELTYPECD",
                         "CLUCLSCD","FSA_ACRES","CLUID","SourceFile","Shape_Length",
                         "Shape_Area","CONTRACT","ACRES","EXPDATE",
                         "PRAC_NBR","CRP_FIELD","EXP_YEAR","DEL",
                         "Shape_Length_1","Shape_Area_1"]
        for f in fieldList:
            if f.name not in keepFieldList: arcpy.DeleteField_management("CLU", f.name)
            arcpy.SetProgressorPosition()

        # Export and delete duplicates from CLU feature class.
        # The deleted features are saved to a feature class called DUPLICATES.
        arcpy.SetProgressor("default", "Exporting and deleting duplicates")
        arcpy.MakeFeatureLayer_management("CLU", "temp", '"DEL" = 1')
        arcpy.CopyFeatures_management("temp", "DUPLICATES")
        arcpy.DeleteFeatures_management("temp")

        # select centroids that no longer intersect a polygon, i.e the polygon should not have been deleted
        # for example, the centroids of small adjacent polygons were within the search radius, or a polygon
        # was centrally located within a surrounding polygon so that the centroids were within the search radius
        arcpy.SetProgressor("default", "Restoring accidental deletions...")
        arcpy.MakeFeatureLayer_management("CLU_POINTS1", "temp")
        arcpy.SelectLayerByLocation_management("temp", "INTERSECT", "CLU") # centroids that intersect remaining CLU features
        arcpy.SelectLayerByAttribute_management("temp", "SWITCH_SELECTION") # centroids that DO NOT intersect remaining CLU features

        # select features from DUPLICATES that were accidentally deleted, based on the previous selection
        arcpy.MakeFeatureLayer_management("DUPLICATES", "temp2")
        arcpy.SelectLayerByLocation_management("temp2", "INTERSECT", "temp")

        # restore the features to CLU and delete from DUPLICATES
        arcpy.CopyFeatures_management("temp2", "RESTORE")
        arcpy.Append_management("RESTORE","CLU")
        arcpy.DeleteFeatures_management("temp2")

        # remove the temporary field
        arcpy.DeleteField_management("CLU", "DEL")
        arcpy.DeleteField_management("DUPLICATES", "DEL")

        # Clean up scratch tables
        arcpy.SetProgressor("default", "Cleaning up...")
        if arcpy.Exists("CLU_POINTS1"): arcpy.Delete_management("CLU_POINTS1")
        if arcpy.Exists("CLU_POINTS2"): arcpy.Delete_management("CLU_POINTS2")
        if arcpy.Exists("SPATIAL_DUPLICATES"): arcpy.Delete_management("SPATIAL_DUPLICATES")
        if arcpy.Exists("RESTORE"): arcpy.Delete_management("RESTORE")

def Count(): # Counts total features in a set of shapefiles

    # For each shapefile
    fcList = arcpy.ListFeatureClasses()
    total = 0

    for fc in fcList:
        arcpy.AddMessage(fc)
        count = arcpy.GetCount_management(fc)
        total = total + int(count[0])

    arcpy.AddMessage("Total: " + str(total))

def SpatialRelate(): # Intersects two feature classes and creates a relationship class

    # set the workspace
    gp.workspace = sys.argv[1]
    gdbPath = os.path.dirname(sys.argv[1])

    # create variables for the input feature classes,
    # the combined feature classes to be intersected
    # and the new relationship foreign key fields
    originFC = os.path.basename(sys.argv[2])
    destFC = os.path.basename(sys.argv[3])
    originKey = "FID_" + originFC
    destKey = "FID_" + destFC
    rAttributes = originKey + " ; " + destKey + " ; " + "Proportion"
    intFC = originFC + " ; " + destFC

    try:
        # test for the existence of, and if necessary
        # create new fields in the input feature class
        # to hold the shape_area and the calculated proportion
        gp.AddMessage("Adding fields [Area1] and [Proportion] to the table " + originFC + "...")
        if not gp.ListFields(originFC,"Area1").Next():
            gp.AddField_management(originFC, "Area1", "DOUBLE")
        if not gp.ListFields(originFC,"Proportion").Next():
            gp.AddField_management(originFC, "Proportion", "DOUBLE")
        
        # calculate the values for Area1
        gp.AddMessage("Copying [Shape_Area]...")
        gp.CalculateField_management(originFC, "Area1", "[Shape_Area]")
        
        # intersect the feature classes
        gp.AddMessage("Intersecting " + intFC + "...")
        gp.Intersect_analysis(intFC, "tmpFC", "ALL")

        # delete the temporary fields in the input feature class
        gp.AddMessage("Deleting fields [Area1] and [Proportion] from the table " + originFC + "...")
        gp.DeleteField_management(originFC, "Area1; Proportion")

        # perform the calculation
        gp.AddMessage("Calculating [Proportion] = [Shape_Area]/[Area1]...")
        gp.CalculateField_management("tmpFC", "Proportion", "[Shape_Area]/[Area1]")

        # create or recreate the relationship class
        gp.AddMessage("Creating attributed relationship class " + originFC + "_" + destFC)
        gp.TableToRelationshipClass_management(originFC, destFC, originFC + "_" + destFC, "SIMPLE", originFC, destFC,
                                               "NONE", "MANY_TO_MANY", "tmpFC", rAttributes, "OBJECTID", originKey,
                                               "OBJECTID", destKey)

        #delete the intersect feature class
        gp.AddMessage("Deleting temporary intersect feature class...")
        gp.Delete_management("tmpFC")

        #compact the database
        gp.AddMessage("Compacting the database " + gdbPath + "...")
        gp.Compact_management(gdbPath)

    except:
        print gp.GetMessages(2)


def MergePoints(): # Updates fields in a master feature class based on intersection of subset dataset

    # --------------------------Get input parameters-------------------------
    gp.workspace = sys.argv[1]
    species = gp.ListFeatureClasses("*","POINT")    # Species Feature Classes
    gp.workspace = sys.argv[2]
    states = gp.ListFeatureClasses("*","POINT")    # States feature classes

    # ----------------------processing loop----------------------------------

    for state in states:
        
        gp.workspace = sys.argv[2]
        
        # create a layer for the state feature class
        gp.MakeFeatureLayer_management(state, "lyrState")
        
        # for each species feature class in the workspace...
        
        gp.workspace = sys.argv[1]
        
        for spec in species:
            mergedata = spec.split(".")[0]
            gp.addmessage("Merging: " + mergedata + " to " + state)
            
            # create a field to hold the presence data (if its not already there)
            if not gp.listfields("lyrState", mergedata):
                gp.AddField_management("lyrState", mergedata, "LONG")
            
            # create a layer for the sub feature class
            gp.MakeFeatureLayer_management(spec, "lyrSpec")
            
            # check intersection
            gp.SelectLayerByLocation_management("lyrState", "ARE_IDENTICAL_TO", "lyrSpec", "#", "NEW_SELECTION")
            
            # calculate the value "1" for all selected records
            gp.CalculateField_management("lyrState", mergedata, "1")
