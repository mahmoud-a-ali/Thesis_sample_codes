#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  2 13:17:02 2018

@author: mali
"""

#import time
import pickle
import pyNN.utility.plotting as plot
import matplotlib.pyplot as plt
import comn_conversion as cnvrt
import prnt_plt_anmy as ppanmy



#=============================== load rslts files ============================================
#file name convention : add the path to the next convention names
        ###  L_rtna_rslt_file      and   R_rtna_rslt_file        for   rtnas 
        ###  L_rf_spks_file[orn]   and   R_rf_spks_file[orn]     for   rfs 
        
        
        
#required variables============================================================
n_rtna   = 2 # till now should be two 
rf_n_orn = 4
rtna_w   = 64
rtna_h   = 64
krnl_sz  = 5

rf_w = rtna_w - krnl_sz +1
rf_h = rtna_h - krnl_sz +1


# file and folder names =======================================================
fldr_name        = 'rslts/icub64x64/' 
L_rtna_rslt_file = 'rslts_L_rtna.pickle'  
R_rtna_rslt_file = 'rslts_R_rtna.pickle'  

L_rf_rslt_file   = []
R_rf_rslt_file   = []
for orn in range(rf_n_orn):
    L_rf_rslt_file.append(  'L_rf_{}f3.pickle'.format(orn)  )
    R_rf_rslt_file.append(  'R_rf_{}f3.pickle'.format(orn)  )
    
# load results    
L_rtna_rslt_fpath = cnvrt.read_flenfldr_ncrntpth( fldr_name, L_rtna_rslt_file )
R_rtna_rslt_fpath = cnvrt.read_flenfldr_ncrntpth( fldr_name, R_rtna_rslt_file )

L_rf_rslt_fpath  = []
R_rf_rslt_fpath  = []
for orn in range(rf_n_orn):
    L_rf_rslt_fpath.append(  cnvrt.read_flenfldr_ncrntpth( fldr_name, L_rf_rslt_file[orn] )   )
    R_rf_rslt_fpath.append(  cnvrt.read_flenfldr_ncrntpth( fldr_name, R_rf_rslt_file[orn] )   )
   
    
    
# load data using pickle and  extract spk_trns & Vm  ======================================================   
print '\n######### load rslts pickle files ...'
# rtnas:
with open(L_rtna_rslt_fpath , 'rb') as L_rtna:
    L_rtna_rslt    = pickle.load(L_rtna)
    ld_L_rtna_spks = L_rtna_rslt.segments[0].spiketrains
    print '#### L_rtna_rslt_file : (', L_rtna_rslt_file,') is loaded !' 
#    print '#### L_rtna_rslt : \n{}'.format(ld_L_rtna_spks )
    
with open(R_rtna_rslt_fpath , 'rb') as R_rtna:
    R_rtna_rslt    = pickle.load(R_rtna)
    ld_R_rtna_spks = R_rtna_rslt.segments[0].spiketrains
    print '#### R_rtna_rslt_file : (', R_rtna_rslt_file,') is loaded !' 
#    print '#### R_rtna_spks : \n{}'.format(ld_R_rtna_spks )
 # rfs:   
ld_L_rf_spks = []
ld_R_rf_spks = []
ld_L_rf_v    = [] 
ld_R_rf_v    = []
for orn in range(rf_n_orn):   #(2, 3):
    print' \n'
    with open(L_rf_rslt_fpath[orn] , 'rb') as L_rf:
        L_rf_rslt = pickle.load(L_rf)
        ld_L_rf_spks.append(  L_rf_rslt.segments[0].spiketrains          )
        ld_L_rf_v.append(     L_rf_rslt.segments[0].filter(name="v")[0]  )
        print '#### L_rf_rslt_file : (', L_rf_rslt_file[orn],') is loaded !' 
#        print '#### L_rf_spks_{} : \n{}'.format( orn,  ld_L_rf_spks[orn]) 
#        print '#### L_rf_v_{} : \n{}'.format( orn,  ld_L_rf_v[orn])
    with open(R_rf_rslt_fpath[orn] , 'rb') as R_rf:
        R_rf_rslt = pickle.load(R_rf)
        ld_R_rf_spks.append(  R_rf_rslt.segments[0].spiketrains          )
        ld_R_rf_v.append(     R_rf_rslt.segments[0].filter(name="v")[0]  )
        print '#### R_rf_rslt_file : (', R_rf_rslt_file[orn],') is loaded !' 
#        print '#### R_rf_spks_{} : \n{}'.format( orn,  ld_R_rf_spks[orn]) 
#        print '#### R_rf_v_{} : \n{}'.format( orn,  ld_R_rf_v[orn])
        
# plot in neo way spk_trns ====================================================
vrjn = 10
#for orn in range(rf_n_orn):
#    ppanmy.plt_rtna_rf_spk_v (ld_L_rtna_spks, ld_L_rf_v[orn], ld_L_rf_spks[orn], orn, vrjn , LR='L')
    

#  convert neo spks to 1D and 2D ==============================================  
##### now we have all results in variable:
        # ld_L_rtna_spks        ld_R_rtna_spks 
        # ld_L_rf_spks[orn]     ld_R_rf_spks[orn]
        # ld_L_rf_v[orn]        ld_R_rf_v[orn]
        
        
print ' # convert spk_trns to TDXY ============================================ '
TDXY = []
#print '### left spks before cnvrt: \n{}'.format(ld_L_rtna_spks)
print '############### converted L_rtna '
TDXY.append( cnvrt.frm_spk_trns_to_1D_2D( ld_L_rtna_spks,  rtna_w, rtna_h ) )
print '############### converted R_rtna '
TDXY.append( cnvrt.frm_spk_trns_to_1D_2D( ld_R_rtna_spks,  rtna_w, rtna_h ) )
for orn in range(rf_n_orn):#range(rf_n_orn):
    print '############### converted L_orn= {} '.format(orn)
    TDXY.append( cnvrt.frm_spk_trns_to_1D_2D( ld_L_rf_spks[orn],  rf_w, rf_h ) )

for orn in range(rf_n_orn):    
    print '############### converted R_orn= {} '.format(orn)    
    TDXY.append( cnvrt.frm_spk_trns_to_1D_2D( ld_R_rf_spks[orn],  rf_w, rf_h ) ) 


print '#### test !!! '    
print '### lenght of TDXY : {}'.format( len(TDXY)  ) # 2+ 2*n_orn )
pop = TDXY[4]
t_ist = 50
print 'check pop: L_rtna_TDXY'
print '### T  :  {}'.format(pop[0][t_ist]) # dimension 4 x t_stp x depend 
print '### 1D :  {}'.format(pop[1][t_ist]) # dimension 4 x t_stp x depend 
print '### X  :  {}'.format(pop[2][t_ist]) # dimension 4 x t_stp x depend 
print '### Y  :  {}'.format(pop[3][t_ist]) # dimension 4 x t_stp x depend 

print '##### required variables: \n n_rtna={}, rf_n_orn={}, rtna_w={}, rtna_h={}, krnl_sz={}, rf_w={} , rf_h={}'.format( n_rtna , rf_n_orn, rtna_w, rtna_h, krnl_sz, rf_w , rf_h  )


# store TDXY as pkl file ======================================================    
pickle_filename = 'TDXY.pickle'
file_pth    = cnvrt.write_flenfldr_ncrntpth(fldr_name, pickle_filename )
print '### file path is: {}'.format(file_pth)
with open( file_pth , 'wb') as handle:
    pickle.dump(TDXY, handle, protocol=pickle.HIGHEST_PROTOCOL)
print '\n###### store TDXY as pickle file: \n{}'.format(file_pth)
print 'done!'
#

