# Creates landscape fragmentation signature
# ----------------------------------Description---------------------------------
# Generates landscape signatures for each polygon of a zonal feature class as
# an output feature class. A grid of polygons is created centered on the centroid
# of each input zone. This x-y grid represents the 2 dimensions: scale and
# histogram class, for further use as the 'footprint' of a histogram graphic which
# can be placed in the center of the zone in a GIS or 3D globe viewer. The database
# can also be used for other analyses of the landscape signature distribution.
#
# A landscape signature represents the combined histograms of the proportion
# of natural area surrounding a pixel, as measured at multiple scales.

# ------------------------------Get input parameters-----------------------------
gp.workspace = sys.argv[1]              # workspace
zone_fc = sys.argv[2]                   # zone feature class
id_field = sys.argv[3]                  # id field in the zone feature class
in_raster = sys.argv[4]                 # land cover grid
scale_range_min = float(sys.argv[5])    # scale range minimum
scale_range_max = float(sys.argv[6])    # scale range maximum
scale_range_step = float(sys.argv[7])   # scale range interval
total_scale = int((scale_range_max - scale_range_min)/scale_range_step + 1)
number_classes = int(sys.argv[8])       # number of histogram classes
output_fc = sys.argv[9]                 # name of output feature class
v_scale = float(sys.argv[10])           # vertical scale factor for output graphics
h_scale = float(sys.argv[11])           # horizontal scale factor for output graphics

# ----------------------execute the script in try/except--------------------------
try:
    # create a new output feature class and add fields
    gp.CreateFeatureClass_management(gp.workspace, output_fc, "POLYGON")
    gp.AddField(output_fc,"name","text", "100")
    gp.AddField(output_fc,"scale","float", "9")
    gp.AddField(output_fc,"total_scal","long", "9")
    gp.AddField(output_fc,"bin","float", "9")
    gp.AddField(output_fc,"total_bin","long", "9")
    gp.AddField(output_fc,"bin_label","text", "20")
    gp.AddField(output_fc,"count","long", "15")
    gp.AddField(output_fc,"total_cnt","long", "15")
    gp.AddField(output_fc,"proportion","float", "9")
    
    # define the output projection from input zone feature class
    gp.DefineProjection_management(output_fc, zone_fc)
    
    # create a cursor to access the table
    cur_out = gp.InsertCursor(output_fc)
    
    # determine the overall analysis extent by buffering the zone dataset
    gp.Buffer_analysis(zone_fc, "buffer.shp", scale_range_max)
    
    # focal mean processing and extraction of statistics at each scale
    for window_size in range(scale_range_min,scale_range_max+1,scale_range_step):
        # create the overall source grid
        gp.extent = gp.describe("buffer.shp").extent # reset the overall extent
        window_type = "CIRCLE " + str(window_size) + " MAP"
        scale_raster = in_raster + str(window_size)
        gp.addmessage("Creating source grid: " + scale_raster)
        gp.FocalStatistics_sa(in_raster, scale_raster, window_type, "MEAN", "NODATA")
        
        # generate statistics for each zone of the input zonal feature class
        cur_zone = gp.SearchCursor(zone_fc)
        row_zone = cur_zone.Next()
        while row_zone:
            poly_id = row_zone.getValue(id_field)
            geom = row_zone.shape
            gp.addmessage("Extracting statistics for scale: " +str(window_size)+ " and polygon: " + poly_id)
            
            # get the zone centroid and adjust so that output graphic will be centered
            lstValues = string.split(geom.centroid)
            centroid_x = float(lstValues[0]) - (float(number_classes) * h_scale)/2
            centroid_y = float(lstValues[1]) - (float(total_scale) * h_scale)/2
            
            # extract zone polygon to temporary feature class
            where_clause = '"' + id_field + '" = '+"'"+poly_id +"'"
            tempMask = poly_id + ".shp"
            gp.Select_analysis(zone_fc, tempMask, where_clause)
            
            # set the analysis extent to the shape extent
            gp.extent = geom.extent
            
            # perform the raster extraction and delete temporary inputs
            gp.ExtractByMask_sa(scale_raster, tempMask, "extract")
            if gp.exists(tempMask): gp.delete(tempMask)
            
            # slice grid to match histogram breaks and delete temporary inputs
            gp.Slice_sa("extract", "slice", number_classes, "EQUAL_INTERVAL","1")
            if gp.exists("extract"): gp.delete("extract")
            
            # create table using zonal statistics and delete temporary inputs
            gp.ZonalStatisticsAsTable_sa("slice", "Value", "slice", "zonestats.dbf")
            if gp.exists("slice"): gp.delete("slice")
            
            # get the total count from the zonal stats table
            gp.Statistics_analysis("zonestats.dbf", "total_count.dbf", "count sum")
            cur_sum = gp.SearchCursor("total_count.dbf")
            row_sum = cur_sum.Next()
            total_count = row_sum.sum_count
            if gp.exists("total_count.dbf"): gp.delete("total_count.dbf")
            del cur_sum
            
            # for each row of the zonestats.dbf table:
            cur_stats = gp.SearchCursor("zonestats.dbf")
            row_stats = cur_stats.Next()
            while row_stats:
                # create coordinates based on zone centroid and analysis window size
                min_x = centroid_x + (h_scale * (row_stats.value - 1))
                min_y = centroid_y + ((window_size - scale_range_min)/scale_range_step) * h_scale
                max_x = min_x + h_scale
                max_y = min_y + h_scale
                # create polygon
                polyArray = gp.createObject("Array")
                pnt = gp.createObject("Point")
                pnt.x = min_x
                pnt.y = min_y
                polyArray.add(pnt)          # lower left
                pnt.x = min_x
                pnt.y = max_y
                polyArray.add(pnt)          # upper left
                pnt.x = max_x
                pnt.y = max_y
                polyArray.add(pnt)          # upper right
                pnt.x = max_x
                pnt.y = min_y
                polyArray.add(pnt)          # lower right
                pnt.x = min_x
                pnt.y = min_y
                polyArray.add(pnt)          # lower left again
                
                # create a row in the output table and populate it
                row_out = cur_out.NewRow()
                row_out.shape = polyArray
                row_out.name = poly_id
                row_out.scale = window_size
                row_out.total_scal = total_scale
                row_out.bin =  row_stats.Value
                row_out.total_bin = number_classes
                row_out.bin_label = str(float(row_stats.Value-1)/float(number_classes)*100) + " - " + \
                    str(float(row_stats.Value)/float(number_classes)*100) + " %"
                
                row_out.count = row_stats.count
                row_out.total_cnt = total_count
                row_out.proportion = float(row_stats.count)/float(total_count) * v_scale
                cur_out.InsertRow(row_out)
                row_stats = cur_stats.Next() # end of loop through the zonestats.dbf
            del cur_stats
            if gp.exists("zonestats.dbf"): gp.delete("zonestats.dbf")
            row_zone = cur_zone.Next()       # end of loop through the rows of the input zone file
        del cur_zone  # delete the zone file cursor
    del cur_out  # delete the output file cursor
    if gp.exists("buffer.shp"): gp.delete("buffer.shp") # delete the temporary buffer file
except:
    # get the traceback object
    tb = sys.exc_info()[2]
    # tbinfo contains the line number that the code failed on and the code from that line
    tbinfo = traceback.format_tb(tb)[0]
    # concatenate information together concerning the error into a message string
    pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n    " + \
        str(sys.exc_type)+ ": " + str(sys.exc_value) + "\n"
    # generate a message string for any geoprocessing tool errors
    msgs = "GP ERRORS:\n" + gp.GetMessages(2) + "\n"
    
    # return gp messages for use with a script tool
    gp.AddError(msgs)
    gp.AddError(pymsg)
