def EXIF_update():

# this is a quickie script that I wrote to update the photo EXIF
# metadata on image files in the folder in which its run
# It updates the datetime metadata to be the same as the first 8 digits
# of the filename, which represent the data in YYYYMMDD format

    import pyexiv2, datetime, os
    dir = os.getcwd()
    for name in os.listdir(dir):
        basename, extension = os.path.splitext(name)
        if (extension.lower() == ".jpg"
         or extension.lower() == ".png"
         or extension.lower() == ".tif"):
            year = int(name[0:4])
            month = int(name[4:6])
            day = int(name[6:8])
            if month == 0: month = 1
            if day == 0: day = 1
            photoDate = datetime.datetime(year, month, day)
            metadata = pyexiv2.ImageMetadata(name)
            metadata.read()
            for key in ["Exif.Image.DateTime","Exif.Photo.DateTimeOriginal","Exif.Photo.DateTimeDigitized"]:
                if key in metadata.exif_keys:
                    print "Updating key", key, metadata[key].value, "to", photoDate
                    metadata[key].value = photoDate
                else:
                    print "Adding key", key, "with value", photoDate
                    metadata[key] = pyexiv2.ExifTag(key, photoDate)
                metadata.write()

def  EXIF2File():

    # update filenames from dateTimeOriginal where it exists
    # only works in root folder

    import pyexiv2, datetime, os
    dir = os.getcwd()
    for root, dirs, files in os.walk(dir):
        for name in files:
            basename, extension = os.path.splitext(name)
            filename = os.path.join(root, name)
            if extension.lower() in (".jpg","jpeg",".png",".tif",".tiff"):
                metadata = pyexiv2.ImageMetadata(filename)
                metadata.read()
                key = "Exif.Photo.DateTimeOriginal"
                if key in metadata.exif_keys:
                    try:
                        newfilename = str(metadata[key].value)+ basename[8:] + extension
                        newfilename = newfilename.replace(":",".")
                        print "Updating filename from", name, "to", newfilename
                        os.rename(name, newfilename)
                    except:
                        print "Could not update",name

def File2EXIF():

    # updates the datetime metadata to be the same as the first 8 digits
    # of the filename, which represent the data in YYYYMMDD format

    import pyexiv2, datetime, os
    dir = os.getcwd()
    for root, dirs, files in os.walk(dir):
        for name in files:
            basename, extension = os.path.splitext(name)
            filename = os.path.join(root, name)
            if extension.lower() in (".jpg","jpeg",".png",".tif",".tiff"):
                year = int(name[0:4])
                month = int(name[4:6])
                day = int(name[6:8])
                if month == 0: month = 1
                if day == 0: day = 1
                photoDate = datetime.datetime(year, month, day)
                metadata = pyexiv2.ImageMetadata(filename)
                metadata.read()
                for key in ["Exif.Image.DateTime","Exif.Photo.DateTimeOriginal","Exif.Photo.DateTimeDigitized"]:
                    if key in metadata.exif_keys:
                        print "Updating key", key, metadata[key].value, "to", photoDate
                        metadata[key].value = photoDate
                    else:
                        print "Adding key", key, "with value", photoDate
                        metadata[key] = pyexiv2.ExifTag(key, photoDate)
                    metadata.write()


def XMLSearch(): # Searches for metadata in XML files

    # set variables
    xmlFiles = []
    xmlDocs = []
    Folders = [sys.argv[1]]
    subFolders = sys.argv[2]  # true or false
    strFind = sys.argv[3]
    strSection = sys.argv[4]
    dateBegin = sys.argv[5]   # searches publication date
    dateEnd = sys.argv[6]
    varProg = sys.argv[7]     # domain: 'complete', 'in work' or 'planned'
    varProj = sys.argv[8]
    varCoord = sys.argv[9]    # from reference shapefile, or feature class
    varInt = sys.argv[10]     # intersects or contains

        
        # return list of XML files in the target folder
        # by using glob to extract files with .xml extension
        # decide whether to search subfolders from user input
    if not (subFolders == "true"):
        xmlFiles = glob.glob(os.path.join(Folders[0],"*.xml"))
    else:
        # return list of XML files in folder and subfolders
        # by using glob to extract files with .xml extension
        # then loop, extracting list of subfolders until none left
        while Folders:
            newFolders = []
            for f in Folders:
                xmlFiles = xmlFiles + glob.glob(os.path.join(f,"*.xml"))
                newFolders = newFolders + [os.path.join(f,nf) for nf in os.listdir(f)
                                           if (os.path.isdir(os.path.join(f,nf)))]
            Folders = newFolders

    # write list of selected files to message window
    for x in xmlFiles:
        print x
    #    gp.addmessages(x)

    # parse the xml files into document object models
    xmldoc = xml.dom.minidom.parse(xmlFiles[0])
    alist = xmldoc.getElementsByTagName('citeinfo')

    # write xml output
    print alist[0].toxml()
