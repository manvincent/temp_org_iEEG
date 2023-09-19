#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 13:18:39 2023

@author: vman
"""

import seaborn as sns
import numpy as np
from skimage import measure
from scipy.stats import percentileofscore
from statsmodels.stats.multitest import fdrcorrection as fdr
import pandas as pd

home_dir = '/media/Data/Projects/iowa_lfp/Analysis/Results'
res_dir = f'{home_dir}/decode_logit_LFP_chans_BN_stats' 

# Specify ROIs of interest
ROIlist = ['Frontal Pole',
            'Frontal Orbital Cortex',
            'Subcallosal Cortex',
            'Anterior Insular Cortex',
            'Posterior Insular Cortex',
            'Cingulate Gyrus',
            'Putamen',
            'Amygdala',
            'Hippocampus',
            'Angular Gyrus',
            'Supramarginal Gyrus']
variables = ['EV','Erisk','Outcome','RPE','riskPE']


def clustChar(clusters, stats, crit):
    """
        Computes cluster characteristics [sum(abs(t-values))] of a clusterised vector or matrix

    """
    clustList = np.unique(clusters[:])
    clustList = clustList[np.nonzero(clustList)]

    clust_sumAcc = np.zeros(len(clustList), dtype=float)
    for clustIdx, clustID in enumerate(clustList):
        clust_timepoints = np.where(clusters == clustID)
        clust_sumAcc[clustIdx] = np.sum(np.abs(stats[clust_timepoints] - crit[clust_timepoints]))
    return clust_sumAcc, clustList

clust_char = np.ones((len(variables), len(ROIlist)), dtype = float) * np.nan
clust_thresh = np.ones((len(variables), len(ROIlist)), dtype = float) * np.nan
var_p = np.ones((len(variables), len(ROIlist)), dtype = float) * np.nan
for v,var in enumerate(variables): 
    for r,ROI in enumerate(ROIlist):
        ROIoutDir = f'{res_dir}/{ROI}'
        
        # Load in null distribution
        H0_maxClust = np.load(f'{res_dir}/{ROI}/{ROI}_clust_{var}_clust_null.npy')
        maxClust_upper_crit = np.load(f'{res_dir}/{ROI}/{ROI}_clust_{var}_clust_thresh.npy')
        clust_thresh[v,r] = maxClust_upper_crit
        # Load in H0_t upper bound 
        H0_upper_crit = np.load(f'{res_dir}/{ROI}/{ROI}_clust_{var}_perm_upbnd.npy')
               
        # Load in t statistics        
        acc = np.load(f'{ROIoutDir}/{ROI}_clust_{var}_acc.npy')
                            
        # Threshold data
        acc_bin = (acc > H0_upper_crit)
        # Determine cluster labels
        acc_clust = measure.label(acc_bin)
        # Extract cluster statistic [sum(abs(t-values))]
        acc_clustChar, clustID = clustChar(acc_clust, acc, H0_upper_crit)
        
        # Get p-value
        null = H0_maxClust
        upbnd = H0_upper_crit
        if len(acc_clustChar) == 0: 
            stat = 0   
        else:
            stat = acc_clustChar.max() 
        p = 1 - percentileofscore(null, stat, nan_policy='omit')/100     
        var_p[v,r] = p 
        clust_char[v,r] = stat
            
        
# Re-format p = 0  to p = 0.001
var_p[np.where(var_p == 0)] = 0.001       
# FDR correct
fdr_q = [fdr(var_p[v,:], alpha=0.05)[1] for v in np.arange(len(variables))]
fdr_q = np.vstack(fdr_q)        

# Create table of p-values
p_df = pd.DataFrame(var_p, index=variables, columns=ROIlist)
# Create table of q-values 
q_df = pd.DataFrame(fdr_q, index=variables, columns=ROIlist).round(3)

# Create table of cluster characteristics
clust_char_df = pd.DataFrame(clust_char, index=variables, columns=ROIlist).round(3)
clust_thresh_df = pd.DataFrame(clust_thresh, index=variables, columns=ROIlist).round(3)
      