#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 14:18:58 2019

@author: vman
"""


import mne
import numpy as np
from copy import deepcopy as dcopy
import pandas as pd
import multiprocessing
num_cores = multiprocessing.cpu_count()
import os
homeDir = 'path to project home directory'
from functions import *

# Specify where the data are
datDir = 'path to data directory containting output from convert_ncs2mne.py'
# Specify output folder for data
outDir = 'output directory e.g. ./Data_preprocessed'
if not os.path.exists(outDir):
    os.makedirs(outDir)


## Specify subjects and blocks
subList = 'list of subject IDs'

blockList = 'block IDs for each subject' 

# Specify the task-start and task-stop event codes
taskStart_code  = 5
taskEnd_code = 6
trialStart_code = 8
trialEnd_code = 16
expEnd_code = 2
guessResp_code = 10
card1_code = 11
# Specify filter cutoffs
low_cutoff = 1
high_cutoff = 250
# Specify (first-order) line noise frequency
notch_freq = 60



for subIdx, subID in enumerate(subList):
    subDir = f'{datDir}/patient_{subID}'
    # Make subject-specific output directory
    subOutDir = f'{outDir}/patient_{subID}'
    if not os.path.exists(subOutDir):
        os.makedirs(subOutDir)

    # Load in subject's channel info
    chansPath = 'path to channel info *_chan_info.pk' 
    subChanDF = pd.read_pickle(chansPath).sort_values('Contact').reset_index(drop=True)

    # Load in bipolar channel mapping
    bipolarPath = 'path to bipolar contact location info' 
    bipolarChanDF = pd.read_csv(bipolarPath).sort_values('Contact').reset_index(drop=True)



    for blockIdx in np.arange(len(blockList[subIdx])):
        blockID = blockList[subIdx][blockIdx]

        # Print which subject/block is being preprocessed
        print('Preprocessing data for Subject:' + subID + ' Block:' + blockID)

        # Load in data
        dataPath = f'{subDir}/patient{subID}_block{blockID}_mne_raw.fif'
        mne_raw = mne.io.read_raw_fif(dataPath, preload=True)
        # Load in events
        eventPath = f'{subDir}/patient{subID}_block{blockID}_mne_events.npy'
        mne_events = np.load(eventPath)
        # Load in real times
        timesPath = f'{subDir}/patient{subID}_block{blockID}_event_times.npy'
        blockTimes = np.load(timesPath)

        # Initalize preprocess-data object
        preprocess_mne = Preprocess(data = mne_raw, events = mne_events)

        # Downsample data (jointly with events)
        preprocess_mne.downSample(high_cutoff = high_cutoff)

        # Delete non-task related data
        blockTimes = preprocess_mne.trimNonTask(taskStart_code, taskEnd_code, trialStart_code, trialEnd_code, blockTimes)

        ## Artifact scrubbing
        # High-pass filter the data (exclude low frequencies, i.e. drift)
        preprocess_mne.bandpassFilter(low_cutoff = low_cutoff, high_cutoff = None)

        # Perform ICA-based denoising on the data
        ICA_fig = preprocess_mne.ICAclean(uniform_threshold = 0.2)

        # Low-pass filter the data (exclude high frequencies)
        preprocess_mne.bandpassFilter(low_cutoff = None, high_cutoff = high_cutoff)

        # Notch filter the data at 60 Hz
        preprocess_mne.data.notch_filter(np.arange(notch_freq,high_cutoff,notch_freq), notch_widths=1, fir_design='firwin')


        for e,elec in enumerate(np.unique(subChanDF['electID'])):   ## Wrangle data for each electrode separately
            # Print which electrode is being preprocessed
            print('Referencing channels on electrode: ' + str(elec))

            # Subset data to include only channels on the current electrode
            curr_mne_filtered = preprocess_mne.data.copy().pick_channels(subChanDF.MNE_label[np.where(subChanDF.electID == elec)[0]].tolist())

            # Perform ICA-based denoising on the data
            preprocess_elec = Preprocess(data = curr_mne_filtered, events = mne_events)
            ICA_fig_elec = preprocess_elec.ICAclean(uniform_threshold = 0.05)
            curr_mne_filtered_elec = preprocess_elec.data.copy()


            # Append the channels to the first electrode raw structure
            if (e == 0):
                # Initialize the appended preprocessed data structure using the first electrode
                mne_filtered = curr_mne_filtered_elec.copy()
            elif (e != 0):
                 # Append independently referenced electrodes together
                mne_filtered.add_channels([curr_mne_filtered_elec])


        # Bipolar referencing
        referenceBipolar(mne_filtered,
                         bipolarChanDF.anode.astype(str).tolist(),
                         bipolarChanDF.cathode.astype(str).tolist())

        # Only keep bipolar channels
        keepChan = np.array(mne_filtered.info.ch_names)[np.where(['-' in x for x in mne_filtered.info.ch_names])[0]]
        mne_filtered_bipolar = mne_filtered.copy().pick_channels(keepChan)


        # Clean up events and timing data
        blockTimes = preprocess_mne.cleanEvents(expEnd_code, guessResp_code, card1_code, blockTimes)

        # Save preprocessed mne-continuous data (by reference type)
        # For bipolar-based referencing
        savePreprocessed_FilePath = f'{subOutDir}/patient{subID}_block{blockID}_mne_preproc.fif'
        mne_filtered_bipolar.save(savePreprocessed_FilePath,overwrite=True)

        # Save adjusted events structure
        saveEvents_FilePath = f'{subOutDir}/patient{subID}_block{blockID}_mne_preproc_events.npy'
        np.save(saveEvents_FilePath, preprocess_mne.events)

        # Save adjusted event times array
        saveTimes_FilePath = f'{subOutDir}/patient{subID}_block{blockID}_preproc_event_times.npy'
        np.save(saveTimes_FilePath, blockTimes)

        # Save ICA-artifact output for QC
        saveFig_FilePath = f'{subOutDir}/patient{subID}_block{blockID}_ICA_QC.png'
        ICA_fig.savefig(saveFig_FilePath)
