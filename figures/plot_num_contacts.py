

import numpy as np
import pandas as pd
homeDir =  'path to home folder'
chanDir = 'path to folder containing channel information (e.g. source data)'

# Specify ROIs of interest
ROIlist = ['Anterior Insular Cortex',
           'Posterior Insular Cortex',
           'Frontal Orbital Cortex',
           'Subcallosal Cortex',
           'Frontal Pole',
           'Putamen',
           'Hippocampus',
           'Amygdala',
           'Cingulate Gyrus',
           'Supramarginal Gyrus',
           'Angular Gyrus']

all_ROI_df = [] 
for ROI in ROIlist:
    ROI_chanDF = pd.read_csv('ROI-specific .csv from source data sheets')
    
    # Get relevant metrics
    numSubs = len(ROI_chanDF['Patient ID'].unique())
    numContacts = ROI_chanDF.shape[0]
    numL = len(ROI_chanDF[ROI_chanDF['Laterality'] == 'L'])
    numR = len(ROI_chanDF[ROI_chanDF['Laterality'] == 'R'])
    
    # Create new dataframe from these metrics
    ROI_df = pd.DataFrame({'ROI': [ROI_title],
                            '# Subs': [numSubs],
                            '# Contacts': [numContacts],
                            '# L': [numL],
                            '# R': [numR]})
    # Append to list of all ROI dataframes
    all_ROI_df.append(ROI_df)

# Concatenate all ROI dataframes
all_ROI_df = pd.concat(all_ROI_df)

# Get total number of contacts across ROIs
total_contacts = all_ROI_df['# Contacts'].sum()
print(f'Total number of contacts across all ROIs: {total_contacts}')

# Save to latex table
all_ROI_df.to_latex(f'{chanDir}/ROI_summary.tex', index=False)
    
    