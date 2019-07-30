#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 11:26:44 2018

@author: mali
"""
import pickle
import neo
import comn_conversion as cnvrt 

#file to read
fldr  = 'rslts/icub64x64/'
fle  = 'L_rf_2f3.pickle'  
pth = cnvrt.read_flenfldr_ncrntpth(fldr, fle)

#if you have the path directly
#pth = '/home/mali/thesis/spiNNaker/tst_bnchmrk/rslts/tst4orn_krnl3_dft500_tres0/rslts_L_rtna.pickle'


with open(pth , 'rb') as pkl:
    data = pickle.load(pkl)
    print '## data:: spks_pth is loaded ! : \n {}'.format( pth)
#    print data.segments[0].spiketrains
spks= data.segments[0].spiketrains
#print spks
print len(spks)
i=0
for spk in range( len(spks) ):
    if spks[spk] !=[]:
        print ' ha'
    else:
        i=i+1
        
print i

#print '\n### spks: \n{}'.format(data.segments[0].spiketrains  )
#for i in range(len(data)/3, 2*len(data)/3):
#    print ' {}   :{}'.format(i,  data[i]  )
#print '\n### spks: \n{}'.format(data)

   