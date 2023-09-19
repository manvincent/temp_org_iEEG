#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 13:57:30 2023

@author: vman
"""


import mne
from sklearn.model_selection import StratifiedKFold
from sklearn.linear_model import LogisticRegression
import numpy as np
import pandas as pd
import os
from matplotlib import pyplot as plt

homeDir =  'path to project home directory'
resultsDir = 'path to Results folder'
os.chdir(f'{homeDir}/Analysis/Code')
from functions import *
from functions_stats import *


# Specify output folder for data
resDir = 'path to results folder for reported estimates e.g. ./decode_logit_LFP_chans_BN_stats'
ciDir = 'path to results of CI analysis''
# resampleDir = f'{resultsDir}/decode_logit_LFP_chans_BN_resampled_1000x'
datDir_sub =  'path to folder containing epoch_times.npy'
times = np.load('path to epoch_times.npy')

# Specify ROIs and effects
effectsList = [['Subcallosal Cortex','EV'],
               ['Amygdala','EV'],
               ['Amygdala', 'Outcome'],
               ['Hippocampus','Outcome'],
               ['Angular Gyrus', 'Outcome'],
               ['Subcallosal Cortex', 'Outcome'],
               ['Frontal Orbital Cortex', 'Outcome'],
               ['Frontal Pole', 'Outcome'],
               ['Frontal Orbital Cortex','Erisk'],
               ['Frontal Orbital Cortex','RPE'],
               ['Anterior Insular Cortex','RPE'],               
               ['Frontal Orbital Cortex','riskPE'],
               ['Anterior Insular Cortex','riskPE'],
               ['Hippocampus','EV'],
               ['Supramarginal Gyrus','Erisk'],
               ['Posterior Insular Cortex','Erisk'],
               ['Cingulate Gyrus','RPE'],
               ['Posterior Insular Cortex','RPE'],
               ['Putamen','riskPE']
               ]

for variable in ['Outcome','EV','Erisk','riskPE','RPE']:
    
    # Set variable colour formatting         
    if (variable == 'EV'):
        colour = 'green'
    elif (variable == 'Outcome'):
        colour = 'black'
    elif (variable == 'riskPE'):
        colour = 'red'
    elif (variable == 'Erisk'):
        colour = 'gold'
    elif (variable == 'RPE'):
        colour = 'blue'
    elif (variable == 'Orisk'):
        colour = 'orange'
        
    labels = [] 
    times_max = [] 
    times_sig_min = []
    times_sig_max = []
    accs = [] 
    lowers = [] 
    uppers = [] 
    q_25s = [] 
    meds = [] 
    q_75s = [] 
    null_upbnds = []
    CIs = [] 
    for effect in effectsList:
        ROI, var = effect
        # Set ROI label formatting                                
        if ROI == 'Frontal Orbital Cortex':
            ROI_title = 'OFC'
        elif ROI == 'Angular Gyrus':
            ROI_title = 'Angular Gyr'
        elif ROI == 'Insular Cortex':
            ROI_title = 'Insula'
        elif ROI == 'Cingulate Gyrus':
            ROI_title = 'Cingulate Gyr'
        elif ROI == 'Supramarginal Gyrus':
            ROI_title = 'Supramarg. Gyr'    
        elif ROI == 'Posterior Insular Cortex':
            ROI_title = 'Post.Insula'    
        elif ROI == 'Anterior Insular Cortex':
            ROI_title = 'Ant. Insula'  
        elif ROI == 'Subcallosal Cortex':
            ROI_title = 'vmPFC'  
        elif ROI == 'Hippocampus':
            ROI_title = 'Hippocampus'  
        else: 
            ROI_title = ROI        
                
                
    
        if var == variable: 
            print(f'Plotting ROI: {ROI}, {var}')
                        
            # Load in reported accuracy and timing
            ROIresDir = f'{resDir}/{ROI}'
            null = np.load(f'{ROIresDir}/{ROI}_clust_{var}_perm_upbnd.npy')            
            reportAcc = np.load(f'{ROIresDir}/{ROI}_clust_{var}_acc.npy')
            reportAcc_masked = np.load(f'{ROIresDir}/{ROI}_clust_{var}_acc_masked.npy')
            max_idx = np.argmax(reportAcc_masked)
            # Get times and acc at max (sig) points
            time_max = times[max_idx]
            time_sig = times[reportAcc_masked > 0.5]
            reportAcc_max = reportAcc[max_idx]
            
            # Load in bootlegged CI distribution 
            ROIciDir = f'{ciDir}/{ROI}'
            boot_acc = np.load(f'{ROIciDir}/{ROI}_clust_{var}_boot_acc.npy')
            mean_folds = np.load(f'{ROIciDir}/{ROI}_clust_{var}_mean_folds.npy')
            upper = np.load(f'{ROIciDir}/{ROI}_clust_{var}_upper.npy')
            lower = np.load(f'{ROIciDir}/{ROI}_clust_{var}_lower.npy')
            q_25, med, q_75 = np.percentile(mean_folds, [25,50,75], axis=0)
            
            
            # Append respective quantities
            labels.append(ROI_title)
            times_max.append(time_max)
            times_sig_min.append(time_sig.min())
            times_sig_max.append(time_sig.max())        
            accs.append(reportAcc_max)
            lowers.append(lower[max_idx])
            uppers.append(upper[max_idx])
            q_25s.append(q_25[max_idx])
            meds.append(med[max_idx])
            q_75s.append(q_75[max_idx])
            null_upbnds.append(null[max_idx])
            CIs.append(mean_folds[:,max_idx])
    
    
    # Compute median of null distributions for each effect
    null_meds = np.median(nulls, axis=1)
    CIs_bc =  np.array(CIs).T - null_meds
    lowers_bc = np.array(lowers) - null_meds 
    uppers_bc = np.array(uppers) - null_meds 
    q_25s_bc = np.array(q_25s) - null_meds 
    q_75s_bc = np.array(q_75s) - null_meds 
    meds_bc = np.array(meds) - null_meds 
    acc_bc = np.array(accs) - null_meds 
    null_upbnd_bc = np.array(null_upbnds) - null_meds
    
    
    
    # To create violin plots?
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(4, 4))
    
    inds = np.arange(1, len(null_meds)+1)
    ax.set_xticks(inds)
    ax.set_xticklabels(labels, rotation=45, 
                       ha="right", fontsize=14)  # Adjust rotation and alignment as needed

    # Draw confidence intervals 
    ax.vlines(inds, lowers_bc, uppers_bc, color='k', linestyle='-', lw=3)    
    ax.vlines(inds, q_25s_bc, q_75s_bc, color='k', linestyle='-', lw=5)        
    ax.scatter(inds, meds_bc, s=50, c='k', zorder=3)    
    for c in range(CIs_bc.shape[0]):
        ax.scatter(inds-0.2, CIs_bc[c], s=5, alpha=0.05, c=colour)
    ax.axhline(0, color='grey', linestyle='-')    
    
    # Draw reported accuracy and null distribution upbnd
    # ax.scatter(inds-0.2, acc_bc, s=50, c='orange', marker='+', zorder=3)
    # ax.hlines(null_upbnd_bc, inds-0.3, inds-0.15, color='grey', linestyle='-')
    
    # Violin plots for CI
    parts = ax.violinplot(CIs_bc,
                          positions = inds, 
                          showmeans=False, showmedians=False, showextrema=False)
    for pc in parts['bodies']:
        pc.set_facecolor(colour)
        pc.set_edgecolor('black')
        pc.set_alpha(0.3)    
        # get the center
        m = np.mean(pc.get_paths()[0].vertices[:, 0])
        # modify the paths to not go further left than the center
        pc.get_paths()[0].vertices[:, 0] = np.clip(pc.get_paths()[0].vertices[:, 0], m, np.inf)        
    ax.set_ylim([-0.005, np.max(CIs_bc.max())+0.01])
    ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%.2f'))
    # ax.set_xlabel('ROI', fontsize=14)
    # ax.set_ylabel(r'$\Delta$ ROC AUC', fontsize=14)