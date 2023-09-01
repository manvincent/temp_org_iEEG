#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 14:48:02 2019

@author: vman
"""
import numpy as np
import os
from functions import *


def convertDat(chans, rawDir):
    # Initialize dictionary for storing data properties
    paramDict = dict()
    
    # Loop through channels (separate NCS files) 
    for chIdx, ch in enumerate(chans):     
        print(f'Loading channel: {ch+1}')
        # Load each channel's respective input file
        chanNCS = dict() 
        chanNCS = load_ncs(rawDir + os.sep + 'LFPx' + str(ch+1) + '_0003.ncs')
        
        if (chIdx == 0):
            print(f'Storing acqusition parameters from channel: {ch+1}')
            # Store data properties from the first channel's header
            paramDict['dat_sFreq'] = float(chanNCS['header']['SamplingFrequency'])
            paramDict['dat_highPass'] = float(chanNCS['header']['DspLowCutFrequency'])
            paramDict['dat_lowPass'] = float(chanNCS['header']['DspHighCutFrequency'])
            # Intialize the numpy array holding all data from the first channel's input
            blockArray = np.empty([len(chans), np.shape(chanNCS['data'])[0]] ,dtype=float)
        # Append input data to the array
        blockArray[chIdx] = chanNCS['data']
    return(blockArray, paramDict)



def convertEvents(paramDict, rawDir):
    # Load in event structure 
    eventStruct = dict()
    eventStruct = load_nev(rawDir + os.sep + 'Events.nev')
    
    # Parse the event structure from NEV and make MNE-compatible array
    eventArray = np.zeros([len(eventStruct['events']), 3], dtype=float)
    for ev in np.arange(len(eventStruct['events'])):
        eventArray[ev,0] = eventStruct['events'][ev][1]
        eventArray[ev,2] = eventStruct['events'][ev][3] 
   
    # Create a time array by covnerting from microSec to miliSec and centering against the first sample
    timeArray = ( eventArray[:,0] - eventArray[0,0] ) / 1e6
    
    # Center the timing of the event array so that the first time-sample is zero
    eventArray[:,0] = np.round(timeArray * paramDict['dat_sFreq'])
    
    # Delete events coded as 'zero'
    zeroEventsIdx = np.where(eventArray[:,2] ==0)[0]
    eventArray = np.delete(eventArray, zeroEventsIdx, axis = 0)
    timeArray = np.delete(timeArray, zeroEventsIdx, axis = 0)
    
    return(eventArray, timeArray)


def uniqueChanNames(ch_names):
    """Ensure unique channel names."""
    FIFF_CH_NAME_MAX_LENGTH = 15
    unique_ids = np.unique(ch_names, return_index=True)[1]
    if len(unique_ids) != len(ch_names):
        dups = set(ch_names[x]
                   for x in np.setdiff1d(range(len(ch_names)), unique_ids))
        for ch_stem in dups:
            overlaps = np.where(np.array(ch_names) == ch_stem)[0]
            # We need an extra character since we append '-'.
           # np.ceil(...) is the maximum number of appended digits.
            n_keep = (FIFF_CH_NAME_MAX_LENGTH - 1 -
                      int(np.ceil(np.log10(len(overlaps)))))
            n_keep = min(len(ch_stem), n_keep)
            ch_stem = ch_stem[:n_keep]
            for idx, ch_idx in enumerate(overlaps):
                ch_name = ch_stem + '-%s' % idx
                if ch_name not in ch_names:
                    ch_names[ch_idx] = ch_name
                else:
                    raise ValueError('Adding a running number for a '
                                     'duplicate resulted in another '
                                     'duplicate name %s' % ch_name)
    return ch_names

 
def parseChanLabel(channel_dataframe): 
    # Retrieve # of channels 
    numChans = len(channel_dataframe)
    # Define the channels to include 
    chan_include_idx = np.array(channel_dataframe['Contact'])-1
    # Create label array for data identification 
    subLabel = channel_dataframe['Contact']
    uniqueChanNames(subLabel) # Modifies the array in-place
    subLabel = np.array(subLabel, dtype=str)
    
    # Update the channel dataframe
    channel_dataframe['MNE_label'] = subLabel
    return(subLabel, channel_dataframe, chan_include_idx)


def labelElect(data): 
    electID = np.zeros(len(data))
    e = 0 
    for i in np.arange(1, len(data)):
        if data.Number[i] == data.Number[i-1] + 1:
            electID[i] = e
        else: 
            e += 1
            electID[i] = e 
    data['electID'] = electID
    return data
