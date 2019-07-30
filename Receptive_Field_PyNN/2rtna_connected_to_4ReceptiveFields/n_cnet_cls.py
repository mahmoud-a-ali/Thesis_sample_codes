#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  3 23:49:20 2018

@author: mali
"""

import time 
import os
import logging
import pickle
#import spynnaker8 as sim 
#import pyNN.spiNNaker as sim
#import pyNN.brian as sim 
#import pyNN.brian as sim 
import pyNN.neuron as sim 


import pyNN.utility.plotting as plot
import matplotlib.pyplot as plt




#from pylab import *
#import seaborn as sns; sns.set()
import print_chs as prnt
import manch_gaussian as manch
import comn_conversion as cnvrt

#logger = logging.getLogger(__file__)
        
class C_NET(object):
    def __init__(self, Lrf_, Rrf_, lif_param_, lyr_n,  label_) :
        if Lrf_._wdth != Rrf_._wdth or Lrf_._hght != Rrf_._hght:
            print '## ERROR:  Lrf_._wdth != Rrf_._wdth or Lrf_._hght != Rrf_._hght'
            return False
        self._Lrf = Lrf_
        self._Rrf = Rrf_
        self._lyr_n = lyr_n
        self._n_rows  = self._Lrf._wdth 
        self._n_cols  = self._Lrf._hght  
        self._min_dsp = -( self._Lrf._wdth - 1 )
        self._max_dsp = ( self._Lrf._wdth - 1 )
        self._min_x = 0
        self._max_x = 2*( self._Lrf._wdth - 1 )
        self._label = label_
        self._pop_sz = self._n_rows * self._n_cols
        self._pop = None
        self._lif_param= lif_param_
        self._out_spks = None
        self._out_v    = None
        self._stop_tm= None
        

        self._2rf_dly = None
        self._2rf_G   = None
        self._2Lrf_connlst = None
        self._2Rrf_connlst = None
        self._2Lrf_proj = None
        self._2Rrf_proj = None

        
        self._L_nrns = None
        self._L_nrns = None
        self._col_nrns = None
        self._row_nrns = None 
        self._x_nrns = None
        self._dsp_nrns = None
        
        print "\n######{} :: Creating pop .... ".format ( self._label)
        self._pop=  sim.Population(self._pop_sz,  sim.IF_curr_exp(**self._lif_param),
                
                                   label=self._label  )       
    # extract related nrns in L and R rf --------------------------------------
    def extract_rltd_rf_nrns(self): #return vector with all nrn idx will connect to that lyr 
        print '### {} :: extracting related_rf_nrns .... '.format(self._label)
        rf_nrns_idx=[] 
        for nrn_idx in range ( self._lyr_n*self._n_rows, self._lyr_n*self._n_rows +self._n_rows ):
            rf_nrns_idx.append( nrn_idx  )
        self._L_nrns = rf_nrns_idx
        self._R_nrns = rf_nrns_idx
        
        
        
    # extract nrn_idx related ith_row in the cnet -----------------------------
    def cnrns_in_ith_row(self): 
        crow_nrns=[] 
        for ith_row in range( self._n_rows ):
            cnrns_in_irow=[]
            for nrn_idx in range ( ith_row*self._n_rows, ith_row*self._n_rows +self._n_rows ):
                cnrns_in_irow.append( nrn_idx  )
            crow_nrns.append( cnrns_in_irow )           
        self._row_nrns=crow_nrns
       
        
    # extract nrn_idx related ith_col in the cnet  ----------------------------
    def cnrns_in_ith_col(self): 
        ccol_nrns=[] 
        for ith_col in range( self._n_cols ):
            cnrns_in_icol=[]
            for nrn in range ( self._n_rows ):
                nrn_idx = nrn*self._n_rows + ith_col
                cnrns_in_icol.append( nrn_idx  )
            ccol_nrns.append( cnrns_in_icol )           
        self._col_nrns= ccol_nrns        
        
    # Create conn_lst to Lrf  ---------------------------------
    def connlst_2Lrf (self, dly_, G_):
        self._2rf_dly = dly_ 
        self._2rf_G= G_ 
        rows_conn_lst=[] 
        for irow in range( self._n_rows ):
            for nrn in range ( self._n_cols ): #n_cols is same as n_nrns per row
                rows_conn_lst.append(   ( self._row_nrns[irow][nrn], self._L_nrns[irow], self._2rf_G, self._2rf_dly )    )
        self._2Lrf_connlst= rows_conn_lst        
        self._2Lrf_proj =   sim.Projection( self._pop, self._Lrf._pop, 
                                      sim.FromListConnector(self._2Lrf_connlst),
                                      #synapse_type=sim.StaticSynapse(weight= W_rtna2rf, delay= dly_rtna_rf),
                                      receptor_type='excitatory', #space=None, source=None,
                                      label='{} --> {}'.format( self._Lrf._label, self._label)    )


    # Create conn_lst to Rrf  ---------------------------------
    def connlst_2Rrf (self, dly_, G_):
        self._2rf_dly = dly_ 
        self._2rf_G= G_
        cols_conn_lst=[] 
        for icol in range( self._n_cols ):
            for nrn in range ( self._n_rows ): #n_rows is same as n_nrns per col
                cols_conn_lst.append(   ( self._col_nrns[icol][nrn], self._R_nrns[icol], self._2rf_G, self._2rf_dly )    )
        self._2Rrf_connlst= cols_conn_lst  
        self._2Rrf_proj =   sim.Projection( self._pop, self._Rrf._pop, 
                                      sim.FromListConnector(self._2Rrf_connlst),
                                      #synapse_type=sim.StaticSynapse(weight= W_rtna2rf, delay= dly_rtna_rf),
                                      receptor_type='excitatory', #space=None, source=None,
                                      label='{} --> {}'.format( self._Rrf._label, self._label )  )

    # extract nrn_idx with x_vlu in the cnet  ---------------------------------
    def cnrns_with_x(self): 
        x_nrns=[] 
        for x_vlu in range( self._min_x, self._max_x+1 ):
            nrns_wth_x_vlu=[]
            for nrn_idx in range ( self._pop_sz ):
                y_row, x_col = cnvrt.frm_nrn_indx_to_2D_grd( nrn_idx, self._n_cols , self._n_rows  )
#                print '## x_vlu: {},  x_col: {},  y_row: {}'.format( x_vlu, x_col, y_row) #discovered that should add one
                if x_col + y_row == x_vlu:
                    nrns_wth_x_vlu.append( nrn_idx  )
            x_nrns.append( nrns_wth_x_vlu )           
        self._x_nrns= x_nrns  
        
        
    # extract nrn_idx with dsp_vlu in the cnet  ---------------------------------
    def cnrns_with_dsp(self): 
        dsp_nrns=[] 
        for dsp_vlu in range( 0, self._max_dsp+1 ):
            nrns_wth_dsp_vlu=[]
            for nrn_idx in range ( self._pop_sz ):
                y_row, x_col = cnvrt.frm_nrn_indx_to_2D_grd( nrn_idx, self._n_cols , self._n_rows  )
#                print '## dsp_vlu: {},  x_col: {},  y_row: {}'.format( dsp_vlu, x_col, y_row) #discovered that should add one
                if x_col - y_row == dsp_vlu:
                    print  nrn_idx, x_col - y_row , dsp_vlu
                    nrns_wth_dsp_vlu.append( nrn_idx  )
            dsp_nrns.append( nrns_wth_dsp_vlu )  
        for dsp_vlu in range( self._min_dsp, 0 ):
            nrns_wth_dsp_vlu=[]
            for nrn_idx in range ( self._pop_sz ):
                y_row, x_col = cnvrt.frm_nrn_indx_to_2D_grd( nrn_idx, self._n_cols , self._n_rows  )
#                print '## dsp_vlu: {},  x_col: {},  y_row: {}'.format( dsp_vlu, x_col, y_row) #discovered that should add one
                if x_col - y_row == dsp_vlu:
                    print  nrn_idx, x_col - y_row , dsp_vlu
                    nrns_wth_dsp_vlu.append( nrn_idx  )
            dsp_nrns.append( nrns_wth_dsp_vlu ) 
        self._dsp_nrns= dsp_nrns          

               
    # print some characteristics-----------------------------------------------
    def prnt_chs(self):
        print '\n###### general ch\'s of {}  =================================='.format(self._label)
        print 'label                 :   {}'.format(self._label)
        print 'wdth                  :   {}'.format(self._n_cols)
        print 'hght                  :   {}'.format(self._n_rows)
        print 'n_of_pop              :   {}'.format( len(self._pop) )
        print 'min_dsp               :   {}'.format( self._min_dsp )
        print 'max_dsp               :   {}'.format( self._max_dsp )
        print 'min_x                 :   {}'.format( self._min_x  ) 
        print 'max_x                 :   {}'.format( self._max_x   ) 
        
        print 'lif_param             :   {}'.format(self._lif_param)
        print 'stop_tm               :   {}'.format( self._stop_tm )
        print 'out_spks              :   {}'.format( self._out_spks)
        print 'related L-nrns        :   {}'.format( self._L_nrns )
        print 'related R-nrns        :   {}'.format( self._R_nrns )
        print 'self._row_nrns        :   {}'.format( self._row_nrns )
        print 'self._col_nrns        :   {}'.format( self._col_nrns )
        print 'self._dsp_nrns        :   {}'.format( self._dsp_nrns )
        print 'self._x_nrns          :   {}'.format( self._x_nrns )
        print 'self._2Lrf_proj       :   {}'.format( self._2Lrf_proj )
        print 'self._2Rrf_proj       :   {}'.format( self._2Rrf_proj )        
        
        print 'self._2Lrf_connlst    :   {}'.format( self._2Lrf_connlst )
        print 'self._2Rrf_connlst    :   {}'.format( self._2Rrf_connlst )

        
        print '----------------------------------------------------------------'
        print '#### ch\' of {}       :'.format(self._label)
        #print 'positions            :   {}'.format(L_rtna._positions)
        print 'label                 :   {}'.format(self._pop.label)
        print 'size = n_nrns         :   {}'.format(self._pop.size)
#        print 'local_size           :   {}'.format(self._pop.local_size)
        print 'structure             :   {}'.format(self._pop.structure)
#        print 'length               :   {}'.format(len(self._pop))
#        print 'length__             :   {}'.format(self._pop.__len__())
        print 'first_id              :   {}'.format(self._pop.first_id) 
        print 'last_id               :   {}'.format(self._pop.last_id)
        print 'index of first id     :   {}'.format(self._pop.id_to_index(self._pop.first_id))
#        print 'all_ids              :  {} '.format(self._pop._all_ids)
        print '================================================================'
    
    
    # print proj chs of each pop of the rf ------------------------------------
    def prnt_proj_chs(self):
        """   should call after  after sim.run like all commands has xxx.get() """
#        print inhb_proj[0].receptor_type
        print '\n========================== cnet_lyr_{}_proj ch\'s ================================'.format(self._lyr_n)
        print '#### _2Lrf_proj                :\n{}'.format(self._2Lrf_proj)  
        print '#### _2Lrf_proj_delay_array          :\n{}'.format(self._2Lrf_proj.get('delay', format='array')  )
        print '##### _2Lrf_proj_weights_array        :\n{}'.format(self._2Lrf_proj.get('weight', format='array') )
        print'-------------------------------------------------------------------------------------'
        print '#### _2Lrf_proj                :\n{}'.format(self._2Rrf_proj)  
        print '#### _2Lrf_proj_delay_array          :\n{}'.format(self._2Rrf_proj.get('delay', format='array')  )
        print '##### _2Lrf_proj_weights_array        :\n{}'.format(self._2Rrf_proj.get('weight', format='array') )
        print '====================================================================================='    
           
        
        
        
        
# wrapper to create cnet ========================================================
def create_cnet_lyr(Lrf_, Rrf_, lif_param_, dly2rf, G2rf, label_='cnet'):
    cnet = []
    n_lyrs = Lrf_._hght
    print "####### \n{} :: Creating cnet with n_lyrs= {} .... \n".format ( label_, n_lyrs )
    for lyr in range( n_lyrs ):
        label = '{}_lyr_{}'.format(label_, lyr)
        cnet_lyr =  C_NET(Lrf_, Rrf_, lif_param_, lyr, label)
        
        cnet_lyr.extract_rltd_rf_nrns( )
        cnet_lyr.cnrns_in_ith_row( )
        cnet_lyr.cnrns_in_ith_col( )
        cnet_lyr.connlst_2Lrf( dly2rf, G2rf)
        cnet_lyr.connlst_2Rrf( dly2rf, G2rf)
        cnet_lyr.cnrns_with_x()
        cnet_lyr.cnrns_with_dsp()
        
        
        
        cnet.append(  cnet_lyr  )
        
    return cnet
#==============================================================================

#
#       
#        
#    #create gb_wghts ----------------------------------------------------------   
##    def create_gb_wghts(self):
##        """ should called before sim.run, create gb_wghts"""
##        print "\n###### Creating gb Fltr wghts: scale=%d, n_orn=%d, sz=%f" % (self._gb_scls, self._orn_idx, self._gb_sz )
##        self._gb_wghts = manch.GaborConnectorList( self._gb_scls, self._orn_idx, self._gb_sz) 
##        return self._gb_wghts    
#    def create_gb_wghts(self):
#        """ should called before sim.run, create gb_wghts"""
#        print "\n###### Creating gb Fltr wghts: scale=%d, n_orn=%d\%d, sz=%f" % (self._gb_scls, self._orn_idx, 4, self._gb_sz )
#        self._gb_wghts = manch.GaborConnectorList( self._gb_scls, 4, self._gb_sz)  ###self._orn_idx
#        return self._gb_wghts
#    
#    
#    
#    # print gb_wghts ----------------------------------------------------------
#    def prnt_gb_wghts(self):
#        prnt.prnt_gb_wghts(self._gb_wghts)
#        
#    def drw_gb_wghts(self):
#            prnt.draw_gb_wghts(self._gb_wghts, self._orn_idx)    
#        
#    
#    #create connlst using gb_wghts --------------------------------------------    
#    def conect2rtna_gb_fltr(self, rf_scan_jmp_ , synpse_dly_ , synpse_gain_  ): 
#        self._gb_connlst_jmp = rf_scan_jmp_
#        self._gb_connlst_dly = synpse_dly_
#        self._gb_connlst_G   = synpse_gain_ 
#        print '\n###### For each orn_idx:  Create gb_conn_lst (jmp=%d,  dly_rtna_rf=%d,  gain=%d)' % (self._gb_connlst_jmp, self._gb_connlst_dly, self._gb_connlst_G )
#        self._gb_connlst = manch.Filter2DConnector(self._rtna._wdth,       self._rtna._hght,         self._wdth,   self._hght,
#                                                       self._gb_wghts[ self._orn_idx ],    self._krnl_sz,         self._krnl_sz,
#                                                       self._gb_connlst_jmp,     self._gb_connlst_dly,   self._gb_connlst_G)
#        n_conn = len(self._gb_connlst)
##            prnt.prnt_conn_lst(self._gb_connlst, n_conn)
#        print '\n### conn_lst per {}: conn by conn '.format(self._label)
#        conn_lst_by_nrn_idx = cnvrt.grid2D_conn_lst_to_1D (self._gb_connlst, self._rtna._wdth, self._wdth) # (conn_lst, pre_n_rows , post_n_rows )
##            print conn_lst_by_nrn_idx
##            prnt.prnt_conn_lst(conn_lst_by_nrn_idx, n_conn)
#        self._proj =   sim.Projection( self._rtna._pop, self._pop, 
#                                             sim.FromListConnector(conn_lst_by_nrn_idx),
##                                             synapse_type=sim.StaticSynapse(weight= W_rtna2rf, delay= dly_rtna_rf),
#                                             receptor_type='excitatory', #space=None, source=None,
#                                             label='{} --> {}'.format(self._rtna._label, self._pop.label)  )    
#            
#            
#            
#    # set lif_param for a pop -------------------------------------------------
#    def set_lif_param_of_pop(self, lif_param_):
#        print '############ before, set:'
#        print  self._lif_param
#
#        self._pop.set(         cm = lif_param_['cm']          )
#        self._pop.set(      tau_m = lif_param_['tau_m']       )
#        self._pop.set( tau_refrac = lif_param_['tau_refrac']  )
#        self._pop.set(  tau_syn_E = lif_param_['tau_syn_E']   )
#        self._pop.set(  tau_syn_I = lif_param_['tau_syn_I']   )
#        self._pop.set(     v_rest = lif_param_['v_rest']      )
#        self._pop.set(    v_reset = lif_param_['v_reset']     )
#        self._pop.set(   v_thresh = lif_param_['v_thresh']    )
#        self._pop.set(   i_offset = lif_param_['i_offset']    )
#        print '############ afer, set'
#        self.prnt_crnt_lif_param()
#
#         
#    
#    # get current values  of lif_para--==--------------------------------------
#    def get_crnt_lif_param(self):
#        param ={}
#        for key in self._lif_param:
#            param[key]= self._pop.get(key)#[0]
#        self._lif_param = param
#        return self._lif_param
#         
#    
#    # print current values  of lif_para----------------------------------------
#    def prnt_crnt_lif_param(self):
#            self.get_crnt_lif_param()
#            print '### {}._lif_param : \n{}'.format( self._pop.label, self._lif_param  )
#  
#
#
#    # recording data-----------------------------------------------------------
#    def record_data(self):        
#        """ called befor sim.run"""
#        print '\n### {}:: recording data for all pop .... '.format(self._label)       
#        self._pop.record(["spikes","v"]) 
#    
#    
#    # write data to pickle file-----------------------------------------------
#    def write_data(self, rslts_fldr_ ):
#       """ should be called after sim.run otherwise it will write empty file"""
#       print '\n### {}::writing pop data to a file.pickle .... '.format(self._pop.label)
#       rslt_fle =  cnvrt.write_flenfldr_ncrntpth(  rslts_fldr_, '{}.pickle'.format(self._label) ) 
#       self._pop.write_data( rslt_fle  )
#       print '\n### {}:: data stored in file : \n{}'.format(self._pop.label, rslt_fle )
#
#
#
#    # get recorded data -------------------------------------------------------
#    def get_data(self):
#        """  should be called bet run and end, after calling you can axis attributes:
#            self._out_spks,  self._out_v,  and self._stop_tm -- it does not return,
#            its called by other methods get_spks and get_v"""
#        print '\n### {}:: get_data for all pop,  now (_out_spks, _out_v, _stop_tm) have values '.format(self._label )
#        rf_neo  =  self._pop.get_data(variables=["spikes", "v"])  
#        self._out_spks=  rf_neo.segments[0].spiketrains 
#        self._out_v= rf_neo.segments[0].filter(name="v")[0]   # simulation [:] otherwise[0]
#        self._stop_tm = float( self._out_spks[0].t_stop)
#        
#
#
#    # get recorded spks -------------------------------------------------------
#    def get_spks(self):
#        """  should be called bet run and end, after calling you can axis attributes:
#            self._out_spks and self._stop_tm -- it mainly rturns recorded spks,"""
#        self.get_data()
#        return self._out_spks
#
#    # get recorded voltage-----------------------------------------------------
#    def get_v(self):
#        """  should be called bet run and end, after calling you can axis attributes:
#            self._out_spks and self._stop_tm -- it mainly rturns recorded spks,"""
#        self.get_data()
#        return self._out_v
#
#
#    #plt_spks after sim--------------------------------------------------------
#    def plt_spks( self, in_rtna):
#        """ plot recorded spks of rtna, should called after calling self.get_data() methods, so 
#           self._out_spks, self._out_spks, and self._stop_tm can be accessable"""
#        param =self.get_crnt_lif_param()   
##        print param[orn] 
#        
##        ttl = '{}-{}, gb_orn= {} g={}, d={}, cm={}, i_offset={}, \ntau_m={}, tau_refrac={}, tau_syn_E={},tau_syn_I={},\nv_reset={}, v_rest={}, v_thresh={}'.format(
##            name, orn, self._gb_connlst_G, self._gb_connlst_dly,
##            param[orn]['cm'], param[orn]['i_offset'], param[orn]['tau_m'], param[orn]['tau_refrac'], 
##            param[orn]['tau_syn_E'], param[orn]['tau_syn_E'], param[orn]['v_reset'], 
##            param[orn]['v_rest'],param[orn]['v_thresh']  )
#
#        
#        
#        print '\n### {}:: plot in_rtna_out_spks, rf_pop_v, and rf_pop_spks .... '.format(self._pop.label )
#        plot.Figure(
#        plot.Panel(in_rtna._out_spks, yticks=True, xlim=(0, self._stop_tm)), 
#        plot.Panel( self._out_v, yticks=True, xticks=True, xlim=(0, self._stop_tm) ), 
#        plot.Panel(self._out_spks,     yticks=True, xticks=True, markersize=5, xlim=(0, self._stop_tm)),
#        title= "{}, \n {}".format(self._label, param)
#        )
#    
#    
#    # print some characteristics-----------------------------------------------
#    def prnt_chs(self):
#        print '\n###### general ch\'s of {}  =================================='.format(self._label)
#        print 'label                 :        {}'.format(self._label)
#        print 'wdth                  :        {}'.format(self._wdth)
#        print 'hght                  :        {}'.format(self._hght)
#        print 'krnl_sz               :        {}'.format(self._krnl_sz)
##        print 'n_orn                 :        {}'.format(self._n_orn)
#        print 'n_of_pop           :        {}'.format( len(self._pop) )
#        print 'lif_param             :  {}'.format(self._lif_param)
#        print 'stop_tm               :   {}'.format( self._stop_tm )
#        print 'out_spks              :   {}'.format( self._out_spks)
#        print '----------------------------------------------------------------'
#        print '#### ch\' of {}       :'.format(self._label)
#        #print 'positions            :        {}'.format(L_rtna._positions)
#        print 'label                 :        {}'.format(self._pop.label)
#        print 'size = n_nrns         :        {}'.format(self._pop.size)
##        print 'local_size           :        {}'.format(self._pop.local_size)
#        print 'structure             :        {}'.format(self._pop.structure)
##        print 'length               :        {}'.format(len(self._pop))
##        print 'length__             :        {}'.format(self._pop.__len__())
#        print 'first_id              :        {}'.format(self._pop.first_id) 
#        print 'last_id               :        {}'.format(self._pop.last_id)
#        print 'index of first id     :        {}'.format(self._pop.id_to_index(self._pop.first_id))
##        print 'all_ids               :        {} '.format(self._pop._all_ids)
#        print '================================================================'
#    
#    
#    
#    
#    
#    # print proj label for each pop of the rf ---------------------------------
#    def prnt_rtna2rf_proj(self):
#        print '\n######  rtna2rf_proj \'{}\' : \n {}'.format( self._label, self._proj)
#    
#    
#    
#    # print proj chs of each pop of the rf ------------------------------------
#    def prnt_rtna2rf_proj_chs(self):
#        """   should call after  after sim.run like all commands has xxx.get() """
##        print inhb_proj[0].receptor_type
#        print '\n========================== rtna_ot_{}_proj ch\'s ================================'.format(self._label)
#        print '#### label                :\n{}'.format(self._proj)  
#        print '#### delay_array          :\n{}'.format(self._proj.get('delay', format='array')  )
##            print '#### delay_list           :\n{}'.format(self._proj[orn].get('delay', format='list')  )
#        print '##### weights_array        :\n{}'.format(self._proj.get('weight', format='array') )
##            print '#### getSynapseDynamics   :\n{}'.format(self._proj[orn].getSynapseDynamics )
##            print '#### __dict__             :\n{}'.format(self._proj[orn].__dict__) 
##            print '#### _synapse_information :\n{}'.format(self._proj[orn]._synapse_information)
##            print '#### size                 :\n{}'.format(self._proj[orn].size)
##        weights, delays = inhib_proj[0].get(["weight", "delay"], format="array")
#        print '====================================================================================='
#
#
#
## wrapper to create rf ========================================================
#def create_rf(rtna_, krnl_sz_=9, n_orn_=8, lif_param_=[], label_='rf'):
#    rf_vect = []
#    for orn_idx_ in range( n_orn_ ):
#        label = '{}_{}f{}'.format(label_, orn_idx_, n_orn_-1)
#        rf_vect.append( rcptv_fld(rtna_, krnl_sz_, orn_idx_ , lif_param_ , label) )
#    return rf_vect
##==============================================================================
#




## fltr krnl specs
#jump=1  
#dly_rtna_rf= .001  
#gain=50
#scales =1
#gb_sz = 3
#
## rf_pop
#W_rtna2rf=1
#W_inhb_rf2rf = 0
#W_exct_rf2rf = 01
#dly_exct_rf2rf= .01
#dly_inhb_rf2rf= .1
#
#


















