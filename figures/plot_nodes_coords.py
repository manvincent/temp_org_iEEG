#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 12:01:18 2023

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
anatDir = f'{homeDir}/Analysis/Chan_Info'
outDir = '/home/vman/Dropbox/PostDoctoral/Projects/iowa/risk/Manuscript/Figures_Materials'


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

for ROI in ROIlist: 
    # Load in raw contact locations 
    ROI_chanData = pd.read_csv(f'{anatDir}/{ROI}_concat_coordDF.csv')
    ROI_chanData['Patient Idx'] = ROI_chanData['Patient Idx']+1
    
    # Load in bipolar contact locations 
    ROI_BP = pd.read_csv(f'{anatDir}/{ROI}_concat_chanDF.csv')
    ROI_BP['subIdx'] = ROI_BP['subIdx'] + 1
    
    # Append to group 
    group_chanData.append(ROI_chanData)
    group_bipolarData.append(ROI_BP)

    
# Create group DF
groupDF = pd.concat(group_chanData)
groupDF_bipolar = pd.concat(group_bipolarData)




# Plot contact locations per subject
values = np.array(groupDF['Patient Idx']) 
coords = np.array(groupDF.iloc[:,2:5])
plot_markers(values, coords, 
             node_size=10, node_cmap='tab10', black_bg=False, alpha=0.8,
             display_mode='lyrz', colorbar=True)
plt.savefig(f'{outDir}/figS1a_contact.svg')
 

# Plot contact locations per subject
values = np.array(groupDF_bipolar.subIdx) 
coords = np.array(groupDF_bipolar.iloc[:,6:9])
plot_markers(values, coords, 
             node_size=20, node_cmap='tab10', black_bg=False, alpha=0.8,
             display_mode='lyrz', colorbar=True)
plt.savefig(f'{outDir}/figS1b_bipolar.svg')

