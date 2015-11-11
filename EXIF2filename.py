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

