import os
import sys

#Plugins path for qgis
#OSX: /Applications/QGIS.app/Contents/Resources/python
#Linux: /usr/share/qgis/python/plugins
sys.path.append("/Applications/QGIS.app/Contents/Resources/python")
 
from qgis.core import *
from datetime import datetime


app = QgsApplication([],False)

#Prefix path where qgis is installed
#For OSX : /Applications/QGIS.app/Contents/MacOS/
#For Linux: /usr
app.setPrefixPath("/Applications/QGIS.app/Contents/MacOS/", True)

app.initQgis()


#Get filename for the day
day_of_year = datetime.now().timetuple().tm_yday
year = datetime.now().year
dayfolder = str(year)+str(day_of_year)

#Set name and path of the cvs file (for input and output)
fullname = "/Users/benjamin/Desktop/NASAdata/"+dayfolder+"/VIIRS_I_South_America_VNP14IMGTDL_NRT_"+dayfolder+"_clean.txt"
filename = "/Users/benjamin/Desktop/NASAdata/"+dayfolder+"/VIIRS__I_South_America_VNP14IMGTDL_NRT_"+dayfolder

#Set uri for make the qgis vector layer
uri = 'file:///%s?crs=%s&xField=%s&yField=%s&decimal=%s&spatialIndex=%s&subsetIndex=%s&watchFile=%s&encoding=%s&geomType=%s&delimiter=%s' % (fullname, 'EPSG:4326', 'longitude', 'latitude', '.', 'no', 'no', 'no', 'UTF-8', 'point',',')

#Create vector layer
layer = QgsVectorLayer(uri, 'my_layer', 'delimitedtext')
print layer.isValid()

#Save as shapefile
QgsVectorFileWriter.writeAsVectorFormat(layer, filename + '.shp', 'UTF-8', layer.crs(), 'ESRI Shapefile')

