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
#from pylab import *
import seaborn as sns; sns.set()
import print_chs as prnt
import manch_gaussian as manch
import comn_conversion as cnvrt
import n_rtna_cls as RTNA
import n_rf_cls as RF
#logger = logging.getLogger(__file__)


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
#spks_fldr  = 'pkl_spk_tms/vlnescan/'
#L_spk_fle  = 'vlnescan_rtna9x9_lnelngth3_tshft500_tres0_lft_lft.pickle'  

spks_fldr  = 'pkl_spk_tms/icub64x64/'
L_spk_fle  = 'icub64x64_12-8-45_lft_lft.pickle' 

L_spks_pth = cnvrt.read_flenfldr_ncrntpth(spks_fldr, L_spk_fle)
# file store
rslts_fldr =  'rslts/1_rtna/'



# instaniate rtna
L_rtna = RTNA.create_rtna( L_spks_pth , wdth_ =64, hght_=64, label_='L_rtna')
n_orn=4
lif_param = {'cm': 0.2,           'i_offset': 0.0,      'tau_m': 1.1, 
                'tau_refrac': 0.1,    'tau_syn_E': 0.01,    'tau_syn_I': 01.01,
                'v_reset': -65.0,     'v_rest': -65.0,      'v_thresh': -63.0
                   }

#rff=[]
# instantiate rf
rff = RF.create_rf( L_rtna, krnl_sz_=5, n_orn_=n_orn, lif_param_=lif_param, label_='L_rf' )
#rff.append(rf0)
#rf1 = RF.create_rf( L_rtna, krnl_sz_=3, n_orn_=1, lif_param_=lif_param, label_='L_rf' )
#rff.append(rf1)
#chs
L_rtna.prnt_chs()
L_rtna.record_data()


rf_scan_jmp=1
synpse_dly=0.01
synpse_gain=35
for orn in range( n_orn):
    rff[orn].prnt_chs()
    rff[orn].record_data()

    rff[orn].create_gb_wghts()
    rff[orn].prnt_gb_wghts()
    rff[orn].drw_gb_wghts()

    rff[orn].conect2rtna_gb_fltr (rf_scan_jmp, synpse_dly, synpse_gain )
    rff[orn].prnt_rtna2rf_proj()

#param = L_rf.get_crnt_lif_param( )
#print 'parammmmmmmmmmmmmmmmm :\n{}'.format(param)

lif_param = {'cm': 0.05,           'i_offset': 0.0,      'tau_m': 0.06, 
                'tau_refrac': 0.01,    'tau_syn_E': 0.05,    'tau_syn_I': 0.05,
                'v_reset': -65.0,     'v_rest': -65.0,      'v_thresh': -63.0}
lif_param_1 = {'cm': 0.05,           'i_offset': 0.0,      'tau_m': 0.06, 
                'tau_refrac': 0.01,    'tau_syn_E': 0.05,    'tau_syn_I': 0.05,
                'v_reset': -65.0,     'v_rest': -65.0,      'v_thresh': -63.0}

for orn in range( n_orn):
    rff[orn].set_lif_param_of_pop( lif_param)
    rff[orn].prnt_crnt_lif_param()





#run simulation ==============================================================
simtime=1.2
sim.run(simtime) # bet run and end ===> write_data and get_data================

for orn in range( n_orn):
    rff[orn].prnt_rtna2rf_proj_chs()




# store data
L_rtna.write_data(  cnvrt.write_flenfldr_ncrntpth(rslts_fldr, 'rslts_L_rtna.pickle')  )
for orn in range( n_orn):
    rff[orn].write_data( rslts_fldr )       
     
# get spks, v, stop_tm
L_rtna_spks =  L_rtna.get_spks()
stop_time   =  L_rtna._stop_tm

rff_spks =[]
rff_v    =[]
for orn in range( n_orn):
    rff_spks.append(  rff[orn].get_spks()  )
    rff_v.append(     rff[orn].get_v()     )




sim.end()
#end simulation ==============================================================

        #L_rtna.prnt_chs()
        #L_rtna.plt_spks( )
for orn in range( n_orn):
    print 'plot {}'.format(rff[orn]._pop.label)
    rff[orn].plt_spks( L_rtna )
    plt.show()



#
#    gain = 150
#    W_rtna2rf = 1
#    dly_rtna_rf = .01
#    L_rf_pop[0].set(         cm = .1*(1))
#    L_rf_pop[0].set(      tau_m = .5 *(1))
#    L_rf_pop[0].set( tau_refrac = 0.1*(1))
#    L_rf_pop[0].set(  tau_syn_E = .5*(1))
#    L_rf_pop[0].set(  tau_syn_I = .5*(1))
#    L_rf_pop[0].set(     v_rest = -55 )
#    L_rf_pop[0].set(    v_reset = -55 )
#    L_rf_pop[0].set(   v_thresh = -53 )

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        