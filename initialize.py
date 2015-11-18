# -----------------Prepare python and arcpy environment----------------------
# Import system modules
import arcpy, os, sys, string, zipfile, glob, urllib, os.path, xml.dom.minidom
from time import strftime
from xml.dom.minidom import parseString
from arcpy import env
env.overwriteOutput = True
gp.CheckOutExtension("Spatial")
