#----------------------------------------------------------------------------------------------------------------
#Create ED's from all CB's in state
#Input is a list of state ID's to process
#Output is a SVG file of is a generalised ED's

#Nick Earwaker
#Lovell Johns Ltd
#15-07-16

#--Input variables
#generalizeRatio			- % of original points in the line that are retained (expressed as a decimal)
#writeStateBnds				- Output state boundaries to the SVG file (True or False)
#EDfield					- Field name in the cluster input which is used to generate the ED boundaries  ("ConDis" or "Labels")

#shapefilePath				- Base folder location that stores a folder containing a Shapefile for each state to process 
#							- The state folder name will be of this format "nhgis0005_shapefile_tl2010_<inputStates index * 10>_ block_2010"
#							- The Shape file name will be of this format <state code>_block_2010.shp"

#clusterPath				- Folder location that stores all cluster input files for processing
#outputPath					- Output folder path
#outputFileName 			- Output SVG file name (Eg = 'output.svg')
#inputStates[]				- List of state ID numbers to process	
#mapScale 					- Scale of output SVG i.e. 1:<mapScale>
#-----------------------------------------------------------------------------------------------------------------

from osgeo import ogr
import os
import json
import visvalingamwyatt as vw
import time
import pandas as pd
import glob as glob

startTime = time.time()

#--Define variables
generalizeRatio=0.1					#Generalization for SVG coordinate output 0.1 retains 10% of the original points
mapExtent=[0,0,0,0]					#Stores the Max map extent of all the input states
nofEDs=[]							#Stores the number of EB's for each of the input states (starting at 0)
stateIndex=-1						#Index no of the current state processing
writeStateBnds = True				#Write the state boundaries or not
EDfield = "Labels"					#Field name in the cluster input which is used to generate the ED boundaries  "ConDis" or "Labels"

#--Define file input-output variables
shapefilePath='/Users/frankanayet/Desktop/Maps/'			#Base folder location that stores the shape files
clusterPath='/Users/frankanayet/Desktop/Maps/'				#Base folder location that cluster input files
outputPath='/Users/frankanayet/Desktop/Maps/'						#Base output path
inputStates=[44]												#List of state ID numbers to process
print str(inputStates[0]) + '_'+ EDfield + '.svg'
outputFileName = str(inputStates[0]) + '_'+ EDfield + '.svg'								#Output SVG file name Only works for 1 state at a time
	

#--Define SVG output variables
inputScale = 1              #Input should always be ground coordinates, thus input scale = 1.
unitspermm = 0.001			#Metres/mm
ptsPerMM = 2.834646         #Points per mm
mapScale = 1000000			#Scale of output SVG i.e. 1:<mapScale>
mapScaleFact = ptsPerMM * (inputScale / (mapScale * unitspermm))		#Get the map scale factor

#--Loop thru each input file (ie state)
for inputFile in inputStates:
	#Open the shape file
	stateIndex+=1
	print inputFile, 'input'
	shapefile = glob.glob(shapefilePath + "nhgis0005_shapefile_tl2010_" + str(inputFile * 10) + "_block_2010/*.shp")          #Shape path = <shapefilePath>\nhgis0005_shapefile_tl2010_<inputStates index * 10>_ block_2010\<state code>_block_2010.shp
	print shapefile, 'shape'
	dataSource = ogr.Open(shapefile[0])
	
	if not dataSource:
		raise IOError("Could not open '%s'"%ds_fname)
		
	layer = dataSource.GetLayer()
	
	#Get the bottom left - top right of the input in map coordinates and work out the max map extent
	layerExtent=layer.GetExtent()	
	if stateIndex == 0:
		mapExtent[0] = int(layerExtent[0])
		mapExtent[1] = int(layerExtent[1])		
		mapExtent[2] = int(layerExtent[2])		
		mapExtent[3] = int(layerExtent[3])		
	else:
		if int(layerExtent[0]) < mapExtent[0]:
			mapExtent[0] = int(layerExtent[0])
		if int(layerExtent[1]) < mapExtent[1]:
			mapExtent[1] = int(layerExtent[1])		
		if int(layerExtent[2]) > mapExtent[2]:
			mapExtent[2] = int(layerExtent[2])		
		if int(layerExtent[3]) > mapExtent[3]:
			mapExtent[3] = int(layerExtent[3])
			
	#Get cluster input and sore in pandas data frame
	clusterInput = glob.glob(clusterPath + "Cluster_" + str(inputStates[stateIndex]) + ".csv")
	print clusterInput	
	xy_db = pd.read_csv(clusterInput[0]) 										
	
	#Set default variables for the processing of each state
	jsonFiles=[]								#List of temp file names that store the generalised unioned geometry for each ED
	outFiles=[]									#List of temp files that store the generalised unioned geometry for each ED					
	geomCollection=[]							#Collection of CB geometries for each ED
	forState = []								#Array of ED geometries to make the state boundary
			
	#Define the number of ED in the state depending on the cluster input filed
	if EDfield == "ConDis":
		edCount = len(xy_db.ConDis.unique())
	else:
		edCount = len(xy_db.Labels.unique())
	
	nofEDs.append(edCount)	#Add the number of ED's for the input state	to list of all states processing
	
	#Build the list of temp output files and geometry collections for the ED's in the state
	for n in range(0, edCount):
		jsonFiles.append("ed_" + str(inputFile) + "_" + str(n) + ".geojson")
		geomCollection.append(ogr.Geometry(ogr.wkbMultiPolygon))
	
	#Open all required temp files	
	for outFile in jsonFiles:
		print outFile, 'outFile'
		outFiles.append(open(outputPath + outFile, 'w'))
		
	#Read each CB feature
	for feature in layer:
		edReference = int(xy_db.loc[xy_db.GISJOIN == feature.GetField("GISJOIN"),EDfield])					#Define the ED index from the cluster input
		#print edReference	
		geomCollection[edReference].AddGeometry(feature.GetGeometryRef())									#Add feature to the relevant geometry collection
	
	#Union all features in each of the geometry collection, generalise and write as GEOJSON to file
	indexCnt=-1
	for toUnion in geomCollection:
		indexCnt+=1
		if toUnion.GetGeometryCount() != 0:						#Check we have geometry for the ED (Should always be the case though)			
			testUnion = toUnion.UnionCascaded()
			forState.append(testUnion)							#Store the unioned ED geometry in list - used to create a state boundary
			generalisedGeom = vw.simplify_geometry(json.loads(testUnion.ExportToJson()), ratio=generalizeRatio)
			json.dump(generalisedGeom, outFiles[indexCnt])		#Write the resulting GeoJSON-file		
			outFiles[indexCnt].close()
			
	#Create geojson of the state boundary if necessary
	if writeStateBnds:
		stateFile = open(outputPath + "state_" + str(inputFile) + ".geojson", 'w')	
		multipolygon = forState[0]   
		for n in range(1, len(forState)):
			multipolygon = multipolygon.Union(forState[n])	
		#Generalise the state polygon
		testgeom2 = vw.simplify_geometry(json.loads(multipolygon.ExportToJson()), ratio=generalizeRatio)
		json.dump(testgeom2, stateFile)	
		stateFile.close()


#---EXPORT TO SVG PROCESS

#Define size of SVG doc in pts
artSizeX=((mapExtent[2]-mapExtent[0])*mapScaleFact)		
artSizeY=((mapExtent[3]-mapExtent[1])*mapScaleFact)		

#Get origin in map coordinates (m)
blx=mapExtent[0]
bly=mapExtent[1]

#Open SVG output file
f = open(outputPath + outputFileName, 'w') 

#Define SVG header
f.write("<?xml version='1.0' encoding='utf-8'?>")
f.write("<!DOCTYPE svg PUBLIC '-//W3C//DTD SVG 1.0//EN' ")
f.write("'http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd'[")
f.write("]>")
f.write("<svg width='" + str(artSizeX) + "' height='" + str(artSizeY) + "' viewBox='0 0 " + str(artSizeX) + " " + str(artSizeY) + "' id='usmap'>")

#Define map styles
f.write("<style id='mapstyles' type='text/css'>")
f.write(".ed{fill:none;stroke:#999999;stroke-width:0.5}")				#Election District Boundary Line
f.write(".state{fill:none;stroke:#000000;stroke-width:1}")				#State District Boundary Line
f.write("</style>")

#--Convert GEOJSON files to SVG.
stateIndex=-1
for inputFile in inputStates:
	stateIndex+=1
	edCnt=-1
	f.write("<g id='state-" + str(inputFile) + "'>")
	#Read the GEOJSON file.
	for n in range(0, nofEDs[stateIndex]):
		intSVGFeatCnt=0
		edCnt+=1
		json_data=open(outputPath + "ed_" + str(inputFile) + "_" + str(edCnt) + ".geojson",'r')                         
		data = json.load(json_data)	
		json_data.close()
		#Write features to SVG
		f.write("<g id='ed-" + str(inputFile) + "-" + str(edCnt) + "'>")
		for feature in data['coordinates']:
			intSVGFeatCnt+=1
			intVertexCnt=0
			outputLine = "<path class='ed' id='f" + str(intSVGFeatCnt) + "' d='"   
					
			#Define feature array for poly and multi poly
			if data['type'] == "Polygon":
				thefeature = feature
			else:
				thefeature = feature[0]
			
			for feature2 in thefeature:   
				intVertexCnt += 1
				strX = str(round(((feature2[0] - blx) * mapScaleFact),1))
				strY = str(round((artSizeY - ((feature2[1] - bly) * mapScaleFact)),1))
				if intVertexCnt == 1:
					outputLine += "M " + strX + " " + strY
				else:
					outputLine += " L " + strX + " " + strY		
			outputLine +=  " z' />"
			f.write(outputLine)
		f.write("</g>")
	#Write the state boundary inf required
	if writeStateBnds:
		json_data=open(outputPath + "state_" + str(inputFile) + ".geojson",'r')
		data = json.load(json_data)
		json_data.close()
		#Write features to SVG
		f.write("<g id='statebnd-" + str(inputFile) + "'>")
		for feature in data['coordinates']:
			intSVGFeatCnt+=1
			intVertexCnt=0
			outputLine = "<path class='state' id='f" + str(intSVGFeatCnt) + "' d='"
			for feature2 in feature[0]:
				intVertexCnt += 1
				strX = str(round(((feature2[0] - blx) * mapScaleFact),1))
				strY = str(round((artSizeY - ((feature2[1] - bly) * mapScaleFact)),1))
				if intVertexCnt == 1:
					outputLine += "M " + strX + " " + strY
				else:
					outputLine += " L " + strX + " " + strY		
			outputLine +=  " z' />"
			f.write(outputLine)
		f.write("</g>")
	f.write("</g>")

f.write("</svg>")	
f.close()

#End of process
endTime = time.time()
print "Process Complete in " +  str((endTime - startTime)/60) + " mins."
#-----------End of Script