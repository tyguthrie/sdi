def ListSDEServiceProperties(InFolder): # Lists SDE Connection properties in MXDs
    # walk through the directory structure starting
    # at the user-specified root folder
    for root, dirs, files in os.walk(InFolder):
        for name in files:
            basename, extension = os.path.splitext(name)
            if extension.lower() == ".mxd":
                
                # update the sde data sources in each mxd
                
                mxd_filename = os.path.join(root, name)
                mxd = arcpy.mapping.MapDocument(mxd_filename)
                arcpy.AddMessage("Reading: " + mxd_filename)
                
                # iterate through the layers in the mxd
                for lyr in arcpy.mapping.ListLayers(mxd):
                    
                    # look for sde connection files that match the old datasource workspace properties
                    if lyr.supports("SERVICEPROPERTIES"):
                        servProp = lyr.serviceProperties
                        if servProp.get('ServiceType') == "SDE":
                            arcpy.AddMessage("Layer: " + lyr.name)
                            arcpy.AddMessage("Server: " + servProp.get('Server'))
                            arcpy.AddMessage("Version: " + servProp.get('Version'))
                            arcpy.AddMessage("User: " +servProp.get('UserName'))
                            arcpy.AddMessage("--------------------------------------")
                            arcpy.AddMessage(" ")
                del mxd

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
