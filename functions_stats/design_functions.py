#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 31 14:58:16 2020

@author: vman
"""

import numpy as np
from matplotlib import pyplot as plt

class Design(object):

    def __init__(self, designMat, designRegressors, **kwargs):
        """
            Creates a 'Design' class that initiates different design matrices for stats.
            Args:
                regressor: a pandas DF of pMod and onsets in 'long' format (with all trial events represented), from glm_subject_massUniv.py
        """
        self.designMat = designMat
        self.intercept = np.ones(len(self.designMat))
        # Pull out non-modulated onset regressors
        self.respAction = np.array(self.designMat.respAction)
        self.card1On = np.array(self.designMat.card1On)
        self.card2On = np.array(self.designMat.card2On)
        self.cardOn = np.array(self.designMat.cardOn)
        self.cardISI = np.array(self.designMat.cardISI)
        # Pull out pMod for covariates, yoked to respAction
        self.covar = np.array(designMat[designRegressors['covar']])
        if 'group_analysis' in kwargs:
            group_analysis = kwargs['group_analysis']
            if group_analysis:
                self.covar = np.column_stack([np.array(designMat[designRegressors['covar']]),
                                             np.array(designMat.filter(regex='sub'))])



    def fullModel(self):
        # Parse the appropriate regressor
        labels = ['intercept','nonMod_cardOn','nonMod_cardISI',
                  'EV','Outcome','RPE',
                  'Erisk','Orisk','riskPE',                  
                  'respAction','reportAcc']
        # Create design matrix
        design = np.column_stack([self.intercept, self.cardOn, self.cardISI,
                                  self.designMat['P1'], self.designMat['P2'], self.designMat['P2_rpe'],
                                  self.designMat['P1_risk-P2_risk'], self.designMat['P1_obsvRisk-P2_obsvRisk'], self.designMat['P1_riskPE-P2_riskPE'],
                                  self.respAction, self.covar])
        regressors_of_interest = np.zeros(design.shape[1], dtype=bool)
        regressors_of_interest[3:9] = 1
        # Define the regressors that others are orthogonalised against (i.e. the ones that claim colinear variance)
        orth_against_regressors = np.zeros_like(regressors_of_interest)
        orth_against_regressors[[4,7]] = 1
        # Define the regressors that are orthogonalized (i.e. get residual variance)
        orth_to_regressors = np.zeros_like(regressors_of_interest) 
        orth_to_regressors[[5,8]] = 1
        return(design, labels, regressors_of_interest, orth_against_regressors, orth_to_regressors)

class Design_singleEvent(object):

    def __init__(self, designMat, designRegressors, **kwargs):
        """
            Creates a 'Design' class that initiates different design matrices for stats.
            Args:
                regressor: a pandas DF of pMod and onsets in 'long' format (with all trial events represented), from glm_subject_massUniv.py
        """
        self.designMat = designMat
        self.intercept = np.ones(len(self.designMat))
        # Pull out non-modulated onset regressors
        self.respAction = np.array(self.designMat.respAction)
        self.card1On = np.array(self.designMat.card1On)
        self.card2On = np.array(self.designMat.card2On)
        self.cardOn = np.array(self.designMat.cardOn)
        self.cardISI = np.array(self.designMat.cardISI)
        # Pull out pMod for covariates, yoked to respAction
        self.covar = np.array(designMat[designRegressors['covar']])
        if 'group_analysis' in kwargs:
            group_analysis = kwargs['group_analysis']
            if group_analysis:
                self.covar = np.column_stack([np.array(designMat[designRegressors['covar']]),
                                             np.array(designMat.filter(regex='sub'))])



    def fullModel(self):
        # Parse the appropriate regressor
        labels = ['intercept','nonMod_cardOn','nonMod_cardISI',
                  'EV','Outcome','RPE',
                  'Erisk','Orisk','riskPE',                  
                  'respAction','reportAcc']
        # Create design matrix
        design = np.column_stack([self.intercept, self.cardOn, self.cardISI,
                                  self.designMat['P1'], self.designMat['P2'], self.designMat['P2_rpe'],
                                  self.designMat['P1_risk-P2_risk'], self.designMat['P2_obsvRisk'], self.designMat['P2_riskPE'],
                                  self.respAction, self.covar])
        regressors_of_interest = np.zeros(design.shape[1], dtype=bool)
        regressors_of_interest[3:9] = 1
        # Define the regressors that others are orthogonalised against (i.e. the ones that claim colinear variance)
        orth_against_regressors = np.zeros_like(regressors_of_interest)
        orth_against_regressors[[4,7]] = 1
        # Define the regressors that are orthogonalized (i.e. get residual variance)
        orth_to_regressors = np.zeros_like(regressors_of_interest) 
        orth_to_regressors[[5,8]] = 1
        return(design, labels, regressors_of_interest, orth_against_regressors, orth_to_regressors)
    