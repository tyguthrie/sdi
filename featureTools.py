def ShapeOrientation(): # Determines whether a shape is taller or wider

    fc = arcpy.GetParameter(0)
    rows = arcpy.SearchCursor(fc)
    desc = arcpy.Describe(fc)
    shapefield = desc.ShapeFieldName
    for row in rows:
        geom = row.getValue(shapefield)
        ext = geom.extent
        h = abs(ext.YMax - ext.YMin)
        w = abs(ext.XMax - ext.XMin)
        if h > w:
            arcpy.AddMessage("this one is taller")
        elif w > h:
            arcpy.AddMessage("this one is wider")
        else:
            arcpy.AddMessage("undetermined")
