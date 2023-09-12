#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 21 18:33:38 2019

@author: vman
"""
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def computeRegressor(data):
    # Parse the data frame 
    data.loc[data.resp_Guess == -1, 'resp_Guess'] = np.nan
    data = data[np.isfinite(data['resp_Guess'])]
    reportEarn = data.reportEarnings
    reportAcc = (reportEarn == np.max(reportEarn)).astype(int)
    # Code the guess on each trial
    guessLeft = (data.respKey_Guess == 1).astype(int)
    guessLow = np.array(data.resp_Guess - 1, dtype=bool)
    card1 = np.array(data.cards_1)
    card1_certain = np.logical_or(card1 == np.min(card1),card1 == np.max(card1)).astype(int)
    numOtherCards = len(np.unique(card1))-1
    winMag = np.unique(np.abs(data.guessEarnings[np.isfinite(data.guessEarnings)]))
    
    ## Before first card is shown
    # P0 = E[P1], reward prediction 1: expected  value of P1, the expected outcome conditional on card 1
    P0 = np.zeros(len(card1)) # Mean between winning and losing  outcomes
    
    # Risk prediction for card 1 = E[(P1-P0)**2]: expected prediction error (squared) after card 1
    P1_risk = np.array([(1/5)*((1/9)**2 + (3/9)**2 + (5/9)**2 + (7/9)**2 + 1) for t in np.arange(len(card1))])
    # Another definition, but needs P1_rpe to be defined already
    # P1_risk = np.array([np.mean(np.unique((P1_rpe)**2)) for t in np.arange(len(card1))]) 
    
    ## After first card is shown
    # Compute number of winning cards given guess
    numCardsWin_guessLow = np.array([len(np.where(np.unique(card1) < card1[i])[0]) for i in np.arange(len(card1))])
    numCardsWin_guessHigh = np.array([len(np.where(np.unique(card1) > card1[i])[0]) for i in np.arange(len(card1))])
    numCardsWin = np.array([numCardsWin_guessLow[i] if (guessLow[i]) else numCardsWin_guessHigh[i] for i in np.arange(len(card1))])
    
    # P1 = E[P2 | card1], reward prediction 2: expected value of P2, the actual reward after card 2 is presented    
    P1 = np.array([(numCardsWin[i] - (numOtherCards-numCardsWin[i]))/numOtherCards for i in np.arange(len(card1))])
    
    # Compute the prediction error for reward prediction 1
    P1_rpe = P1-P0
    
    # Compute the observed risk (i.e. squared RPE)
    P1_obsvRisk = (P1_rpe)**2
    # Compute the risk prediction error
    P1_riskPE = P1_obsvRisk - P1_risk
    
    # Risk prediction for card 2 = E{(P2-P1)**2}
    P2_risk = np.array([(numCardsWin[i]/numOtherCards) * (1 - P1[i])**2 + ((numOtherCards-numCardsWin[i])/numOtherCards) * (-1 - P1[i])**2 for i in np.arange(len(card1))])
    
    ## After second card is shown
    # Compute the reward prediction error 
    P2 = data.guessEarnings / winMag
    P2_rpe = P2 - P1
    
    # Compute the observed risk 
    P2_obsvRisk = (P2_rpe)**2
    # Compute the risk prediction error
    P2_riskPE = P2_obsvRisk - P2_risk
    
    
    # Rescale the two risk prediction error variables (P1_riskPE and P2_riskPE) to be comparable to rpe (followign Preuschoff et al)
    # rescaled_riskPE = sign(riskPE) * sqrt(abs(riskPE))
    #P1_riskPE_rescaled = np.sign(P1_riskPE) * np.sqrt(np.abs(P1_riskPE))
    #P2_riskPE_rescaled = np.sign(P2_riskPE) * np.sqrt(np.abs(P2_riskPE))
    
    # Store model-based variables in pandas dataframe
    regressorDF = pd.DataFrame({'P0':P0,
                                'P1_risk':P1_risk,
                                'P1':P1,
                                'P1_rpe':P1_rpe,
                                'P1_obsvRisk': P1_obsvRisk,
                                'P1_riskPE':P1_riskPE,
                                'P2_risk':P2_risk,
                                'P2':P2,
                                'P2_rpe':P2_rpe,
                                'P2_obsvRisk':P2_obsvRisk,
                                'P2_riskPE':P2_riskPE,
                                })
    regressorDF = regressorDF - regressorDF.mean()
    # Add covariates (not mean-centered, binary) 
    regressorDF['card1'] = card1_certain
    regressorDF['reportAcc'] = reportAcc
    regressorDF['guessLeft'] = guessLeft
    regressorDF = regressorDF.reset_index(drop=True)
    
    
    # Compute correlation matrix between regressors
    #corrDF = regressorDF.drop(labels=['card1','reportAcc'],axis=1)
    corr = np.abs(np.round(regressorDF.corr(),2))
    # Generate a mask for the upper triangle
    mask = np.zeros_like(corr, dtype=np.bool)
    mask[np.triu_indices_from(mask)] = True
    # Plot correlation matrix
    fig, ax = plt.subplots()
    sns.heatmap(corr, annot=True, mask=mask, cmap='jet',
            xticklabels=corr.columns.values,
            yticklabels=corr.columns.values,
            ax = ax)
    ax.set_title("| Pearson's correlation |")
    return(regressorDF,fig)



    