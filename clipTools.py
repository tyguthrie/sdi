def ClipRaster(workspace,clip_file,in_raster): # Clips a raster
    # Set the workspace
    gp.workspace = workspace
    try:
        # for each record of the input clip file
        # clip the input raster
        gp.addmessage("The following text can be pasted into a fragstats batch file e.g. fragbatch.fbt")
        rows = gp.SearchCursor(clip_file)
        
        row = rows.Next()
        while row:
            # get the name of the county and use it to create the output raster name
            # ensure that the output raster name has no spaces and is <= 13 chars
            namestring = row.name
            namestring = namestring.replace(" ","_")
            out_raster = namestring[:13]
            # output the text for use in fragstats batch file
            gp.addmessage(gp.workspace + "\\" + out_raster + ",x,9999,x,x,IDF_ARCGRID")
            # get the polygon coordinates
            geom = row.shape
            in_poly = ""
            PntArray = geom.getpart(0) # assumes all polygons are single part
            PntArray.Reset
            pnt = PntArray.Next()
            while pnt:
                in_poly = in_poly + str(pnt.x) + " " + str(pnt.y) + ";"
                pnt = PntArray.Next()
            # set the analysis extent to the shape extent
            gp.extent = geom.extent
            # perform the raster extraction
            gp.ExtractByPolygon_sa(in_raster, in_poly, out_raster, "INSIDE")
            row = rows.Next()
    except:
        gp.GetMessages

def ClipReproject(input_datasets,out_workspace,clip_features,prefix,Coordinate_System): # Clips and reprojects multiple input datasets
    datasetList = input_datasets.split(";")

    # use BLM default if not specified
    if Coordinate_System == "#" or not Coordinate_System:
        arcpy.AddMessage("Using Default BLM Coordinate System")
        Coordinate_System = "PROJCS['NAD_1983_Albers',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Albers'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-96.0],PARAMETER['Standard_Parallel_1',29.5],PARAMETER['Standard_Parallel_2',45.5],PARAMETER['Latitude_Of_Origin',23.0],UNIT['Meter',1.0]];-16901100 -6972200 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision"
    # set geographic transformations environment variable
    arcpy.env.geographicTransformations = "NAD_1983_To_WGS_1984_5; NAD_1927_To_NAD_1983_NADCON"

    # for each input dataset
    for dataset in datasetList:
        # clean up the name
        dataset = string.replace(dataset,"'","")
        # if name contains dots this will cause problems identifying the output feature class name,
        # so take the portion after the last dot by splitting the string from the right and popping
        # the segment into the fc variable; pop function used because unknown whether it will split
        # into one or two pieces
        fc = string.rsplit(os.path.basename(dataset),".",1).pop()
        arcpy.AddMessage("Processing " + fc)
        
        # clip
        try:
            arcpy.AddMessage("clipping...")
            clip_output = out_workspace + "\\" + prefix + "_" + fc + "_clip"
            
            if arcpy.Exists(clip_output):
                arcpy.Delete_management(clip_output)
            arcpy.Clip_analysis(dataset, clip_features, clip_output, "")
        except:
            arcpy.AddMessage("Error clipping " + dataset)
            arcpy.AddMessage(arcpy.GetMessages())

        # reproject
        try:
            arcpy.AddMessage("reprojecting...")
            
            # Determine if the input has a defined coordinate system
            dsc = arcpy.Describe(clip_output)
            sr = dsc.spatialReference
            if sr.Name == "Unknown":
                # skip
                arcpy.AddMessage("Cannot project " + clip_output)
                arcpy.AddMessage("Spatial reference unknown")
            
            else:
                prj_output = clip_output + "_prj"
                if arcpy.Exists(prj_output):
                    arcpy.Delete_management(prj_output)
                arcpy.Project_management(clip_output, prj_output, Coordinate_System)
                if arcpy.Exists(clip_output):
                    arcpy.Delete_management(clip_output)

        except:
            arcpy.AddMessage("Error projecting " + dataset)
            arcpy.AddMessage(arcpy.GetMessages())

def ClipShip(Layer,infile,outzip): # Clips and ships

    # Local variables...
    Clip_Features = "%scratchworkspace%\\%layer%.shp"

    # Process: Clip...
    gp.Clip_analysis(Layer, Clip_Area, Clip_Features, "")

    # Delete zip file if exists
    if os.path.exists(outzip):
        os.unlink(outzip)

    zip = zipfile.ZipFile(outzip, 'w', zipfile.ZIP_DEFLATED)
    path = infile.replace("shp","*")
    infiles = glob.glob(path)

    for each in infiles:
        try:
            zip.write(each, os.path.basename(each))
        
        except Exception, e:
            gp.AddWarning("    Error adding %s: %s" % (each, e))

    zip.close()
