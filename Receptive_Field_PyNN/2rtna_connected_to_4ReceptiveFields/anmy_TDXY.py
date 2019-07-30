#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  2 13:09:55 2018

@author: mali
"""

#import time
import pickle
import pyNN.utility.plotting as plot
import matplotlib.pyplot as plt
import comn_conversion as cnvrt
import prnt_plt_anmy as ppanmy

# file and folder names =======================================================
fldr_name        = 'rslts/icub64x64/'
pickle_filename = 'TDXY.pickle'
file_pth    = cnvrt.read_flenfldr_ncrntpth(fldr_name, pickle_filename )

with open(file_pth , 'rb') as tdxy:
    TDXY    = pickle.load( tdxy )
print '### lenght of TDXY : {}'.format( len(TDXY)  ) # 2+ 2*n_orn )
pop = TDXY[0]
t_ist = 1040
print 'check pop: L_rtna_TDXY'
print '### T  :  {}'.format(pop[0][t_ist]) # dimension 4 x t_stp x depend 
print '### 1D :  {}'.format(pop[1][t_ist]) # dimension 4 x t_stp x depend 
print '### X  :  {}'.format(pop[2][t_ist]) # dimension 4 x t_stp x depend 
print '### Y  :  {}'.format(pop[3][t_ist]) # dimension 4 x t_stp x depend 

print pop[0]
print pop[1]

#required variables============================================================
n_rtna   = 2  # till now should be two 
n_orn    = 4
rtna_w   = 64
rtna_h   = 64
krnl_sz  = 5

rf_w = rtna_w - krnl_sz +1
rf_h = rtna_h - krnl_sz +1

subplt_rws = n_rtna
subplt_cls = n_orn+1

########### to make animation fast as scale now in micro second ###############
#first to scale be divide over 10 or 100 ======================================
T=TDXY[0][0]
t10u=T [0:T[-1]:100]
#print '### t_10u : {}'.format(t10u)

# second find all times has spikes any one of the rtna or rf ==================
t_spks=[]
for pop in range ( len(TDXY) ): 
    for inst in range( len(TDXY[pop][0]) ):
        if TDXY[pop][2][inst]!=[] :
            t_spks.append( TDXY[pop][0][inst] ) 
            print pop, TDXY[pop][0][inst] 
            
t_spks.sort()
for each in t_spks:
    count = t_spks.count(each)
    if count > 1:
        t_spks.remove(each)
print 't_spks : {}'.format( t_spks )




#animate the rtna_rf =========================================================
#print 'abplt_rw, sbplt_cl, rtna_w, rtna_h, rf_w, rf_h: {}, {}, {}, {}, {}, {} '.format(subplt_rws, subplt_cls, rtna_w, rtna_h, rf_w,  rf_h)
fig, axs = plt.subplots(subplt_rws, subplt_cls, sharex=False,  sharey=False)  #, figsize=(12,5))
axs = ppanmy.init_fig_mxn_sbplt_wxh_res (fig, axs, rtna_h, rtna_w, rf_w,  rf_h,  subplt_rws, subplt_cls)
plt.grid(True)
plt.show(block=False)
plt.pause(.01)
#for i in t_spks: #t10u:
#    axs = ppanmy.init_fig_mxn_sbplt_wxh_res (fig, axs, rtna_h, rtna_w, rf_w,  rf_h,  subplt_rws, subplt_cls)
#    plt.suptitle('rtna_rf_orn_3:   t= {} usec'.format( i ) )
#    if subplt_rws==1:  
#        axs[0].scatter( TDXY[0][2][i], TDXY[0][3][i] )          
#        for col in range (subplt_cls):
#            axs[col].scatter( TDXY[col+1][2][i], TDXY[col+1][3][i] )
##        plt.savefig( 'fgrs/anmy_1/{}_t{}.png'.format(vrjn, i)  )
#        plt.show(block=False)
#        plt.pause(2)
#        for col in range(subplt_cls): 
#            axs[col].cla()                
#                                    
#    elif subplt_rws==2:            
#        for col in range (subplt_cls):
#            axs[0][0].scatter( TDXY[0][2][i], TDXY[0][3][i] )
#            axs[1][0].scatter( TDXY[1][2][i], TDXY[1][3][i] )
#            for col in range(1,n_orn+1):
#                row=0
#                axs[row][col].scatter( TDXY[col+1][2][i], TDXY[col+1][3][i] )
#            for col in range(1,n_orn):
#                row=1
#                axs[row][col].scatter( TDXY[n_orn+1+col][2][i], TDXY[n_orn+1+col][3][i] )
##            plt.savefig( 'fgrs/anmy_1/{}_t{}.png'.format(vrjn, i)  )
#            plt.show(block=False)
#            plt.pause(2)
#            for row in range(subplt_rws):
#                for col in range (subplt_cls):
#                    axs[row][col].cla()
#                           



print '##### required variables: \n n_rtna={}, TDXY_len={}, rtna_w={}, rtna_h={}, krnl_sz={}, rf_w={} , rf_h={}'.format( n_rtna , len(TDXY), rtna_w, rtna_h, krnl_sz, rf_w , rf_h  )





plt.show(block=False)
last_t_spks=-310
for i in range( len(t_spks) ): #t10u:
#    plt.pause(2)
    if t_spks[i]-last_t_spks > 300:
        #clear        
        if subplt_rws==2:            
            for row in range(subplt_rws):
                for col in range (subplt_cls):
                    axs[row][col].cla() 
        elif subplt_rws==1: 
            for col in range(subplt_cls): 
                    axs[col].cla()  
        axs = ppanmy.init_fig_mxn_sbplt_wxh_res (fig, axs, rtna_h, rtna_w, rf_w,  rf_h,  subplt_rws, subplt_cls)
        plt.suptitle('rtna_rf_orn:   t= {} usec'.format( t_spks[i] ) )
        plt.pause(1.5)
    #--------------------------------------------------------------------------
        if subplt_rws==1:  
            axs[0].scatter( TDXY[0][2][t_spks[i]], TDXY[0][3][t_spks[i]] )          
            for col in range (subplt_cls):
                axs[col].scatter( TDXY[col+1][2][t_spks[i]], TDXY[col+1][3][t_spks[i]] )
    #        plt.savefig( 'fgrs/anmy_1/{}_t{}.png'.format(vrjn, i)  )                         
        elif subplt_rws==2:            
            for col in range (subplt_cls):
                axs[0][0].scatter( TDXY[0][2][t_spks[i]], TDXY[0][3][t_spks[i]] )
                axs[1][0].scatter( TDXY[1][2][t_spks[i]], TDXY[1][3][t_spks[i]] )
                for col in range(1,n_orn+1):
                    row=0
                    axs[row][col].scatter( TDXY[col+1][2][t_spks[i]], TDXY[col+1][3][t_spks[i]] )
                for col in range(1,n_orn+1):
                    row=1
                    axs[row][col].scatter( TDXY[n_orn+1+col][2][t_spks[i]], TDXY[n_orn+1+col][3][t_spks[i]] )
    #            plt.savefig( 'fgrs/anmy_1/{}_t{}.png'.format(vrjn, i)  )
    #--------------------------------------------------------------------------
        plt.pause(.5)
    else: #====================================================================
    #--------------------------------------------------------------------------
        if subplt_rws==1:  
            axs[0].scatter( TDXY[0][2][t_spks[i]], TDXY[0][3][t_spks[i]] )          
            for col in range (subplt_cls):
                axs[col].scatter( TDXY[col+1][2][t_spks[i]], TDXY[col+1][3][t_spks[i]] )
    #        plt.savefig( 'fgrs/anmy_1/{}_t{}.png'.format(vrjn, i)  )                                      
        elif subplt_rws==2:            
            for col in range (subplt_cls):
                axs[0][0].scatter( TDXY[0][2][t_spks[i]], TDXY[0][3][t_spks[i]] )
                axs[1][0].scatter( TDXY[1][2][t_spks[i]], TDXY[1][3][t_spks[i]] )
                for col in range(1,n_orn+1):
                    row=0
                    axs[row][col].scatter( TDXY[col+1][2][t_spks[i]], TDXY[col+1][3][t_spks[i]] )
                for col in range(1,n_orn+1):
                    row=1
                    axs[row][col].scatter( TDXY[n_orn+1+col][2][t_spks[i]], TDXY[n_orn+1+col][3][t_spks[i]] )
    #            plt.savefig( 'fgrs/anmy_1/{}_t{}.png'.format(vrjn, i)  )
    #--------------------------------------------------------------------------
        plt.pause(.5)

    last_t_spks = t_spks[i]
    

                    
                
                

# suing builtin animation function ===========================================
#strt_tm = TDXY[0][0][0]
#stop_tm = TDXY[0][0][-1]
#print '\n### n_orn x n_rtna : {}x{}'.format(n_orn, n_rtna)
#print '\n### strt_tm - stop_tm : {} - {}'.format(strt_tm, stop_tm)
#ppanmy.anmy_rtna_rf_orn( TDXY, rtna_h, rtna_w, n_rtna, krnl_sz, strt_tm , stop_tm)


















