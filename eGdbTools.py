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
