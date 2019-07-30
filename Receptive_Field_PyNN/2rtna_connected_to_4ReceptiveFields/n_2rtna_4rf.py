#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  3 17:28:21 2018

@author: mali
"""

import time 
import os
import logging
import numpy as np
import pickle
#import spynnaker8 as sim 
#import pyNN.spiNNaker as sim


import pyNN.neuron as sim 
from pyNN.space import Grid2D
import pyNN.utility.plotting as plot
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import print_chs as prnt
import manch_gaussian as manch
import comn_conversion as cnvrt
import n_rtna_cls as RTNA
import n_rf_cls as RF


# sim setup
step_tm = 0.01
sim.setup(timestep = step_tm, min_delay=0.1, max_delay=1.0)
#sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 120)
print '\n############################################ sim param:'
print '## get_time_step:  {}'.format ( sim.get_time_step() )
print '## get_min_delay:  {}'.format ( sim.get_min_delay() )
print '## get_max_delay:  {}'.format ( sim.get_max_delay() )



# load spikes times from pickle file 
print '\n###### loading the spike_times.pickle file as list of list of list .... '
#file to read
spks_fldr  = 'pkl_spk_tms/icub64x64_nsy/'
L_spk_fle  = 'icub64x64_12-8-45_rght_rght.pickle' 
R_spk_fle  = 'icub64x64_12-8-45_lft_lft.pickle'

L_spks_pth = cnvrt.read_flenfldr_ncrntpth(spks_fldr, L_spk_fle)
R_spks_pth = cnvrt.read_flenfldr_ncrntpth(spks_fldr, R_spk_fle)

# store rslts
rslts_fldr =  'rslts/icub64x64_nsy/'

# instaniate rtna
L_rtna = RTNA.create_rtna( L_spks_pth , wdth_ =64, hght_=64, label_='L_rtna')
R_rtna = RTNA.create_rtna( R_spks_pth , wdth_ =64, hght_=64, label_='R_rtna')

n_orn=4
lif_param = {'cm': 0.2,           'i_offset': 0.0,      'tau_m': 1.1, 
                'tau_refrac': 0.1,    'tau_syn_E': 0.01,    'tau_syn_I': 01.01,
                'v_reset': -65.0,     'v_rest': -65.0,      'v_thresh': -63.0
                   }

# instantiate L_rf and R_rf
L_rf = RF.create_rf( L_rtna, krnl_sz_=5, n_orn_=n_orn, lif_param_=lif_param, label_='L_rf' )
R_rf = RF.create_rf( R_rtna, krnl_sz_=5, n_orn_=n_orn, lif_param_=lif_param, label_='R_rf' )


#chs
L_rtna.prnt_chs()
R_rtna.prnt_chs()
L_rtna.record_data()
R_rtna.record_data()


rf_scan_jmp=1
synpse_dly=0.01
synpse_gain= 35
for orn in range( n_orn):
    L_rf[orn].prnt_chs()
    L_rf[orn].record_data()
    R_rf[orn].prnt_chs()
    R_rf[orn].record_data()

    L_rf[orn].create_gb_wghts()
    R_rf[orn].create_gb_wghts()


    L_rf[orn].conect2rtna_gb_fltr (rf_scan_jmp, synpse_dly, synpse_gain )
#    L_rf[orn].prnt_rtna2rf_proj()
    R_rf[orn].conect2rtna_gb_fltr (rf_scan_jmp, synpse_dly, synpse_gain )
#    R_rf[orn].prnt_rtna2rf_proj()

lif_param = {'cm': 0.05,           'i_offset': 0.0,      'tau_m': 0.06, 
                'tau_refrac': 0.01,    'tau_syn_E': 0.05,    'tau_syn_I': 0.05,
                'v_reset': -65.0,     'v_rest': -65.0,      'v_thresh': -63.0}
lif_param_1 = {'cm': 0.05,           'i_offset': 0.0,      'tau_m': 0.06, 
                'tau_refrac': 0.01,    'tau_syn_E': 0.05,    'tau_syn_I': 0.05,
                'v_reset': -65.0,     'v_rest': -65.0,      'v_thresh': -63.0}

for orn in range( n_orn):
    L_rf[orn].set_lif_param_of_pop( lif_param)
#    L_rf[orn].prnt_crnt_lif_param()
    R_rf[orn].set_lif_param_of_pop( lif_param)
#    R_rf[orn].prnt_crnt_lif_param()




#run simulation ==============================================================
simtime=1.2
sim.run(simtime) # bet run and end ===> write_data and get_data================

for orn in range( n_orn):
    L_rf[orn].prnt_rtna2rf_proj_chs()
    R_rf[orn].prnt_rtna2rf_proj_chs()

# store data
L_rtna.write_data(  cnvrt.write_flenfldr_ncrntpth(rslts_fldr, 'rslts_L_rtna.pickle')  )
R_rtna.write_data(  cnvrt.write_flenfldr_ncrntpth(rslts_fldr, 'rslts_R_rtna.pickle')  )

for orn in range( n_orn):
    L_rf[orn].write_data( rslts_fldr )    
    R_rf[orn].write_data( rslts_fldr )   
     
# get spks, v, stop_tm
L_rtna_spks =  L_rtna.get_spks()
stop_time   =  L_rtna._stop_tm

L_rf_spks =[]
L_rf_v    =[]
for orn in range( n_orn):
    L_rf_spks.append(  L_rf[orn].get_spks()  )
    L_rf_v.append(     L_rf[orn].get_v()     )


sim.end()
#end simulation ==============================================================
for orn in range( n_orn):
    print 'plot {}'.format(L_rf[orn]._pop.label)
    L_rf[orn].plt_spks( L_rtna )
    plt.show()



        
        
        
        
        
        
        
        
        
        
        
        
        
        
