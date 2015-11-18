# Essential GIS modules
# Sample code only 
def gdal(filename,GA_ReadOnly, shapefileName) # GDAL is a translator library with Python bindings that allows access to raster data using a unified abstract layer. Bundled with it is OGR, which provides similar functionality for vector data.
    import gdal
    from gdal const import* 
    #Open the raster dataset
    dataset=gdal.Open(filename,GA_ReadOnly)
    #Print the projection of the data 
    print dataset.GetProjection()    - 
    # Using OGR
    import ogr
    # Get the driver
    driver=ogr.GetDriverByName('ESRIShapefile')
    #Open a shapefile
    dataset=driver.Open(shapefileName,0)

def numpy # numpy is a package that enables n-dimensional array manipulation
    from numpy import * 
    #Sample IO Table data
    ioSample=[[1,2],[3,4]]
    #Turn into a numpy array
    ioMatrix=array(ioSample)
    #Find the inverse of ioMatrix
    ioMatrixInv=linalg.inv(ioMatrix)

def NetworkX # NetworkX is a Python package for the creation, manipulation, and study of the structure, dynamics, and functions of complex networks
    import networkx as nx
    #Create a graph
    g=nx.Graph()
    #Populate the graph
    g.add_node(1)
    g.add_node(2)
    g.add_node(3)
 
    #Createedges
    g.add_edge(1,2)
    g.add_edge(1,3) 
    #Print the neighbors of node 1(returns 2)
    print g.neighbors(1)

def xlrd #  xlrd is a Python module that allows one to read Excel files without the need of Microsoft Excel or Windows
    import xlrd
    #Open the Excel file
    bok=xlrd.open_workbok("excelFile.xls")
    #Read the first sheet in the Excel workbook
    shet=bok.sheet_by_index(0)
    #Read the first row from column A to E 
    rowValues=shet.row_values(0,start_colx=0,end_colx=4)
    #Print the row values
    for value in row Values: print value

def xlwt #  xlwt is a Python module that allows for cross platform Excel file creation without the need of Microsoft Office.
    impor txlwt
    #Create a new workbok
    bok=xlwt.Workbok()
    #Add a new sheet
    shet=bok.ad_sheet("MySheet")
    #Write the number 5 in the first row,first column
    shet.write(0,0,5)
    #Savethefile
    bok.save("myExcelFile.xls")

def replace_text(): # replaces text in all files defined by extension

    import os, sys, string, os.path
    InFolder = "D:/arcgisserver/config-store/services"
    ext = ".json"
    original = 'minInstancesPerNode": 1'
    replacement = 'minInstancesPerNode": 0'
    for root, dirs, files in os.walk(InFolder):
        for name in files:
            basename, extension = os.path.splitext(name)
            if extension.lower() == ext:
                theFile = open(os.path.join(root, name),'r')
                old = theFile.read()
                theFile.close()
                new = old.replace(original, replacement)
                theFile = open(os.path.join(root, name),'w')
                theFile.write(new)
                theFile.close()
                print name + " complete"
              
    input("Press ENTER to continue...")
