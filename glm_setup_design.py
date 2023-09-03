#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 22:18:53 2020

@author: vman
"""


import numpy as np
import pandas as pd
import os
homeDir = '/media/Data/Projects/iowa_lfp'
os.chdir(f'{homeDir}/Analysis/Code')
from functions_stats import *



# Specify where the data are
datDir =  f'{homeDir}/Analysis/Data_LFP_BN'
outDir = f'{homeDir}/Analysis/Design'
if not os.path.exists(outDir):
    os.makedirs(outDir)

## Specify subjects and blocks
subList = np.unique([i.split('_')[1] for i in next(os.walk(datDir))[1]])
# subList = ['567','585']

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


# Code legends
event_id = {'GuessOn': 9,
    'GuessResp': 10,
    'Card1On': 11,
    'Card1Off': 12,
    'Card2On': 13,
    'ReportOn': 14,
    'ReportResp': 15}

compVar_code= {'P1_risk': 10,
               'P1': 11,
               'P1_rpe': 11,
               'P1_obsvRisk': 11,
               'P1_riskPE': 11,
               'P2_risk': 12,
               'P2': 13,
               'P2_rpe': 13,
               'P2_obsvRisk': 13,
               'P2_riskPE': 13,
               'card1': 11,
               'reportAcc': 15,
               'guessLeft':10}

designRegressors = dict(ev = ['P1'],
                  outcome = ['P2'],
                  rpe = ['P2_rpe'],
                  Erisk = ['P1_risk','P2_risk'],
                  Orisk = ['P2_obsvRisk'],
                  PErisk = ['P2_riskPE'],
                  covar = ['card1','reportAcc'])



for subIdx, subID in enumerate(subList):
    subDir = f'{datDir}/patient_{subID}'
    subOutDir = f'{outDir}/patient_{subID}'
    if not os.path.exists(subOutDir):
        os.makedirs(subOutDir)


    concat_designMat = []
    concat_modRegress = []
    for blockIdx in np.arange(len(blockList[subIdx])):
        blockID = blockList[subIdx][blockIdx]

        # Load in behavioural data
        subData = pd.read_csv(f'{homeDir}/Analysis/Behaviour/patient{subID}_block{blockID}_behav.csv')

        # Load in events
        eventPath = f'{datDir}/patient_{subID}/patient{subID}_block{blockID}_mne_preproc_events_trimmed.npy'
        mne_events = np.load(eventPath)

        # Pull out event labels/codes as separate DF
        eventCodes = pd.DataFrame({'code':mne_events[:,2]})

        ## Create design matrix
        # Create non-modulate consets
        card1On = np.zeros(len(eventCodes),dtype=int)
        card2On = np.zeros(len(eventCodes),dtype=int)
        cardOn = np.zeros(len(eventCodes),dtype=int)
        cardISI = np.zeros(len(eventCodes),dtype=int)
        respAction = np.zeros(len(eventCodes),dtype=int)

        card1On[np.where((eventCodes.code == event_id['Card1On']))[0]] = 1
        card2On[np.where((eventCodes.code == event_id['Card2On']))[0]] = 1
        cardOn[np.where((eventCodes.code == event_id['Card1On']) |  (eventCodes.code == event_id['Card2On']))[0]] = 1
        cardISI[np.where((eventCodes.code == event_id['GuessResp']) | (eventCodes.code == event_id['Card1Off']))[0]] = 1
        respAction[np.where((eventCodes.code == event_id['GuessResp']) | (eventCodes.code == event_id['ReportResp']))[0]] = 1
        # Add to new design dataframe
        designMat = pd.DataFrame(dict(respAction = respAction,
                                      card1On = card1On,
                                      card2On = card2On,
                                      cardOn = cardOn,
                                      cardISI = cardISI))

        # Compute the model-based regressors for this subject
        [modRegress, regressFig] = computeRegressor(subData)
        modRegress['blockID'] = blockIdx

        # Append regressor to event codes
        eventIndices = dict()
        pModDF = pd.DataFrame()
        for varIdx, compVar in enumerate(compVar_code.items()):
            # Compute mean of regressor
            varMean = np.nanmean(modRegress[compVar[0]])
            # Initialize compvar array
            pMod = np.zeros(len(eventCodes), dtype=float)
            # Find corresponding and non-corresponding events for the regressor
            corrEvent = np.where(eventCodes.code == compVar[1])[0]
            #nonEvent = np.where(eventCodes.code != compVar[1])[0]
            # Assign parametric regressor at correct event
            pMod[corrEvent] = modRegress[compVar[0]]
            # Append to design matrix
            pModDF[compVar[0]] = pMod
            # Append block ID to matrix
            pModDF['blockID'] = np.ones(len(eventCodes),dtype=int) * blockIdx
            # Store non-events for mean-centering
            eventIndices[compVar[0]] = corrEvent

        # Join computational variables into regressors
        for regIdx, reg in enumerate(designRegressors.items()):
            currVar = reg[1]
            if reg[0] != 'covar':
                if len(currVar) > 1:
                    # Add joint variables together to make regressor
                    jointReg = np.add(pModDF[currVar[0]], pModDF[currVar[1]])
                    # Compute mean of new regressors
                    jointReg_mean = np.nanmean(modRegress[[currVar[0],currVar[1]]])
                    # Populate non-corresponding events with the mean
                    jointEventIdx = np.append(eventIndices[currVar[0]],eventIndices[currVar[1]])
                    jointReg[[x for x in np.arange(len(jointReg)) if not x in jointEventIdx]] = jointReg_mean
                    # Define regressor label
                    jointReg_label = '-'.join(currVar)
                    # Append to design matrix
                    designMat[jointReg_label] = jointReg
                else:
                    # Specify regressor
                    singleReg = pModDF[currVar[0]]
                    # Compute mean of regressor
                    singleReg_mean =  np.nanmean(modRegress[currVar[0]])
                    # Populate non-corresponding events with the mean
                    eventIdx = eventIndices[currVar[0]]
                    singleReg[[x for x in np.arange(len(singleReg)) if not x in eventIdx]] = singleReg_mean
                    # Append to design matrix
                    designMat[currVar[0]]  = singleReg
        # Copy over covariates and blockID into design matrix
        designMat[designRegressors['covar']] = pModDF[designRegressors['covar']]
        designMat['blockID'] = pModDF['blockID']

        # Round small floating points to zeros
        designMat = designMat.round(decimals=5)

        # Concatenate across blocks
        concat_designMat.append(designMat)
        concat_modRegress.append(modRegress)
    sub_designMat = pd.concat(concat_designMat, axis=0)
    sub_modRegress = pd.concat(concat_modRegress, axis=0)

    # Save this subject's design for GLM
    sub_designMat.to_csv(f'{subOutDir}/patient{subID}_GLM_design.csv', sep=',', index=False)
    # Save trial-wise comptuational variable values for temporal model
    sub_modRegress.to_csv(f'{subOutDir}/patient{subID}_fulltrial_design.csv', sep=',', index=True, index_label='TrialNo')
