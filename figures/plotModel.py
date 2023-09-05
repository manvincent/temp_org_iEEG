#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 24 14:38:08 2019

@author: vman
"""
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import rc
rc('font',**{'family':'sans-serif','sans-serif':['Arial']})
rc('text', usetex=False)

def plotModel():
    # Define internal function
    def minmax(x):
        return (x-np.nanmin(x))/(np.nanmax(x)-np.nanmin(x))
    # build model variables for plot
    card1 = np.arange(1,11,1)
    numOtherCards = len(np.unique(card1))-1
    ## Before first card is shown
    # P0 = E[P1], reward prediction 1: expected  value of P1, the expected outcome conditional on card 1
    P0 = np.zeros(len(card1)) # Mean between winning and losing  outcomes    
    # Risk prediction for card 1 = E[(P1-P0)**2]: expected prediction error (squared) after card 1
    P1_risk = np.array([(1/5)*((1/9)**2 + (3/9)**2 + (5/9)**2 + (7/9)**2 + 1) for t in np.arange(len(card1))])
    # Another definition, but needs P1_rpe to be defined already    
    ## After first card is shown
    # Compute number of winning cards given guess
    numCardsWin = np.array([len(np.where(np.unique(card1) < card1[i])[0]) for i in np.arange(len(card1))])
    # P1 = E[P2 | card1], reward prediction 2: expected value of P2, the actual reward after card 2 is presented    
    P1 = np.array([(numCardsWin[i] - (numOtherCards-numCardsWin[i]))/numOtherCards for i in np.arange(len(card1))])
    # Compute the prediction error for reward prediction 1
    P1_rpe = P1-P0
    # Compute the risk prediction error
    P1_riskPE = (P1_rpe)**2 - P1_risk
    # Risk prediction for card 2 = E{(P2-P1)**2}
    P2_risk = np.array([(numCardsWin[i]/numOtherCards) * (1 - P1[i])**2 + ((numOtherCards-numCardsWin[i])/numOtherCards) * (-1 - P1[i])**2 for i in np.arange(len(card1))])
    # Compute win/loss variables for plots
    P2_rpe_lose = np.repeat(-1,len(card1)) - P1
    P2_rpe_win = np.repeat(1,len(card1)) - P1
    P2_riskPE_win = (P2_rpe_win)**2 - P2_risk
    P2_riskPE_lose = (P2_rpe_lose)**2 - P2_risk
    # No prediction error if p(win) = 1 or 0, will defs guess correctly
    P2_rpe_lose[-1] = np.nan  
    P2_rpe_win[0] = np.nan 
    P2_riskPE_lose[-1] = np.nan
    P2_riskPE_win[0] = np.nan 
    
    #### Plottting ####
    
    fig, ax = plt.subplots(1,5, sharex=True, sharey=True, figsize=(12,3))
    fig.text(0.5, -0.1, 'Card 1', ha='center')
    # Expected value (at C1) and P0
    ax[0].plot(card1, P1, color="green", linewidth=3, label='EV')
    # ax[0].plot(card1, P0, color="green", linewidth=3, linestyle='--', label='P0')
    ax[0].legend(shadow=False)
    # Uncertainty at C1 
    ax[1].plot(card1, P1_riskPE, color="red", linewidth=3, label=r"$RiPE_{c1}$")
    # ax[1].plot(card1, P1_rpe**2, color="orange", linewidth=3, label=r"$O.Risk_{c1}$")
    ax[1].plot(card1, P1_risk, color="gold", linewidth=3, linestyle='--',label=r"$E.Risk_{c1}$")
    ax[1].legend(shadow=False)
    # RPE at C2 
    ax[2].plot(card1, P2_rpe_win, color="blue", linewidth=3, label=r"$RePE_{c2} | win$")
    ax[2].plot(card1, P2_rpe_lose, color="lightblue", linewidth=3, label=r"$RePE_{c2} | lose$")    
    ax[2].legend(shadow=False)
    # Uncertainty at C2 | win
    ax[3].plot(card1, P2_riskPE_win, color="red", linewidth=3, label=r"$RiPE_{c2} | win$")
    # ax[3].plot(card1, P2_rpe_win**2, color="orange", linewidth=3, label=r"$O.Risk_{c2} | win$")
    ax[3].plot(card1, P2_risk, color="gold", linewidth=3, linestyle='--',label=r"$E.Risk_{c2} | win$")
    ax[3].legend(shadow=False,loc='lower left')
    # Uncertainty at C2 | lose
    ax[4].plot(card1, P2_riskPE_lose, color="red", linewidth=3, label=r"$RiPE_{c2} | lose$")
    # ax[4].plot(card1, P2_rpe_lose**2, color="orange", linewidth=3, label=r"$O.Risk_{c2} | lose$")
    ax[4].plot(card1, P2_risk, color="gold", linewidth=3, linestyle='--',label=r"$ERisk_{c2}| lose$")
    ax[4].legend(shadow=False,loc='lower right')    
    return(fig)
