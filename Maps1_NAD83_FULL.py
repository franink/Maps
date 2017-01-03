# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 14:24:38 2014

@author: frankkanayet
"""

import sys
import os
import csv
from osgeo import ogr
from shapely.wkb import loads
from shapely.geometry import *
import pandas as pd
from random import uniform

def LoadFile(infile):
    """
    infile is a string with the file name
    Loads a .csv file for a single subject and takes the "practice", lines
    """
    state_db = []
    fin = open(infile, 'U')
    original_db = csv.reader(fin)
    for row in original_db:
        state_db.append(row)
    fin.close()
    return state_db

def Extract_Racial_Data(state_db):
    """
    state_db is a single state database with info about population by race for each cenus block
    this function returns a cropped database with only 5 racial categories: non-hispanic white,
    non-hispanic black, non hispanic asian, hispanic, non hiapanic other, the GISJOIN code, state code, 
    state name, and total population.
    """
    crop_state_db = []
    state_db[0].append('NH_White')
    state_db[0].append('NH_Black')
    state_db[0].append('NH_Asian')
    state_db[0].append('Hispanic')
    state_db[0].append('Other')
    state_db[0].append('Total')
    indGISJOIN = state_db[0].index('GISJOIN')
    indSTATE = state_db[0].index('STATE')
    indSTATEA = state_db[0].index('STATEA')
    indCDA = state_db[0].index('CDA')   #COngressional district
    indPOP = state_db[0].index('H7Z001') #This code is temporary I'm waiting for the real codes from downloaded table
    indPOP_White = state_db[0].index('H7Z003') #These codes are from the original table used to make the new ones
    indPOP_NonLatino = state_db[0].index('H7Z002')
    indPOP_Black = state_db[0].index('H7Z004')
    indPOP_Asian = state_db[0].index('H7Z006')
    indPOP_Hispanic = state_db[0].index('H7Z010')
    indNH_White = state_db[0].index('NH_White')
    indNH_Black = state_db[0].index('NH_Black')
    indNH_Asian = state_db[0].index('NH_Asian')
    indHispanic = state_db[0].index('Hispanic')
    indOther = state_db[0].index('Other')
    indTotal = state_db[0].index('Total')
    crop_state_db = [[state_db[0][indGISJOIN],state_db[0][indSTATE],state_db[0][indSTATEA],
                      state_db[0][indCDA],state_db[0][indNH_White],state_db[0][indNH_Black],state_db[0][indNH_Asian]
                      ,state_db[0][indHispanic],state_db[0][indOther],state_db[0][indTotal]]]
    for line in range(2, len(state_db)):
        tmp = []
        state_db[line].extend([0,0,0,0,0,0])
        state_db[line][indPOP] = int(state_db[line][indPOP])
        state_db[line][indPOP_NonLatino] = int(state_db[line][indPOP_NonLatino])
        state_db[line][indNH_White] = int(state_db[line][indPOP_White])
        state_db[line][indNH_Black] = int(state_db[line][indPOP_Black]) 
        state_db[line][indNH_Asian] = int(state_db[line][indPOP_Asian]) 
        state_db[line][indHispanic] = int(state_db[line][indPOP_Hispanic]) 
        state_db[line][indOther] = int(state_db[line][indPOP_NonLatino]) - int(state_db[line][indPOP_White]) - int(state_db[line][indPOP_Black]) - int(state_db[line][indPOP_Asian])
        state_db[line][indTotal] = int(state_db[line][indPOP])
        tmp = [state_db[line][indGISJOIN],state_db[line][indSTATE],state_db[line][indSTATEA],
                      state_db[line][indCDA],state_db[line][indNH_White],state_db[line][indNH_Black],state_db[line][indNH_Asian]
                      ,state_db[line][indHispanic],state_db[line][indOther],state_db[line][indTotal]]
        crop_state_db.append(tmp)
    return crop_state_db

def Make_CSV_Out(crop_state_db):
    """
    Take crop_state_db as input and create a csv file with the relevant data
    """
    IndState_Code = crop_state_db[0].index('STATEA')
    state_code = crop_state_db[1][IndState_Code]
    name = '%s/cropped_state_%s.csv' % (filepath, state_code)
    fou = open(name, 'w')
    datawriter = csv.writer(fou, dialect='excel')
    for row in crop_state_db:
        datawriter.writerow(row)
    fou.close()
    

#execute previous code
filepath = '/Users/frankkanayet/Documents/Research/Personal/Maps'
os.chdir(filepath)
sys.path.append(filepath)
#state = ['1', '15', '32']
#state = ['12', '17', '36', '39', '42', '48', '4', '5', '8',
#          '9', '13', '16', '18', '19', '20', '21', '22', '23', '24',
#         '25', '26', '27', '28', '29', '31', '33', '34', '35', '37', '40']
#state = ['41', '45', '47', '49', '51', '53', '54', '55']
state = ['44']
state_dict = {'1':'AL','2':'AK','4':'AZ','5':'AR','6':'CA','8':'CO','9':'CT','10':'DE',
              '11':'DC','12':'FL','13':'GA','15':'HI','16':'ID','17':'IL','18':'IN',
              '19':'IA','20':'KS','21':'KY','22':'LA','23':'ME','24':'MD','25':'MA',
              '26':'MI','27':'MN','28':'MS','29':'MO','30':'MT','31':'NE','32':'NV',
              '33':'NH','34':'NJ','35':'NM','36':'NY','37':'NC','38':'ND','39':'OH',
              '40':'OK','41':'OR','42':'PA','44':'RI','45':'SC','46':'SD','47':'TN',
              '48':'TX','49':'UT','50':'VT','51':'VA','53':'WA','54':'WV','55':'WI',
              '56':'WY'}
# This is the file of the table with the racial data for a single state.
# Later this will be a list of files one foe each state
for st in state:
    print 'state:', st
    infile = 'nhgis0005_csv/nhgis0005_ds172_2010_block_'+st+'.csv'
    state_db = LoadFile(infile)
    crop_state_db = Extract_Racial_Data(state_db)
    Make_CSV_Out(crop_state_db)
    IndState_Code = crop_state_db[0].index('STATEA')
    state_code = crop_state_db[1][IndState_Code] # this will be generalized when there is a list of states
    crop_file = '%s/cropped_state_%s.csv' % (filepath, state_code)
    ## Make dictionary of indexes to maerge GISfile to population file
    fin = open(crop_file, 'U')
    line_reader = csv.reader(fin)
    counter = 0
    GIStoIndex = {}
    IndexToGIS = {}
    for row in line_reader:
        if not (row[0] in GIStoIndex):
            GIStoIndex[row[0]] = counter
            IndexToGIS[counter] = row[0]
        counter += 1
    fin.close()            
    ### In the file names _440_ corresponds to state number (in this case 44 plus a 0)
    state_name = state_dict[st]
    ds = ogr.Open('nhgis0005_shapefile_tl2010_'+st+'0_block_2010/'+state_name+'_block_2010.shp')
    if ds is None:
        print "Open failed.\n"
        sys.exit(1)
    
    lyr = ds.GetLayerByIndex(0)
    
    lyr.ResetReading()
    
    feat_defn = lyr.GetLayerDefn()
    
    field_defns = [feat_defn.GetFieldDefn(i) for i in range(feat_defn.GetFieldCount())]
    
    # The following conditionals need to be changed to the actual value of race once I figure this out
    # So far this is just a sample code of something I need to do to extract the races of people
    
    # this is a test to see if we are getting what we want
    #for i, defn in enumerate(field_defns):
    #    print defn.GetName()
    
    # Obtain the number of features (Census Blocks) in the layer
    n_features = len(lyr)
    n_features
    #example of the info we get
    lyr[0].GetField('GISJOIN') #same code as crop file
    lyr[0].GetField('STATEFP10') #state code
    lyr[0].GetField('ALAND10')  #LAND AREA?
    lyr[0].GetField('AWATER10') #WATER AREA?
    lyr[0].GetField('INTPTLAT10') #LATITUDE?
    lyr[0].GetField('INTPTLON10') #LONGITUDE?
    lyr[0].GetField('Shape_area')
    lyr[0].GetField('Shape_len')
    
    
    pop_dat = pd.read_csv(crop_file)
    #xlon,xlat and mx,my are not necessarily the same point but are central points inside the block
    x_y_dataFields = ['GISJOIN', 'State', 'ConDis', 'mx', 'my']
    x_y_data = []
    x_y_data.append(x_y_dataFields)
    # Iterate through every feature (Census Block Ploygon) in the layer,
        # obtain the population counts, and create a point for each block in various coordinates
    
    for j, feat in enumerate( lyr ):
        # Print a progress read-out for every 1000 features and export to hard disk  
        if j % 1000 == 0:
            #conn.commit()
            print "%s/%s (%0.2f%%)"%(j+1,n_features,100*((j+1)/float(n_features)))
            # Obtain total population, racial counts, and state fips code of the individual census block
        GISJOIN = feat.GetField('GISJOIN')
        LON = feat.GetField('INTPTLON10')
        LAT = feat.GetField('INTPTLAT10')
        pop_Index = GIStoIndex[GISJOIN] - 1
        pop = pop_dat['Total'][pop_Index]
        #print GISJOIN, pop
    #        white = pop_dat['NH_White'][pop_Index]
    #        black = pop_dat['NH_Black'][pop_Index]
    #        asian = pop_dat['NH_Asian'][pop_Index]
    #        hispanic = pop_dat['Hispanic'][pop_Index]
    #        other = pop_dat['Other'][pop_Index]
        statefips = pop_dat['STATEA'][pop_Index]
        Con_Dis = pop_dat['CDA'][pop_Index]
        #print GISJOIN, pop, statefips
        # Obtain the OGR polygon object from the feature
        geom = feat.GetGeometryRef()
        if geom is None:
            continue
        # Convert the OGR Polygon into a Shapely Polygon
        poly = loads(geom.ExportToWkb())
        if poly is None:
            continue  
        # Obtain the "boundary box" of extreme points of the polygon
        bbox = poly.bounds
        if not bbox:
            continue
        leftmost,bottommost,rightmost,topmost = bbox
        for i in range(pop):
            # Choose a random x,y within the boundary box
            # and within the orginial ploygon of the census block
            tmp = []        
            while True:            
                samplepoint = Point(uniform(leftmost, rightmost),uniform(bottommost, topmost))            
                if samplepoint is None:
                    break        
                if poly.contains(samplepoint):
                    break
            mx, my = samplepoint.x, samplepoint.y
            tmp = [GISJOIN, statefips, Con_Dis, mx, my]
            x_y_data.append(tmp)
    del pop_dat
    
    
    name = '%s/x_y_state_%s_NAD83_FULL.csv' % (filepath, st)
    fou = open(name, 'w')
    datawriter = csv.writer(fou, dialect='excel')
    for row in x_y_data:
        datawriter.writerow(row)
    fou.close()
    


    