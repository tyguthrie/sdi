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
