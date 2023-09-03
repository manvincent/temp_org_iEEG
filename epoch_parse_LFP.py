#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 12:35:03 2020

Load in preprocessed data (LFP, non-decomposed signal) and parse into epochs.
Save the Epoch (mne-type) files for each subject/block
All trial events (event codes) are embedded into a single structure

@author: vman
"""


import mne
import numpy as np
import pandas as pd
import time
import os
# homeDir = '/export/home/vman/iowa/ephys'
homeDir = '/media/Data/Projects/iowa_lfp'
os.chdir(f'{homeDir}/Analysis/Code')
from functions import *

# Specify where the data are
datDir =   f'{homeDir}/Analysis/Data_preprocessed'
# Specify output folder for data
outDir =  f'{homeDir}/Analysis/Data_LFP_BN'
if not os.path.exists(outDir):
    os.makedirs(outDir)

## Specify subjects and blocks
subList = np.unique([i.split('_')[1] for i in next(os.walk(datDir))[1]])

# Some subIDs are repeated because they have multiple blocks of data
blockList = np.array([['031'],
                      ['037','038'],
                      ['043'],
                      ['043','044'],
                      ['001','003'],
                      ['001','002'],
                      ['044','046'],
                      ['060','063'],
                      ['095'],
                      ['122']],dtype=object)

# Specify epoching parameters here:
tmin = 0.8
tmax = 1.5 # extent of epoch window (sec)

# Create legend of event IDs
event_id = {'GuessOn': 9,
            'GuessResp': 10,
            'Card1On': 11,
            'Card1Off': 12,
            'Card2On': 13,
            'ReportOn': 14,
            'ReportResp': 15}

for subIdx, subID in enumerate(subList):
    subDir = f'{datDir}/patient_{subID}'
    # Make subject-specific output directory
    subOutDir = f'{outDir}/patient_{subID}'
    if not os.path.exists(subOutDir):
        os.makedirs(subOutDir)

    for blockIdx in np.arange(len(blockList[subIdx])):
        blockID = blockList[subIdx][blockIdx]

        # Load in data
        dataPath = f'{subDir}/patient{subID}_block{blockID}_mne_preproc.fif'
        mne_preproc = mne.io.read_raw_fif(dataPath, preload=True)

        # Load in events
        eventPath = f'{subDir}/patient{subID}_block{blockID}_mne_preproc_events.npy'
        mne_events = np.load(eventPath)

        # Parse events to only include those specified in event_id (for epoching)
        events_idx = [np.where(mne_events[:,2] == list(event_id.values())[i])[0] for i in np.arange(len(event_id))]
        mne_events = mne_events[np.sort(np.concatenate(events_idx))]
        np.save(f'{subOutDir}/patient{subID}_block{blockID}_mne_preproc_events_trimmed.npy', mne_events)

        # Initalize Epoch-data object
        epoch_mne = Epoch(data = mne_preproc)

        # Epoch data round the events
        mne_epoch, _ = epoch_mne.epochData(mne_events,
                                           event_id,
                                           tmin,
                                           tmax,
                                           baseline_bool = True,
                                           baseline_tmin = -0.2,
                                           baseline_tmax = 0)

        # Save un-averaged epoched data
        saveERP_FilePath = f'{subOutDir}/patient{subID}_block{blockID}_mne_ERP.fif'
        mne_epoch.save(saveERP_FilePath ,overwrite=True)

# Save an instance of the epoch timings
times = mne_epoch._raw_times
np.save(f'{outDir}/epoch_times.npy', times)
