#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 22:39:18 2022

@author: vman
"""


import nilearn as nl
import nilearn.image as nlimg
import xml.etree.ElementTree as ET
from nilearn.plotting import plot_glass_brain, plot_markers
from scipy.stats import zscore
import numpy as np
import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
matplotlib.rcParams['xtick.labelsize'] = plt.rcParams['ytick.labelsize'] = plt.rcParams['axes.labelsize'] = 10
import os

# Specify where template/atlas data are
homeDir =  'path to home directory''
anatDir = 'path to contact coordinate directory e.g. ./contactData'
roiAnatDir = 'path to results of decoding analysis from full model'
roiFeatDir = 'path to results of decoding analysis - feature importance'
outDir = 'output directory'
templateDir = 'path to anatomical template directory'

template = f'{templateDir}/CIT168_T1w_700um_MNI.nii.gz'
cortMask = f'{templateDir}/cortical_atlases.nii.gz'
cort_xml = f'{templateDir}/HarvardOxford-Cortical.xml'
subcortMask = f'{templateDir}/subcortical_atlases.nii.gz'
subcort_xml = f'{templateDir}/HarvardOxford-Subcortical.xml'

# Iterate over cortical ROIs 
cort_img = nlimg.load_img(cortMask)     
ROI_cortical = ET.parse(cort_xml).getroot()
subcort_img = nlimg.load_img(subcortMask)
ROI_subcortical = ET.parse(subcort_xml).getroot()


# Parse ROI images for the EV effect
effects = {'EV':  [['Amygdala',                    
                    'Hippocampus',
                    'Subcallosal Cortex'],
                    'summer'],
            'Outcome':  [['Frontal Orbital Cortex',
                          'Amygdala',              
                          'Frontal Pole',
                          'Subcallosal Cortex',
                          'Hippocampus',
                          'Angular Gyrus'],
                         'autumn'],
            'Erisk':  [['Frontal Orbital Cortex',
                         'Supramarginal Gyrus',                    
                         'Posterior Insular Cortex'],                   
                        'Wistia'],
             'riskPE': [['Frontal Orbital Cortex',
                         'Putamen',
                        'Anterior Insular Cortex'],
                        'gist_heat'],
             'RPE': [['Frontal Orbital Cortex',
                     'Cingulate Gyrus',
                     'Anterior Insular Cortex',
                     'Posterior Insular Cortex'],            
                       'Blues']}
            
for eff, eff_ROI in effects.items(): 
    eff_ROI_maps = [] 
    for ROIidx, ROI in enumerate(eff_ROI[0]): 
        # Look for maps in the cortical atlas 
        for cortROI in ROI_cortical[1]:
            # String match by ROI name
            if ROI in cortROI.text:
                print(f'Identified {cortROI.text}')            
                ROI_idx = int(cortROI.attrib['index'])
                # Get ROI image from correct volume of atlas 
                niimg_data = nlimg.get_data(cort_img)[:,:,:,ROI_idx]
                # Threshold according to p > 10
                niimg_data[np.where(niimg_data < 10)] = 0
                # Create new ROI image 
                eff_ROI_maps.append(nlimg.new_img_like(template, niimg_data))
        
        # Look for maps in the subcortical atlas 
        for subcortROI in ROI_subcortical[1]:
            # String match by ROI name
            if ROI in subcortROI.text:
                print(f'Identified {subcortROI.text}')
                ROI_idx = int(subcortROI.attrib['index'])
                # Get ROI image from correct volume of atlas 
                niimg_data = nlimg.get_data(subcort_img)[:,:,:,ROI_idx]
                # Threshold according to p > 10
                niimg_data[np.where(niimg_data < 10)] = 0
                # Create new ROI image 
                eff_ROI_maps.append(nlimg.new_img_like(template, niimg_data))
    
    
    # Plot contact locations per relevant ROI for this effect 
    eff_ROIdata= [] 
    for ROIidx, ROI in enumerate(eff_ROI[0]): 
        # Load in ROI (group averaged) contact locations 
        ROI_chanData = pd.read_csv('path to coordinate csv for ROI')
        ROI_chanData['ROIidx'] = ROIidx+1
        ROI_chanData['ROI'] = ROI 
        # Load in feature importance     
        weights = np.load('path to feature importance results ')
        acc_masked = np.load('path to statistical test results') # To identify periods of significance
        # Get average weights during significant period
        weight_sig = np.mean(weights[:,np.where(acc_masked > 0.5)[0]], axis=1)
        # Get positive weights
        weight_sig[weight_sig < 0] = np.nan
        ROI_chanData['feature_weights'] = zscore(weight_sig, nan_policy='omit')
        # Append across ROIs
        eff_ROIdata.append(ROI_chanData)
    # Create all coordinates across ROIs 
    eff_ROIdf = pd.concat(eff_ROIdata)
    
    
    values = np.array(eff_ROIdf.feature_weights)
    coords = np.array(eff_ROIdf.iloc[:,2:5])
    display = plot_markers(values, coords, 
                 node_size=10, node_cmap=eff_ROI[1],
                 black_bg=False, alpha=1, node_vmin=-1,node_vmax=1,
                 display_mode='z', colorbar=True)
    
    for ROIidx, ROImap in enumerate(eff_ROI_maps):
        display.add_contours(ROImap, levels=[10], colors='black', 
                             filled=False, alpha=0.7, linewidths=3)
    
    display.savefig(f'{outDir}/{eff}_decode_topoplot.svg')



