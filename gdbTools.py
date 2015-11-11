def updateDomains():
    # updates domains from coded values to actual values and fixes data in fields
    # make sure map service is stopped or else you won't get a schema lock for the domains
    env.env.wors = "Database Connections\\IN_OWNER@cosde.tnc.sde"
    # here are the domains to be updated
    domains = [["IN_AdjuvantNames","ADJUVANT_HERBICIDENAME"],
               ["IN_App Method","APP_METHOD"],
               ["IN_HerbicideNames","HERBICIDE_HERBICIDENAME"],
               ["IN_HerbicideNames","HERBICIDE_HERBICIDENAME2"],
               ["IN_Treatment Type","TREATMENT_TYPE"]]
    # this is the feature class
    fc = "Database Connections\\IN_OWNER@cosde.tnc.sde\\tncgdb.IN_OWNER.IN_Invasives"
    arcpy.MakeFeatureLayer_management(fc, "lyr")
    for domain in domains:
        # export to a temp table on disk
        tbl = "c:\\temp\\" + domain[1] + ".dbf"
        arcpy.DomainToTable_management(env.workspace, domain[0], tbl, "code", "desc")
        # step thru the table
        rows = arcpy.SearchCursor(tbl)
        for row in rows:
            # delete the old domain value
            arcpy.DeleteCodedValueFromDomain_management(env.workspace, domain[0], row.code)
            print "deleting " + domain[0] + "," + row.code
            # add the new one
            arcpy.AddCodedValueToDomain_management(env.workspace, domain[0], row.desc, row.desc)
            print "adding " + domain[0] + "," + row.desc
            # find the rows in the table with this domain and update them
            query = '"' + domain[1] + '" = ' + "'" + row.code + "'"
            exp = '"' + row.desc + '"'
            arcpy.SelectLayerByAttribute_management("lyr", "NEW_SELECTION", query)
            print query, exp, arcpy.GetCount_management("lyr")
            if arcpy.GetCount_management("lyr") > 0:
                arcpy.CalculateField_management("lyr", domain[1], exp)
