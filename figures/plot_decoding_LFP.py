#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 22:38:29 2022

@author: vman
"""


import mne
import numpy as np
import pandas as pd
from scipy.stats import percentileofscore
from copy import deepcopy as dcopy
from scipy import signal
# Build filter
filt_b, filt_a = signal.butter(1, [0.1], btype='lowpass') #low pass filter

from scipy.stats import sem as sem
from pathlib import Path
import seaborn as sns
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.ticker import FormatStrFormatter

# Define plot styling
from matplotlib.patches import Rectangle
matplotlib.rcParams['xtick.labelsize'] = plt.rcParams['ytick.labelsize'] = plt.rcParams['axes.labelsize'] = 10
import os
homeDir = '/media/Data/Projects/iowa_lfp'
os.chdir(f'{homeDir}/Analysis/Code')
from functions_stats import *


# Specify analysis Type to plot
analysisType = 'timeseries'
# Specify where the data are
datDir =  f'{homeDir}/Analysis/Data_LFP'

resultsDir = f'{homeDir}/Analysis/Results/decode_logit_LFP_chans_BN_stats'
# featureDir = f'{homeDir}/Analysis/Results/decode_logit_LFP_old_features'
outDir = '/home/vman/Dropbox/PostDoctoral/Projects/iowa/risk/Manuscript/Figures_Materials'


# Import timing array
times = np.load(f'{datDir}/epoch_times.npy')
times = times[100:]
# Specify list of effects
# effects = ['EV','Outcome']
# effects = ['Erisk','riskPE']
effects = ['EV']
# effects = ['Erisk', 'EV','Outcome','riskPE','RPE','Orisk']

for eff in effects: 
    # Parsing for significant effects 
    acc_list = [] 
    for path in Path(f'{resultsDir}').rglob(f'*{eff}_acc_masked.npy'):
        acc_list.append(path.name)    
    effectPrefix = [i.split('_acc_masked.npy')[0] for i in acc_list]

    # Initialize plot 
    fig, ax = plt.subplots(len(effectPrefix),1, 
                           figsize=(2,2*len(effectPrefix)),
                           sharex=True, sharey=True)
    fig.text(0.5, 0.05, 'Time since onset [sec]', ha='center' )
    fig.text(-0.15, 0.5, r'A.U.C.', va='center', rotation='vertical')
    # Pull out effects for each region 
    acc_ROI = []
    sig_period = []
    peakAcc = [] 
    y_mean = [] 
    ROI_name = [] 
    for effIdx, effectPre in enumerate(effectPrefix):

        # Specify ROI and effect name
        currROI = effectPre.split('_')[0]
        if currROI == 'Frontal Orbital Cortex':
            ROI_title = 'OFC'
        elif currROI == 'Angular Gyrus':
            ROI_title = 'Angular Gyr'
        elif currROI == 'Insular Cortex':
            ROI_title = 'Insula'
        elif currROI == 'Cingulate Gyrus':
            ROI_title = 'Cingulate Gyr'
        elif currROI == 'Supramarginal Gyrus':
            ROI_title = 'Supramarg. Gyr'    
        elif currROI == 'Posterior Insular Cortex':
            ROI_title = 'Post.Insula'    
        elif currROI == 'Anterior Insular Cortex':
            ROI_title = 'Ant. Insula'  
        elif currROI == 'Subcallosal Cortex':
            ROI_title = 'vmPFC'  
        elif currROI == 'Hippocampus':
            ROI_title = 'Hippocampus'  
        else: 
            ROI_title = currROI
        ROI_name.append(ROI_title) 
        # Get ROI directory
        roiDir = f'{resultsDir}/{currROI}'
        # Get ROI's channel info
        roiChans = pd.read_csv(f'{roiDir}/{currROI}_concat_chanDF.csv')
        # Get mean Y coordinate:
        centroid= np.mean(np.array(roiChans.filter(like='CIT').filter(like='Y')))
        y_mean.append(centroid)
        
        currEff = effectPre.split('_')[-1]
        if (currEff == 'EV'):
            colour = 'green'
        elif (currEff == 'Outcome'):
            colour = 'black'
        elif (currEff == 'riskPE'):
            colour = 'red'
        elif (currEff == 'Erisk'):
            colour = 'gold'
        elif (currEff == 'RPE'):
            colour = 'blue'
        elif (currEff == 'Orisk'):
            colour = 'orange'
            
      

        # Load in decode accuracy
        acc = acc_masked = sem = []
        acc = np.load(f'{roiDir}/{effectPre}_acc.npy')     
        acc_ROI.append(acc)
        acc_filt = signal.filtfilt(filt_b, filt_a, acc)
        
        acc_masked = np.load(f'{roiDir}/{effectPre}_acc_masked.npy')
        # acc_masked[times < 0.31] = 0.5     
        
        # Get null distribution
        null = np.load(f'{resultsDir}/{currROI}/{effectPre}_clust_null.npy')
        upbnd = np.load(f'{roiDir}/{effectPre}_perm_upbnd.npy')
        diff = acc[acc_masked > 0.5] - upbnd[acc_masked > 0.5]
        stat = np.sum(np.abs(diff))
        p = 1 - percentileofscore(null, stat, nan_policy='omit')/100
        print(f'{currROI}: {currEff}: p = {np.round(p,3)}')
                
        sig_period.append(times[np.where((acc_masked>0.5) & (times>0))]) 
        peakAcc.append(times[np.argmax(acc_masked)]) 
        sem = np.load(f'{roiDir}/{effectPre}_sem.npy')
        # Load in permutation upper bound
        perm_thresh = np.load(f'{roiDir}/{effectPre}_perm_upbnd.npy')
        
        ax[effIdx].title.set_text(f'{ROI_title}')
        ax[effIdx].set_ylim([0.45, 0.58])        
        ax[effIdx].yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        ax[effIdx].axvline(0, linewidth=2, color='red', linestyle='--')
        ax[effIdx].plot(times, acc_filt, color=colour, linewidth=3,alpha=1)          
        ax[effIdx].fill_between(times,
                        acc_filt-sem, acc_filt+sem,                        
                        facecolor=colour, alpha=0.3)
        ax[effIdx].plot(times, perm_thresh, color='red', alpha=0.8, linewidth=2)
        
        # Get start/stop timepoints of significance 
        mask = (acc_masked > 0.5) & (times > 0)
        mask = np.insert(mask, -1, 0)
        first_vals = np.argwhere((~mask[:-1] & mask[1:]))  # Look for False-True transitions
        last_vals = np.argwhere((mask[:-1] & ~mask[1:])) + 1  # Look for True-False transitions
        # Fill area of significance 
        for start, stop in zip(first_vals, last_vals):            
            ax[effIdx].axvspan(times[start], times[stop], facecolor='grey', alpha=0.6)
            
    # fig.savefig(f'{outDir}/{currEff}_decode_LFP.svg', format="svg")
    
    
    
    # Plot significant periods as boxplot
    # Mask out ROIS not plotted 
    acc_ROI = np.array(acc_ROI)
    sig_period_ROI = np.array(sig_period)
    peakAcc_ROI = np.array(peakAcc)
    y_mean_ROI = np.array(y_mean)
    names_ROI = np.array(ROI_name)
    # Re-order by peak accuracy (earliest to latest)
    acc_ROI = acc_ROI[np.argsort(peakAcc_ROI)]
    names_ROI = names_ROI[np.argsort(peakAcc_ROI)]
    sig_period_ROI = sig_period_ROI.T[np.argsort(peakAcc_ROI)]
    peakAcc_ROI = peakAcc_ROI[np.argsort(peakAcc_ROI)]
    
    fig,ax = plt.subplots(1,1, figsize=(2,2))
    fig.suptitle('effect')
    ax.scatter(peakAcc, y_mean, color=colour)
    sns.regplot(x=peakAcc, y = y_mean, color=colour, ci=None, fit_reg=False,
                ax=ax)
    ax.set_xlim([-0.2,0.5])
    ax.invert_yaxis()
    ax.set_xlabel('Peak decoding time [sec]')
    ax.set_ylabel(r'$\longleftarrow$ Anterior [y]')

    # fig.savefig(f'{outDir}/{currEff}_decode_LFP_spatiotemporal.svg', format="svg")
    
    
    
    fig,ax = plt.subplots(1,1, figsize=(2,2))
    for i in np.arange(len(names_ROI)):
        ax.fill_between(times, i-0.3, i+0.3,
                        where=np.in1d(times,sig_period_ROI[i]),
                        color=colour, alpha=0.6)
        ax.fill_between(times, i-0.5, i+0.5,
                        where=np.in1d(times,peakAcc_ROI[i]),
                        color='black')
    ax.set_xlim([-0.2,0.5])
    ax.set_yticks(np.arange(len(names_ROI)), list(names_ROI))    
    ax.set_xlabel('Time since onset [sec]')
    # fig.savefig(f'{outDir}/{currEff}_decode_LFP_latency.svg', format="svg")
    
