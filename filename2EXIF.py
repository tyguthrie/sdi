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
