import os
import sys
import getopt

#Plugins path for qgis
#OSX: /Applications/QGIS.app/Contents/Resources/python
#Linux: /usr/share/qgis/python/plugins
sys.path.append("/Applications/QGIS.app/Contents/Resources/python")
 
from qgis.core import *
from datetime import datetime

def usage():
    print "\n Create ShapeFile from VIIRS data"
    print " -d: directory for save ShapeFile"

def initConfig():
    ligand = ""
    protein = ""
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'd:h', ['directory=', 'help'])
        if not opts:
          print ' Missing parameters'
          usage()
          sys.exit(2)
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(2)
        elif opt in ('-d', '--directory'):
            directory = arg
        else:
            usage()
            sys.exit(2)
    return directory

if __name__ == "__main__":

	app = QgsApplication([],False)

	#Prefix path where qgis is installed
	#For OSX : /Applications/QGIS.app/Contents/MacOS/
	#For Linux: /usr
	app.setPrefixPath("/Applications/QGIS.app/Contents/MacOS/", True)

	app.initQgis()

	directory = initConfig()

	#Get filename for the day
	day_of_year = datetime.now().timetuple().tm_yday
	year = datetime.now().year
	dayfolder = str(year)+str(day_of_year)

	if not os.path.isdir(directory+"/"+dayfolder):
		print "Directory not found, no viirs data for processing"
	else:
		#Set name and path of the cvs file (for input and output)
		logPath = directory+"/"+dayfolder+"/VIIRS_log.log"
		if not os.path.isfile(logPath):
			print "Log not found."
		else:
			logFile = open(logPath)
			timeupdate = logFile.readlines()[-1].strip()

			viirsname = directory+dayfolder+"/VIIRS_I_South_America_VNP14IMGTDL_NRT_"+dayfolder+"_"+timeupdate+"_clean.txt"
			shapefile = directory+dayfolder+"/VIIRS__I_South_America_VNP14IMGTDL_NRT_"+dayfolder+"_"+timeupdate

			#Set uri for make the qgis vector layer
			uri = 'file:///%s?crs=%s&xField=%s&yField=%s&decimal=%s&spatialIndex=%s&subsetIndex=%s&watchFile=%s&encoding=%s&geomType=%s&delimiter=%s' % (viirsname, 'EPSG:4326', 'longitude', 'latitude', '.', 'no', 'no', 'no', 'UTF-8', 'point',',')

			#Create vector layer
			layer = QgsVectorLayer(uri, "VIIRS_"+dayfolder+"_"+timeupdate, 'delimitedtext')
			if not layer.isValid():
				print "Layer error"
			else:		
				#Save as shapefile
				QgsVectorFileWriter.writeAsVectorFormat(layer, shapefile + '.shp', 'UTF-8', layer.crs(), 'ESRI Shapefile')
				print "Shapefile complete"









