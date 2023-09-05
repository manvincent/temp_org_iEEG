#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 13 01:16:23 2021

@author: vman
"""

from nilearn.plotting import plot_markers, plot_roi
from nilearn import datasets
import numpy as np
import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
# Define plot styling
matplotlib.rcParams['xtick.labelsize'] = plt.rcParams['ytick.labelsize'] = plt.rcParams['axes.labelsize'] = 10

import os
homeDir = '/media/Data/Projects/iowa_lfp'
anatDir = f'{homeDir}/Anatomy/anatomicalData/contactData'
roiAnatDir = f'{homeDir}/Analysis/Results/timeseries_LFP/Group_level_timeseries'
outDir = '/home/vman/Dropbox/PostDoctoral/Projects/iowa/risk/Manuscript/Figures_Materials'

subList = np.array([384,399,403,418,493,507,525,532,567,585])

# Specify ROIs of interest
ROIlist = ['Frontal Pole',
           'Subcallosal Cortex',
           'Frontal Orbital Cortex',
           'Cingulate Gyrus',
           'Supramarginal Gyrus',
           'Angular Gyrus',
           'Putamen',
           'Hippocampus',
           'Amygdala',
           'Anterior Insular Cortex',
           'Posterior Insular Cortex']


# Load in subject contact location data
group_chanData = [] 
group_bipolarData = [] 
for subIdx, subID in enumerate(subList):    
    # Load in raw contact locations 
    sub_chanData = pd.read_csv(f'{anatDir}/{subID}_contact_locations_fsparc.csv')
    sub_chanData['subIdx'] = subIdx+1
    # Load in bipolar contact locations 
    sub_bipolarData = pd.read_csv(f'{anatDir}/{subID}_contact_locations_bipolar.csv')
    sub_bipolarData ['subIdx'] = subIdx+1
    
    # Append to group 
    group_chanData.append(sub_chanData)
    group_bipolarData.append(sub_bipolarData)

# Create group DF
groupDF = pd.concat(group_chanData)
groupDF_bipolar = pd.concat(group_bipolarData)


# Plot contact locations per subject
values = np.array(groupDF.subIdx) 
coords = np.array(groupDF.iloc[:,5:8])
plot_markers(values, coords, 
             node_size=5, node_cmap='Dark2', black_bg=False, alpha=0.8,
             display_mode='lyrz', colorbar=True)
# plt.savefig(f'{outDir}/figS1_contact.svg')
 
# Plot contact locations per subject
values = np.array(groupDF_bipolar.subIdx) 
coords = np.array(groupDF_bipolar.iloc[:,1:4])
plot_markers(values, coords, 
             node_size=5, node_cmap='Dark2', black_bg=False, alpha=0.8,
             display_mode='lyrz', colorbar=True)
# plt.savefig(f'{outDir}/figS1_bipolar.svg')

# Plot contact locations per ROI 
all_ROIdata= [] 
for ROIidx, ROI in enumerate(ROIlist): 
    # Load in ROI (group averaged) contact locations 
    ROI_chanData = pd.read_csv(f'{roiAnatDir}/{ROI}/{ROI}_coordsDF.csv')
    ROI_chanData['ROIidx'] = ROIidx+1
    ROI_chanData['ROI'] = ROI 
    # Append across ROIs
    all_ROIdata.append(ROI_chanData)
# Create all coordinates across ROIs 
all_ROIdf = pd.concat(all_ROIdata)

# Plot contact locations per ROI
values = np.array(all_ROIdf.ROIidx) 
coords = np.array(all_ROIdf.iloc[:,2:5])
plot_markers(values, coords, 
             node_size=20, node_cmap='tab20', black_bg=False, alpha=0.8,
             display_mode='lyrz', colorbar=True)
# plt.savefig(f'{outDir}/fig1_contactROI.svg')
