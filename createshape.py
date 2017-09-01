import os
import sys
import getopt
import timeit
import shutil




#Plugins path for qgis
#OSX: /Applications/QGIS.app/Contents/Resources/python
#Linux: /usr/share/qgis/python/plugins
sys.path.append("/Applications/QGIS.app/Contents/Resources/python")

#plugins path for processing (QGIS)
sys.path.append("/Applications/QGIS.app/Contents/Resources/python/plugins")
 
from qgis.core import *
from datetime import datetime

def usage():
    print "\n Create ShapeFile from VIIRS data"
    print " -d: directory for save ShapeFile"
    print " -m: directory of masks shapes folder (Chilean Zones)"

def initConfig():
    ligand = ""
    protein = ""
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'd:m:h', ['directory=', 'maskdir=','help'])
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
		elif opt in ('-m', '--maskdir'):
		    maskdirectory = arg
		else:
		    usage()
		    sys.exit(2)
    return [directory, maskdirectory]


if __name__ == "__main__":

	directories = initConfig()
	directory = directories[0]
	maskDirectory = directories[1]

	app = QgsApplication([],False)

	#Prefix path where qgis is installed
	#For OSX : /Applications/QGIS.app/Contents/MacOS/
	#For Linux: /usr
	app.setPrefixPath("/Applications/QGIS.app/Contents/MacOS/", True)

	app.initQgis()

	import processing
	from processing.core.Processing import Processing

	Processing.initialize()

	#Get filename for the day
	day_of_year = datetime.now().timetuple().tm_yday
	year = datetime.now().year
	dayfolder = str(year)+str(day_of_year)

	dayfolderPath = os.path.join(directory, dayfolder)

	if not os.path.isdir(dayfolderPath):
		print "Directory not found, no viirs data for processing"
	else:
		#Set name and path of the cvs file (for input and output)
		logPath =  os.path.join(dayfolderPath, "VIIRS_log.log")
		if not os.path.isfile(logPath):
			print "Log not found."
		else:
			logFile = open(logPath)
			timeupdate = logFile.readlines()[-1].strip()
			logFile.close()

			viirsname = os.path.join(dayfolderPath, "VIIRS_I_South_America_VNP14IMGTDL_NRT_"+dayfolder+"_"+timeupdate+".txt")
			shapefile = os.path.join(dayfolderPath, "VIIRS__I_South_America_VNP14IMGTDL_NRT_"+dayfolder+"_"+timeupdate+".shp")

			#Set uri for make the qgis vector layer
			uri = 'file:///%s?crs=%s&xField=%s&yField=%s&decimal=%s&spatialIndex=%s&subsetIndex=%s&watchFile=%s&encoding=%s&geomType=%s&delimiter=%s' % (viirsname, 'EPSG:4326', 'longitude', 'latitude', '.', 'no', 'no', 'no', 'UTF-8', 'point',',')

			#Create vector layer
			layer = QgsVectorLayer(uri, "VIIRS_"+dayfolder+"_"+timeupdate, 'delimitedtext')
			if not layer.isValid():
				print "Layer error"
			else:		
				#Save as shapefile
				QgsVectorFileWriter.writeAsVectorFormat(layer, shapefile, 'UTF-8', layer.crs(), 'ESRI Shapefile')
				#print "Shapefile complete"

				tempPath = os.path.join(dayfolderPath, "temp")

				if not os.path.isdir(tempPath):
					os.makedirs(tempPath)

				start_time = timeit.default_timer()
				temp01Path = os.path.join(tempPath, "temp_nortegrande.shp")
				temp02Path = os.path.join(tempPath, "temp_nortechico.shp")
				temp03Path = os.path.join(tempPath, "temp_centro.shp")
				temp04Path = os.path.join(tempPath, "temp_sur.shp")
				temp05Path = os.path.join(tempPath, "temp_austral.shp")

				norteGPath = os.path.join(maskDirectory, "MASCARAS_FOCOS_POR_ZONAS", "01_ZONA_NORTE_GRANDE.shp")
				norteCPath = os.path.join(maskDirectory, "MASCARAS_FOCOS_POR_ZONAS", "02_ZONA_NORTE_CHICO.shp")
				centroPath = os.path.join(maskDirectory, "MASCARAS_FOCOS_POR_ZONAS", "03_ZONA_CENTRAL.shp")
				surPath = os.path.join(maskDirectory, "MASCARAS_FOCOS_POR_ZONAS", "04_ZONA_SUR.shp") 
				australPath = os.path.join(maskDirectory, "MASCARAS_FOCOS_POR_ZONAS", "05_ZONA_AUSTRAL.shp")

				viirs_layer = QgsVectorLayer(shapefile, "partial_layer", "ogr")
				#viirs_layer = QgsVectorLayer(os.path.join(dayfolderPath, "viirstest.shp"), "partial_layer", "ogr")

				northG_layer =	QgsVectorLayer(norteGPath, "norteG_vector_Layer", "ogr")
				northC_layer =	QgsVectorLayer(norteCPath, "norteCh_vector_Layer", "ogr")
				center_layer =	QgsVectorLayer(centroPath, "central_vector_Layer", "ogr")
				south_layer =	QgsVectorLayer(surPath, "south_vector_Layer", "ogr")
				austral_layer = QgsVectorLayer(australPath, "austral_vector_Layer", "ogr")
				#print "Layer upload complete"

				clipLayerPath = ""

				processing.runalg("qgis:clip", viirs_layer, northG_layer, temp01Path)
				tempNorthG_layer = QgsVectorLayer(temp01Path, "northg", "ogr")
				if not tempNorthG_layer.isValid():
					print "North Gr clip layer error"
				else:
					clipLayerPath += temp01Path+";"

				processing.runalg("qgis:clip", viirs_layer, northC_layer, temp02Path)
				tempNorthC_layer = QgsVectorLayer(temp02Path, "northc", "ogr")
				if not tempNorthC_layer.isValid():
					print "North Ch clip layer error"
				else:
					clipLayerPath += temp02Path+";"

				processing.runalg("qgis:clip", viirs_layer, center_layer, temp03Path)
				tempCenter_layer = QgsVectorLayer(temp03Path, "center", "ogr")
				if not tempCenter_layer.isValid():
					print "Center clip layer error"
				else:
					clipLayerPath += temp03Path+";"

				processing.runalg("qgis:clip", viirs_layer, south_layer, temp04Path)
				tempSouth_layer = QgsVectorLayer(temp04Path, "south", "ogr")
				if not tempSouth_layer.isValid():
					print "South clip layer error"
				else:
					clipLayerPath += temp04Path+";"

				processing.runalg("qgis:clip", viirs_layer, austral_layer, temp05Path)
				tempAustral_layer = QgsVectorLayer(temp05Path, "austral", "ogr")
				if not tempAustral_layer.isValid():
					print "Austral clip layer error"
				else:
					clipLayerPath += temp05Path+";"
								
				layerFeaturesCount = 0
				layerFeaturesCount += tempNorthG_layer.featureCount()
				layerFeaturesCount += tempNorthC_layer.featureCount()
				layerFeaturesCount += tempCenter_layer.featureCount()
				layerFeaturesCount += tempSouth_layer.featureCount()
				layerFeaturesCount += tempAustral_layer.featureCount()

				if layerFeaturesCount == 0:
					print "No fire detected"
					print []
				else:
					nameFile = "VIIRS_"+dayfolder+"_"+timeupdate+"_CLIP"
					clipLayerPath = clipLayerPath.strip(";")
					finalClipPath = os.path.join(dayfolderPath, nameFile+".shp")
					processing.runalg("qgis:mergevectorlayers", clipLayerPath, finalClipPath)
					print "VIIRS shape created successfully"
					outList = []
					listdir = os.listdir(dayfolderPath)
					for file in listdir:
						if nameFile in file:
							outList.append(os.path.join(dayfolderPath, file))
					print outList
					#print finalClipPath.strip(".shp")+".*"

				
				shutil.rmtree(tempPath)
				elapsed = timeit.default_timer() - start_time
				#print "time: ", elapsed






