
#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed May 23 01:01:27 2018
@author: mali

# fill rtna nrns_spks row by row
ex: 3by3 rtna
\ x0\ x1\ x2\
--------------   ----
\ 0 \ 1 \ 2 \    y=0    --> row_n_0 or 
..............  .....
\ 3 \ 4 \ 5 \    y=1    --> row_n_1 or y=1
..............  .....
\ 6 \ 7 \ 8 \    y=2    --> row_n_2 or y=2
..............  .....

"""


import pickle
import os
import numpy as np
import comn_conversion as cnvrt

# check desired specs==========================================================
rtna_w = 64
rtna_h = 64


ch_idx = 0
t_idx = 1
pol_idx = 2 
x_idx = 3
y_idx = 4 

#load evts=====================================================================
fldr_name =  'txt_evts/gn_icub_stimulus_64_nsy/'
dataset   =  'icub64x64_12-8-45_rght'

dataset_name = dataset + '.txt'
infle_pth= cnvrt.read_flenfldr_ncrntpth(fldr_name, dataset_name)
print infle_pth
evts = np.loadtxt(infle_pth)


# store pkl file ==============================================================  
def save_spk_fle( spks, cmra):
    pickle_filename = '{}_{}.pickle'.format(dataset, cmra)
    fldr_name =  'pkl_spk_tms/{}_nsy'.format(dataset.split('_')[0])
    outfle_pth    = cnvrt.write_flenfldr_ncrntpth(fldr_name, pickle_filename )
    with open( outfle_pth , 'wb') as handle:
        pickle.dump(spks, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print '\n###### store spike_times as pickle file: \n{}\n'.format(outfle_pth)
    return outfle_pth

# loaded data info  =========================================================== 
n_evts = len(evts)
start_time = evts[0][t_idx]
stop_time = evts[-1][t_idx]
simtime = stop_time - start_time

print '######### dataset is loaded: \n {}'.format(infle_pth)
print '## number of events  :  {}'.format(n_evts)
print '## evt[0]'.format( evts[0])
print '## start time is     :  {}'.format(start_time)
print '## stop time is     :  {}'.format(stop_time)
print '## simtime is     :  {}'.format(simtime)

#print 'data set is {}'.format(evts)
#all(x==myList[0] for x in myList)
#x.count(x[0]) == len(x)

ch_col = evts[:,0]
chnls = np.unique(ch_col)
n_cmras = len(chnls)
camera = None   # to be assigned

if n_cmras==1 and chnls[0]==0:
    print '##',dataset_name,'   :  has only events from left camera (ch=0)'
    camera= 'lft'
    spk_tms =  cnvrt.cnvrt_cmra_evts_to_spk_tms(evts, start_time, simtime,  
                                                       dataset_name, camera, rtna_w, rtna_h,
                                                       ch_idx, t_idx, pol_idx, x_idx, y_idx )
    out_pth = save_spk_fle( spk_tms, camera)
    #..........................................................................
elif n_cmras==1 and chnls[0]==1:
    print '##',dataset_name,'  :  has only events from right camera (ch=1)'
    camera= 'rght'
    spk_tms = cnvrt.cnvrt_cmra_evts_to_spk_tms(evts, start_time, simtime,
                                                       dataset_name, camera, rtna_w, rtna_h,
                                                       ch_idx, t_idx, pol_idx, x_idx, y_idx )
    out_pth = save_spk_fle( spk_tms, camera)
    #..........................................................................
else :
    print '##',dataset_name,'   :  has events from both left and right cameras'
    camera= 'lft'
    lft_evts = evts[ [evts[:,0] == 0 ] ] 
    print '\n## lft_evts: \n{}'.format(lft_evts)
    spk_tms =  cnvrt.cnvrt_cmra_evts_to_spk_tms(lft_evts, start_time, simtime,  
                                                       dataset_name, camera, rtna_w, rtna_h,
                                                       ch_idx, t_idx, pol_idx, x_idx, y_idx )
    out_pth = save_spk_fle( spk_tms, camera)
    #..........................................................................
    camera='rght'
    rght_evts = evts[ [evts[:,0] == 1] ]
    print '\n## rght_evts: \n{}'.format(rght_evts)
    spk_tms = cnvrt.cnvrt.cnvrt_cmra_evts_to_spk_tms(rght_evts, start_time, simtime,  
                                                       dataset_name, camera, rtna_w, rtna_h,
                                                       ch_idx, t_idx, pol_idx, x_idx, y_idx )
    out_pth = save_spk_fle( spk_tms, camera)
    



# load to check ===============================================================
print '\n######### load spk.pickle file to check ...'
# rtnas:
with open(out_pth , 'rb') as spk_pkl:
    spks_t    = pickle.load(spk_pkl)
    print '#### spks : (', out_pth,') is loaded !' 
    print '#### spks : \n{}'.format(spks_t )




















