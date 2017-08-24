import urllib
from urllib2 import urlopen
from datetime import datetime
import os
import getopt
import sys

def usage():
    print "\n Get VIIRS data from NASA"
    print " -d: directory for save VIIRS data"

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

def searchBox(coor):
	#Chilean block coordinates
	bloque = [[-17.5, -22.7, -67.8],
			[-22.7, -24.4, -66.9],
			[-24.4, -28.4, -68.2],
			[-28.4, -36.5, -69.5],
			[-36.5, -38.9, -70.5],
			[-38.9, -44.3, -71.5],
			[-44.3, -51.9, -71.0],
			[-51.9, -55.1, -66.2]]

	for seg in range(len(bloque)):
		if coor[0] <= bloque[seg][0] and coor[0] > bloque[seg][1] and coor[1] <= bloque[seg][2]:
			return True
	return False

if __name__ == "__main__":
	#Set directory for save data
	directory = initConfig()

	#Get filename for the day
	day_of_year = datetime.now().timetuple().tm_yday
	year = datetime.now().year
	dayfolder = str(year)+str(day_of_year)
	filename = "VIIRS_I_South_America_VNP14IMGTDL_NRT_"+dayfolder+".txt"

	if not os.path.isdir(directory+"/"+dayfolder):
		os.makedirs(directory+"/"+dayfolder)

	#Set user and pass for VIIRS server
	username = "benjartv"
	password = "Ironmaiden1991"

	#Get file from Active Fire Data NASA (via FTP)
	req = urlopen('ftp://'+username+':'+password+'@nrt3.modaps.eosdis.nasa.gov/FIRMS/viirs/South_America/')
	data = req.read()

	if filename not in data:
		print "VIIRS file not found, please try later."
	else:
		content = data.split()
		index = content.index(filename)
		timeupdate = content[index-1].split(":")
		timeupdate = timeupdate[0]+timeupdate[1]

		filenamePath = directory+"/"+dayfolder+"/VIIRS_I_South_America_VNP14IMGTDL_NRT_"+dayfolder+"_"+timeupdate+".txt"
		fileoutPath = directory+"/"+dayfolder+"/VIIRS_I_South_America_VNP14IMGTDL_NRT_"+dayfolder+"_"+timeupdate+"_clean.txt"
		logPath = directory+"/"+dayfolder+"/VIIRS_log.log"

		if not os.path.isfile(filenamePath):		
			urllib.urlretrieve('ftp://'+username+':'+password+'@nrt3.modaps.eosdis.nasa.gov/FIRMS/viirs/South_America/'+filename, filenamePath)

			#Remove data from other countries than Chile
			file = open(filenamePath)
			content = file.readlines()
			file.close()

			textout = ""
			first = content.pop(0)
			textout += first

			for line in content:
				aux = line.strip().split(",")
				coordanda = [float(aux[0]), float(aux[1])]
				if searchBox(coordanda):
					auxText = ""
					for i in range(len(aux)-1):
						auxText += aux[i]+","
					auxText += aux[-1]+"\n"
					textout += auxText

			file = open(fileoutPath,"w")
			file.write(textout)
			file.close()

			logfile = open(logPath, "a")
			logfile.write(timeupdate+"\n")
			logfile.close()

			print "VIIRS file downloaded completely."
		else:
			print "VIIRS file is already updated."






