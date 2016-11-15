Maps
====
How to get the cluster code to work:

1. login to the server and go to /home/frank/Maps
2. run python Cluster_Equal_Send_ParallelDist_8_2016,py
3. This should work as is and run a clustering run for state '44' that is small.
4. The file that makes that code run can be found in /usr/local/lib/python2.7/dist-packages/sklearn/cluster/Ek_means.py
5. Use fix_states_TEST44.py to combine cluster information with complete census block information
6. Use createElectionDistricts_ver1_15-07-16.py to make a map of the state
