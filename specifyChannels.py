#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 26 08:37:37 2020

Loads in specified template image and each subject's channel locations (from EMU lab)
Identifies channels as being in GM or WM, and sets bipolar pairings between adjacent channels
Computes 'averaged coordinates' between bipolar pairs to map onto interpolated bipolar virtual channels in preprocessing
Outputs subject-specific updated channel coordinates and GM/WM information 

@author: vman
"""


import numpy as np
import pandas as pd
import os
homeDir = '/media/Data/Projects/iowa_lfp'
os.chdir(f'{homeDir}/Analysis/Code')
from functions import *

# Specify where the data are
datDir = f'{homeDir}/Anatomy/anatomicalData/contactData'

# Process template image
template = f'{homeDir}/Anatomy/anatomicalData/Template/CIT168_T1w_700um_MNI.nii.gz'
templateMask = f'{homeDir}/Anatomy/anatomicalData/Template/CIT_mask.nii.gz'

# Specify whether to use all channels or only grey matter
chanType = 'GM' # Can be 'all' or 'GM'
## Specify subjects and blocks
subList = np.unique([i.split('_')[0] for i in next(os.walk(datDir))[2]])


for subIdx, subID in enumerate(subList):
    print(f'Computing bipolar channel locations for {subID}')
    # Load in subject's channel info
    subChanDF = pd.read_csv(f'{datDir}/{subID}_contact_locations_fsparc.csv')

    # Create new channel class
    label_channel = Channel(data = subChanDF)

    # Add column for electrode number
    label_channel.labelElect()

    # Identify GM vs WM voxels before bipolar averaging
    label_channel.convertCoord(template, chanType = 'all') 
    label_channel.maskCoordinates(templateMask)

    # Update bipolar dataframes
    label_channel.bipolarPairs()

    # Clean up bipolar channels not in grey matter
    if chanType == 'GM':
        label_channel.maskGM()

    # Output to csv
    if chanType == 'all':
        outPath = f'{datDir}/{subID}_contact_locations_bipolar.csv'
    elif chanType == 'GM':
        outPath = f'{datDir}/{subID}_contact_locations_bipolarGM.csv'

    label_channel.data_bipolar.to_csv(outPath, sep=',', index=False)
