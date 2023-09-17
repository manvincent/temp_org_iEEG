#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 16 14:31:52 2022

Inferential statistic on behaviour in ephys group

@author: vman
"""

#%% Import modules 
from matplotlib import pyplot as plt
from matplotlib import rc
rc('font',**{'family':'sans-serif','sans-serif':['Arial']})
rc('text', usetex=False)
import scipy.stats as stats
from sklearn.preprocessing import minmax_scale
from pymer4.models import Lmer, Lm
from statsmodels.tsa.ar_model import AutoReg
import seaborn as sns
import numpy as np
import pandas as pd
import os

#%% Specify paths
homeDir = '/media/Data/Projects/iowa_lfp'

# Specify where the data are
datDir =  f'{homeDir}/Analysis/Behaviour'
# Specify output folder for data
outDir = f'{homeDir}/Analysis/Behaviour/Results'
if not os.path.exists(outDir):
    os.makedirs(outDir)

#%% Specify subjects and blocks
subList = np.array(['384','399','403','418','493','507','525','532','567','585'])
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

#%% Prepare data for stats
# Loop through subjects and blocks
group_reportAcc = []
group_timeAcc = []
groupData = []
groupData_L1 = []
groupData_L2 = []

for subIdx, subID in enumerate(subList):    
    subData = []
    subData_L1 = []
    subData_L2 = []
    for blockIdx in np.arange(len(blockList[subIdx])):
        blockID = blockList[subIdx][blockIdx]
        
        # Load in data
        blockData = pd.read_csv(f'{homeDir}/Analysis/Behaviour/patient{subID}_block{blockID}_behav.csv')
        blockData['subID'] = int(subID)      
        blockData['trialNo'] = np.arange(len(blockData))
        blockData['catTrial'] = pd.qcut(blockData.trialNo, 3, retbins = False, labels=['early','middle','late'])
        blockData = blockData.dropna(subset=['respKey_Guess','isCorrectReport'],axis=0)
        blockData['blockIdx'] = blockIdx
        
        # Encode stay vs switch
        prevGuess = np.roll(blockData.resp_Guess,1)
        blockData['switch'] = (blockData.resp_Guess != prevGuess).astype(int)
        
        # Recode guess choice and L/R
        blockData['guessLower'] = blockData.resp_Guess - 1
        blockData['guessLRight'] = blockData.respKey_Guess - 1
                        
        # Define prev trial variables 
        blockData['prevTrial_EV']= np.roll(blockData.p1,1)
        blockData['prevTrial_ERisk']= np.roll(blockData.riskP2,1)
        blockData['prevTrial_riskPE']= np.roll(blockData.peRiskP2,1)
        blockData['prevTrial_RPE']= np.roll(blockData.peP2,1)
        blockData['prevTrialOut_L1'] = np.roll(blockData.p2,1)        
        blockData_L1 = blockData.iloc[1:,:]
        
        # Define prev guess and keypress L/R 
        blockData['guessLower_L1'] = np.roll(blockData.guessLower, 1)
        blockData['guessLower_L2'] = np.roll(blockData.guessLower, 2)        
        blockData['guessLRight_L1'] = np.roll(blockData.guessLRight, 1)
        blockData['guessLRight_L2'] = np.roll(blockData.guessLRight, 2)        
        blockData_L2 = blockData.iloc[2:,:]

        # Append to subData
        subData.append(blockData)
        subData_L1.append(blockData_L1)
        subData_L2.append(blockData_L2)
    
    # Create subject dataframe
    subData = pd.concat(subData)
    subData_L1 = pd.concat(subData_L1)
    subData_L2 = pd.concat(subData_L2)
    
    # Append to group data
    groupData.append(subData)
    groupData_L1.append(subData_L1)
    groupData_L2.append(subData_L2)
    
    
    # Compute report accuracy
    isCorrectReport = subData.isCorrectReport
    perc_reportAcc = np.divide(np.nansum(isCorrectReport),len(isCorrectReport)) * 100
    group_reportAcc.append(perc_reportAcc)
        
    # Does report accuracy decrease over time
    group_tertAcc = np.empty(3,dtype=float)
    for tertIdx, tertile in enumerate(['early','middle','late']):
        tertData = subData[subData['catTrial'] == tertile]
        tertReport = tertData.isCorrectReport
        perc_reportTertAcc = np.divide(np.nansum(tertReport),len(tertReport)) * 100
        group_tertAcc[tertIdx] = perc_reportTertAcc
    group_timeAcc.append(group_tertAcc)        

# Create group DFs
groupData = pd.concat(groupData)
groupData_L1 = pd.concat(groupData_L1)
groupData_L2 = pd.concat(groupData_L2)
#%% Descriptive stats on group report acc
mean_acc = np.mean(group_reportAcc)
sd_acc = np.std(group_reportAcc)
sem_acc = stats.sem(group_reportAcc)

#%% Mixed effects model: (one-sample t-test against 0.5)
# Create vector for re-centered (against 0.5) DV
groupData['isCorrectReport_mc'] = groupData['isCorrectReport'] - 0.5
# Specify lme version of one-sample t-test
ephys_mod_chance = Lmer("isCorrectReport_mc ~ 1 + (1|subID) ", 
                        data=groupData, 
                        family='gaussian')
res = ephys_mod_chance.fit()
display(res)



#%% Plotting report accuracy 
fig, ax = plt.subplots(figsize=(3,3), dpi=500)
# Plot ephys group
ax.bar(x=0, height=mean_acc, 
          edgecolor='black', color='none', width=0.1, linewidth=3)
ax.errorbar(x=0, y = mean_acc, yerr=sem_acc , c='black')
ax.scatter(x=np.ones(len(group_reportAcc)) * 0.01, y=group_reportAcc, color='blue', s=8, alpha=0.5)

ax.set_xticks([]); 
ax.set_ylim([80,103])
ax.set_xlim([-0.1, 0.1])
ax.set_ylabel('Accuracy')

# fig.savefig('fig1_reportacc.svg')


#%% Wrangle dataframe of group accuracy across time 
group_timeAccDF = pd.melt(pd.DataFrame({'early':np.array([group_timeAcc[i][0] for i in np.arange(len(group_timeAcc))]),
                                'mid':np.array([group_timeAcc[i][1] for i in np.arange(len(group_timeAcc))]),
                                'late':np.array([group_timeAcc[i][2] for i in np.arange(len(group_timeAcc))])
                                }))
group_timeAccDF.columns = ['time','reportAcc']
    
#%% Mixed effects model: does trial number predict report accuracy
groupData['trialNo'] = minmax_scale(groupData['trialNo'] )
ephys_mod_time = Lmer("isCorrectReport ~ trialNo + (1+trialNo|subID)", 
                data=groupData, family='binomial')
ephys_time = ephys_mod_time.fit()
display(ephys_time)

#%% Plot Report accuracy across time
# Convert the 'time' column to a categorical data type with the desired order
group_timeAccDF['time'] = pd.Categorical(group_timeAccDF['time'], categories=['early', 'mid', 'late'], ordered=True)
# Group the data by the 'time' column
grouped = group_timeAccDF.groupby('time')
# Calculate the mean and standard deviation for each group of 'time'
time = grouped.time.first().values
means = grouped.reportAcc.mean().values
sems = grouped.reportAcc.sem().values

# Create the point plot
fig, ax = plt.subplots(figsize=(3,3), dpi=500)
# Plot the error bars
ax.errorbar(x=time, y=means, yerr=sems, fmt='o', c='blue')
ax.plot(time, means, c='blue')
ax.set_ylabel('Accuracy')
ax.set_xlabel('Period')
ax.legend().set_title('')
# fig.savefig('fig1_time_reportacc.svg')

#%% Mixed effects model: does previous trial comp. variables predict current trial choice
ephys_mod_guess = Lmer("guessLower ~ prevTrial_EV + prevTrial_RPE + prevTrial_ERisk + prevTrial_riskPE + (1+prevTrial_EV + prevTrial_RPE + prevTrial_ERisk + prevTrial_riskPE |subID)", 
                data=groupData_L1, family='binomial')
ephys_guess = ephys_mod_guess.fit()
display(ephys_guess)


#%% Plotting the guess model
# Create array of lower and upper CI
CI_array = np.array([ephys_guess.Estimate[1:].values - ephys_guess['2.5_ci'][1:].values,
                     ephys_guess['97.5_ci'][1:].values - ephys_guess.Estimate[1:].values])


fig, ax = plt.subplots(figsize=(3,2), dpi=500, sharey=True)
ax.scatter(x=np.arange(4)-0.2, y=ephys_guess.Estimate[1:].values, color='black')
ax.errorbar(x = np.arange(4)-0.2, y = ephys_guess.Estimate[1:].values,
            yerr = CI_array,
             ls='none', color='black')
ax.scatter(x = np.ones(ephys_mod_guess.fixef.shape[0]) * 0, y=ephys_mod_guess.fixef['prevTrial_EV'], color='blue', alpha=0.5)             
ax.scatter(x = np.ones(ephys_mod_guess.fixef.shape[0]), y=ephys_mod_guess.fixef['prevTrial_RPE'], color='blue', alpha=0.5 )             
ax.scatter(x = np.ones(ephys_mod_guess.fixef.shape[0]) * 2, y=ephys_mod_guess.fixef['prevTrial_ERisk'], color='blue', alpha=0.5 )             
ax.scatter(x = np.ones(ephys_mod_guess.fixef.shape[0]) * 3, y=ephys_mod_guess.fixef['prevTrial_riskPE'], color='blue', alpha=0.5 )             

ax.axhline(0,color='red',linestyle='--')
ax.set_xticks(np.arange(4))
ax.set_xticklabels(['EV','RePE','E.Risk',r'RiPE'],fontsize=10)
ax.set_ylabel('Coefficient (a.u.)')

# fig.savefig(f'{outDir}/fig1_guessmod_coef.svg')




#%% Mixed effects model: does previous outcome predict stay/switch
ephys_mod_switch = Lmer("switch ~ prevTrialOut_L1 + (1+prevTrialOut_L1|subID)", 
                data=groupData_L1, family='binomial')
ephys_switch = ephys_mod_switch.fit()
display(ephys_switch)

#%% Splitting switch/stay data
perSub_meanDF = groupData_L1.groupby(['subID', 'prevTrialOut_L1'], as_index=False).mean()
loss_DF = perSub_meanDF[perSub_meanDF.prevTrialOut_L1 == -1]
win_DF = perSub_meanDF[perSub_meanDF.prevTrialOut_L1 == 1]

#%% Plotting stay/switch as a function of previous outcome
fig, ax = plt.subplots(figsize=(3,3), dpi=500)
ax.bar(x=-0.1, height=np.mean(loss_DF.switch), 
          edgecolor='black', color='none', width=0.1, linewidth=3, label='loss')
ax.errorbar(x=-0.1, y = np.mean(loss_DF.switch), yerr=stats.sem(loss_DF.switch), c='black')
ax.scatter(x=np.ones(len(loss_DF)) * -0.09, y=loss_DF.switch, color='blue', s=8, alpha=0.5)
          
ax.bar(x=0, height=np.mean(win_DF.switch), 
          edgecolor='black', color='grey', width=0.1, linewidth=3, label='win')
ax.errorbar(x=0, y = np.mean(win_DF.switch), yerr=stats.sem(win_DF.switch), c='black')
ax.scatter(x=np.ones(len(win_DF)) * 0.01, y=win_DF.switch, color='blue', s=8, alpha=0.5)

ax.set_xticks([-0.1, 0]); 

ax.set_xticklabels(['loss','win'])
ax.yaxis.set_ticks(np.arange(0.4, 0.7, 0.05))
ax.set_xlim([-0.2, 0.1])
ax.set_ylim([0.4, 0.6])
ax.set_ylabel('P(switch)')
ax.set_xlabel('Previous outcome')

# fig.savefig('fig1_stayswitch.svg')

                  
#%% Mixed effects AR(2) model: effect on guess 
mod_guess = Lmer("guessLower ~ guessLower_L1 + guessLower_L2 + (1 + guessLower_L1 + guessLower_L2 |subID)", 
                data=groupData_L2, 
                family='binomial')
res_guess = mod_guess.fit()
display(res_guess)
# Format fixef into long-format for plotting 
mod_guess_fixef = mod_guess.fixef.iloc[:,1:]
mod_guess_fixef.columns = ['L1','L2']
mod_guess_long = pd.melt(mod_guess_fixef, id_vars=None, 
                      var_name='lag', 
                      value_name='coef')
mod_guess_long['mod'] = 'Guess'

#%% Plotting the guess AR model
# Create array of lower and upper CI
mod_guess_CI = np.array([res_guess.Estimate[1:].values - res_guess['2.5_ci'][1:].values,
                     res_guess['97.5_ci'][1:].values - res_guess.Estimate[1:].values])


fig, ax = plt.subplots(figsize=(2,2), dpi=500, sharey=True)
ax.scatter(x=np.arange(2)-0.2, y=res_guess.Estimate[1:].values, color='black')
ax.errorbar(x = np.arange(2)-0.2, y = res_guess.Estimate[1:].values,
            yerr = mod_guess_CI,
             ls='none', color='black')
ax.scatter(x = np.ones(mod_guess.fixef.shape[0]) * 0, y=mod_guess.fixef['guessLower_L1'], color='blue', alpha=0.5)             
ax.scatter(x = np.ones(mod_guess.fixef.shape[0]), y=mod_guess.fixef['guessLower_L2'], color='deepskyblue', alpha=0.5 )             

ax.axhline(0,color='red',linestyle='--')
ax.set_ylabel('Coefficient (a.u.)')
ax.set_xlabel('Guess')
ax.set_ylim([-0.6,0.6])
ax.set_xticks(np.arange(2))
ax.set_xticklabels(['L1','L2'],fontsize=10)
ax.yaxis.set_major_locator(plt.MaxNLocator(3))

fig.savefig(f'{outDir}/fig1_AR_guess.svg')

#%% Mixed effects AR(2) model: effect on L/R 
mod_LR = Lmer("guessLRight ~ guessLRight_L1 + guessLRight_L2 + (1 + guessLRight_L1 + guessLRight_L2 |subID)", 
                data=groupData_L2, 
                family='binomial')
res_LR = mod_LR.fit()
display(res_LR)
# Format fixef into long-format for plotting 
mod_LR_fixef = mod_LR.fixef.iloc[:,1:]
mod_LR_fixef.columns = ['L1','L2']
mod_LR_long = pd.melt(mod_LR_fixef, id_vars=None, 
                      var_name='lag', 
                      value_name='coef')
mod_LR_long['mod'] = 'LR'


#%% Plotting the guess AR model
# Create array of lower and upper CI
mod_LR_CI = np.array([res_LR.Estimate[1:].values - res_LR['2.5_ci'][1:].values,
                     res_LR['97.5_ci'][1:].values - res_LR.Estimate[1:].values])


fig, ax = plt.subplots(figsize=(2,2), dpi=500, sharey=True)
ax.scatter(x=np.arange(2)-0.2, y=res_LR.Estimate[1:].values, color='black')
ax.errorbar(x = np.arange(2)-0.2, y = res_LR.Estimate[1:].values,
            yerr = mod_guess_CI,
             ls='none', color='black')
ax.scatter(x = np.ones(mod_LR.fixef.shape[0]) * 0, y=mod_LR.fixef['guessLRight_L1'], color='blue', alpha=0.5)             
ax.scatter(x = np.ones(mod_LR.fixef.shape[0]), y=mod_LR.fixef['guessLRight_L2'], color='deepskyblue', alpha=0.5 )             

ax.axhline(0,color='red',linestyle='--')
ax.set_ylabel('Coefficient (a.u.)')
ax.set_xlabel('Left/Right')
ax.set_ylim([-1.5,1.5])
ax.set_xticks(np.arange(2))
ax.set_xticklabels(['L1','L2'],fontsize=10)

fig.savefig(f'{outDir}/fig1_AR_LR.svg')


# %%
'''
group_ar_guess_coef = np.empty((2,len(subList)), dtype=float)
group_ar_LR_coef = np.empty((2,len(subList)), dtype=float)

for subIdx, subID in enumerate(subList):    
    subData = []
    for blockIdx in np.arange(len(blockList[subIdx])):
        blockID = blockList[subIdx][blockIdx]
        
        # Load in data
        blockData = pd.read_csv(f'{homeDir}/Analysis/Behaviour/patient{subID}_block{blockID}_behav.csv')
        blockData['trialNo'] = np.arange(len(blockData))
        blockData['catTrial'] = pd.qcut(blockData.trialNo, 3, retbins = False, labels=['early','middle','late'])
        blockData = blockData.dropna(subset=['respKey_Guess','isCorrectReport'],axis=0)
        blockData['blockIdx'] = blockIdx
        
        # Encode stay vs switch
        prevGuess = np.roll(blockData.resp_Guess,1)
        blockData['switch'] = (blockData.resp_Guess != prevGuess).astype(int)
        
        # Append to subData
        subData.append(blockData)
    
    # Create subject dataframe
    subData = pd.concat(subData)
    subData['subID'] = subID
    
    # Auto-regressive (2) models
    # Previous guess
    mod_AR_guess = AutoReg(subData.resp_Guess, 2, old_names=False)
    ar_guess_res = mod_AR_guess.fit()
    group_ar_guess_coef[0,subIdx] = ar_guess_res.params[1]
    group_ar_guess_coef[1,subIdx] = ar_guess_res.params[2]
    

    # Previous left/right
    mod_AR_LR = AutoReg(subData.respKey_Guess, 2, old_names=False)
    ar_LR_res = mod_AR_LR.fit()
    group_ar_LR_coef[0,subIdx] = ar_LR_res.params[1]
    group_ar_LR_coef[1,subIdx] = ar_LR_res.params[2]
    
   
   
# Create dataframe for autoregressive results
ephys_AR_DF = pd.DataFrame(columns=['lag','mod','sample','coef'])
ephys_AR_DF['coef'] = np.concatenate([group_ar_guess_coef.flatten(), group_ar_LR_coef.flatten()])
ephys_AR_DF['sample'] = 'ephys'
ephys_AR_DF['mod'] = np.concatenate([np.tile('guess',len(subList)*2), np.tile('LR', len(subList)*2)])
ephys_AR_DF['lag'] = np.tile(np.concatenate([np.ones(len(subList)), np.ones(len(subList))*2]),2)

# Plot AR results 

fig, ax = plt.subplots(figsize=(3,2), dpi=500, sharey=True)
# Ephys AR results
sns.stripplot(x='mod',y='coef',hue = 'lag', palette= sns.color_palette(palette='Blues',n_colors=2), 
              alpha=0.8, size=6,
              data=ephys_AR_DF, dodge=0.15, jitter=False, ax=ax)
sns.pointplot(x='mod',y='coef',hue = 'lag', color='black',
              data=ephys_AR_DF, dodge=0.1, join=False, scale=.5, errwidth=0.8,
              ax=ax).legend_.remove()
ax.axhline(0,color='red',linestyle='--')
ax.set_ylabel('Coefficient')
ax.set_xlabel('ephys')

# fig.savefig('fig1_AR.svg')


'''