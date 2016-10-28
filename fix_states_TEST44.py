import pandas as pd
import numpy as np
from scipy.spatial import distance as dist

#Change filepath to appropriate path in server
#filepath = '/Users/frankanayet/Documents/Research/Personal/Maps/'
filepath = '/Users/frankanayet/Desktop/Maps/'

state_dict = {'1':'AL','2':'AK','4':'AZ','5':'AR','6':'CA','8':'CO','9':'CT','10':'DE',
              '11':'DC','12':'FL','13':'GA','15':'HI','16':'ID','17':'IL','18':'IN',
              '19':'IA','20':'KS','21':'KY','22':'LA','23':'ME','24':'MD','25':'MA',
              '26':'MI','27':'MN','28':'MS','29':'MO','30':'MT','31':'NE','32':'NV',
              '33':'NH','34':'NJ','35':'NM','36':'NY','37':'NC','38':'ND','39':'OH',
              '40':'OK','41':'OR','42':'PA','44':'RI','45':'SC','46':'SD','47':'TN',
              '48':'TX','49':'UT','50':'VT','51':'VA','53':'WA','54':'WV','55':'WI',
              '56':'WY'}

# states = ['1','4','5','6','8','9',
#               '12','13','15','16','17','18',
#               '19','20','21','22','23','24','25',
#               '26','27','28','29','31','32',
#               '33','34','35','36','37','39',
#               '40','41','42','44','45','47',
#               '48','49','51','53','54','55']

states = ['44']

for st in states:
	print st
	#Make sure files are in the same filepath
	clus = pd.read_csv(filepath+'Clustered_'+st+'.csv')
	xy = pd.read_csv(filepath+'x_y_state_'+st+'_NAD83_FULL.csv')
	print 1
	merged = pd.merge(xy,clus[['ConDis','Labels']],how='outer',left_index=True,right_index=True,suffixes=('_xy','_clus'))
	del clus
	del xy
	print 2
	merged = merged.rename(columns={'ConDis_xy':'ConDis'})
	print 3
	group_mx = merged[['GISJOIN','mx','my']].groupby('GISJOIN').mean()
	group_labels = merged[['GISJOIN','State','ConDis','ConDis_clus','Labels']].groupby('GISJOIN').agg(lambda x:x.value_counts().index[0])
	grouped = pd.concat([group_mx, group_labels], axis=1)
	del group_labels
	del group_mx
	print 4
	#grouped.Labels = grouped.Labels.round()
	print 5
	xxy = pd.read_csv('xx_y_state_'+st+'_NAD83_FULL.csv')
	print 6
	xxy_grouped = xxy.groupby('GISJOIN').mean()
	print 7
	del xxy
	print 8
	grouped = pd.concat([grouped,xxy_grouped])
	print 9
	#new_grouped = grouped.groupby(level=0).mean()
	print 10
	centroids = grouped[['Labels','mx','my']].groupby('Labels').mean()
	print 11
	to_label = grouped.loc[np.isnan(grouped['Labels']), ['mx','my','Labels']]
	print 12
	res = dist.cdist(centroids,to_label[['mx','my']])
	print 13
	to_label['Labels'] = res.argmin(0)
	print 14
	grouped.loc[np.isnan(grouped['Labels']),'Labels'] = to_label.Labels
	print 15
	grouped.ConDis = grouped.ConDis - 1
	print 16
	grouped.sort_values('ConDis',inplace=True) #Can be sorted by 'Labels' or 'ConDis'
	print 17
	outname = 'Cluster_'+st+'.csv'
	print 18
	grouped.to_csv(outname)



