
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 14:29:07 2019

@author: vman
"""

import mne
import numpy as np
import pandas as pd
import multiprocessing
num_cores = multiprocessing.cpu_count()
import os
homeDir = 'path to project home directory'
from functions import *

# Specify where the data aref
datDir = 'path to data directory containting raw data in per-sub subdirectories'
anatDir = 'path to contact data directory'
# Specify output folder for data
outDir = 'output directory e.g. ./Data_unfiltered'
if not os.path.exists(outDir):
    os.makedirs(outDir)


## Specify subjects and blocks
subList = np.unique([i.split('_')[1] for i in next(os.walk(datDir))[1]])

blockList = 'block IDs for each subject' 
# e.g. np.array([['031'],['037','038'],['043'],['043','044'],['001','003'],['001','002'],['044','046'],['060','063']],dtype=object)



# check that blocks and chans correspond to subjects
if (len(subList) != len(blockList)):
    raise Exception("Error! Check subject and block lists")



for subIdx, subID in enumerate(subList):
    subDir = f'{datDir}/patient_{subID}'
    # Make subject-specific output directory
    subOutDir = f'{outDir}/patient_{subID}'
    if not os.path.exists(subOutDir):
        os.makedirs(subOutDir)

    # Read in subject-specific channel anatomy file
    subChanDF = pd.read_csv(f'{anatDir}/{subID}_contact_locations_fsparc.csv')
    # Add column for electrode number
    subChanDF = labelElect(subChanDF)


    # Parse channel labels and ROIs for this subject
    [subLabel, subChanDF, chanInclude] = parseChanLabel(subChanDF)
    # Save the channel ROI array and parsed channel labels
    saveChans_FilePath = subOutDir + os.sep + 'patient' + subID + '_chan_info.pkl'
    subChanDF.to_pickle(saveChans_FilePath)

    # Loop through task blocks
    for blockIdx in np.arange(len(blockList[subIdx])):
        blockID = blockList[subIdx][blockIdx]
        # Specify block raw data directory
        rawDir = f'{subDir}/raw_block_{blockID}'

        # Define output paths
        saveRaw_FilePath = f'{subOutDir}/patient{subID}_block{blockID}_mne_raw.fif'
        saveEvents_FilePath = f'{subOutDir}/patient{subID}_block{blockID}_mne_events.npy'
        saveTimes_FilePath = f'{subOutDir}/patient{subID}_block{blockID}_event_times.npy'


        if not os.path.exists(saveRaw_FilePath):
            print(f'Converting data for Subject: {subID} Block: {blockID}')

            # Convert the raw data into numpy array (MNE-compatible)
            [blockArray,paramDict] = convertDat(chanInclude, rawDir)

            # Convert the event codes (triggers) into numpy array (MNE-compatible)
            [mne_events,blockTimes] = convertEvents(paramDict,rawDir)

            ## Pass information to MNE info structure
            info = mne.create_info(
                    ch_names = subLabel.tolist(),
                    ch_types =  np.repeat('ecog',len(chanInclude)).tolist(),
                    sfreq = paramDict['dat_sFreq'])
            info['highpass'] = paramDict['dat_highPass']
            info['lowpass']= paramDict['dat_lowPass']

            # Integrate into MNE data structure
            mne_raw = mne.io.RawArray(blockArray, info)

            # Downsample to 1000 Hz
            # (Max. usable frequency: 500 Hz)
            mne_raw_resampled, mne_events_resampled = mne_raw.copy().resample(1000,npad='auto',events=mne_events,n_jobs=num_cores)

            # Save MNE data
            mne_raw_resampled.save(saveRaw_FilePath,overwrite=True)

            # Save the event codes (timestamp = data index)
            np.save(saveEvents_FilePath, mne_events_resampled)

            # Save the event times (timestamp = real time in ms)
            np.save(saveTimes_FilePath, blockTimes)

            del blockArray
            del mne_raw
            del mne_raw_resampled
        else:
            print('Already processed subject: ' + subID + ', block: ' + blockID)
