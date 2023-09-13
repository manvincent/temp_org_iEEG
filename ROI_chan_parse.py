
import numpy as np
import pandas as pd
import os

homeDir =  '/media/Data/Projects/iowa_lfp'
os.chdir(f'{homeDir}/Analysis/Code')
from functions import *
from functions_stats import *

# Specify where to output channel info
datDir =  'path to preprocessed or epoched data'
chanDir = 'path to output directory e.g. ./Chan_Info'
if not os.path.exists(chanDir):
    os.makedirs(chanDir)

# Specify where template/atlas data are
anatDir = 'path to directory holding template images' 
coordPath = 'path to directory containing contact coordinate csv files' 
cortMask = 'path to cortical ROI atlas (should be in same space as template e.g. CIT 0.7mm)' 
subcortMask = 'path to subcortical ROI atlas'

## Specify subjects and blocks
subList = np.unique([i.split('_')[1] for i in next(os.walk(datDir))[1]])

# Some subIDs are repeated because they have multiple blocks of data
blockList = 'block IDs for each subject' 

# Specify ROIs of interest
ROIlist = ['Frontal Pole',
           'Subcallosal Cortex',
           'Frontal Orbital Cortex',
           'Cingulate Gyrus',
           'Supramarginal Gyrus',
           'Angular Gyrus',
           'Putamen',
           'Hippocampus',
           'Amygdala',
           'Anterior Insular Cortex',
           'Posterior Insular Cortex']

for subIdx, subID in enumerate(subList):
    
    # Load in subject's channel info
    bipolarPath = 'path to dataframe (csv) containing bipolar channel coordinates' # Should contain x,y,z values in the same space as template and atlases (e.g. CIT 0.7mm)
    bipolarChanDF = pd.read_csv(bipolarPath).sort_values('Contact').reset_index(drop=True)
    # Drop white matter channels
    WM_chanIdx = np.where(bipolarChanDF.GM == 0)[0]
    bipolarChanDF.drop(WM_chanIdx,inplace=True)
    bipolarChanDF = bipolarChanDF.reset_index(drop=True)

    # Specify directory to output the channel coordinates dataframes for ROIs
    roiDir = f'{chanDir}/patient_{subID}'
    if not os.path.exists(roiDir):
        os.makedirs(roiDir)

    # Create ROI dataframe from input data (x,y,z coordinates)
    cort_xml = f'{anatDir}/HarvardOxford-Cortical.xml'
    subcort_xml = f'{anatDir}/HarvardOxford-Subcortical.xml'
    roiDF = create_ROI_mask(bipolarChanDF, cort_xml,
                            cortMask, subcort_xml, subcortMask, voxP_thresh=10)
    
     # Iterate over ROIs of interest and run stats
    for ROI in ROIlist:
        ROI_chanDF = bipolarChanDF.iloc[np.where(roiDF.filter(like = ROI) == 1)[0]]
        # Export ROI channel dataframe (for use in group GLM analysis)
        ROI_chanDF.to_csv(f'{roiDir}/patient{subID}_{ROI}_chanDF.csv',
                         sep=',', index=False)

