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

