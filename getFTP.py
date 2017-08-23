import urllib 
from datetime import datetime
import os

def searchBox(coor, bloque):
	for seg in range(len(bloque)):
		if coor[0] <= bloque[seg][0] and coor[0] > bloque[seg][1] and coor[1] <= bloque[seg][2]:
			return True
	return False

#Get filename for the day
day_of_year = datetime.now().timetuple().tm_yday
year = datetime.now().year
filename = "VIIRS_I_South_America_VNP14IMGTDL_NRT_"+str(year)+str(day_of_year)+".txt"
fileout = "VIIRS_I_South_America_VNP14IMGTDL_NRT_"+str(year)+str(day_of_year)+"_clean.txt"
dayfolder = str(year)+str(day_of_year)
if not os.path.isdir("NASAdata/"+dayfolder):
	os.makedirs("NASAdata/"+dayfolder)

username = "benjartv"
password = "Ironmaiden1991"

#Get file from Active Fire Data NASA (via FTP)
urllib.urlretrieve('ftp://'+username+':'+password+'@nrt3.modaps.eosdis.nasa.gov/FIRMS/viirs/South_America/'+filename, "NASAdata/"+dayfolder+"/"+filename)

#Chilean block coordinates
bloque = [[-17.5, -22.7, -67.8],
		[-22.7, -24.4, -66.9],
		[-24.4, -28.4, -68.2],
		[-28.4, -36.5, -69.5],
		[-36.5, -38.9, -70.5],
		[-38.9, -44.3, -71.5],
		[-44.3, -51.9, -71.0],
		[-51.9, -55.1, -66.2]]


#Remove data from other countries than Chile
file = open("NASAdata/"+dayfolder+"/"+filename)
content = file.readlines()
file.close()

textout = ""
first = content.pop(0)
textout += first

for line in content:
	aux = line.strip().split(",")
	coordanda = [float(aux[0]), float(aux[1])]
	if searchBox(coordanda, bloque):
		auxText = ""
		for i in range(len(aux)-1):
			auxText += aux[i]+","
		auxText += aux[-1]+"\n"
		textout += auxText

file = open("NASAdata/"+dayfolder+"/"+fileout,"w")
file.write(textout)
file.close()






