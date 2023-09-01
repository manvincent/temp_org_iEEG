#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 21 15:59:04 2020

@author: vman
"""




import numpy as np
import pandas as pd
import nilearn as nl
import nilearn.image as nlimg
import xml.etree.ElementTree as ET

        
def is_odd(num):
   return num % 2 != 0

    
class Channel(object):

    def __init__(self, data):
        """
            Creates a 'Channel' class that takes in a dataframe of channel coordinates and compute bipolar pairings and locations
            Functions applied on a given class instance will adjust in-place
            Args:
                data: pandas dataframe
        """
        self.data = data
                        
    def labelElect(self): 
        electID = np.zeros(len(self.data))
        e = 0 
        for i in np.arange(1, len(self.data)):
            if self.data.Number[i] == self.data.Number[i-1] + 1:
                electID[i] = e
            else: 
                e += 1
                electID[i] = e 
        self.data['electID'] = electID
        return
    
    
    def bipolarPairs(self): 
        data_bipolar = [] 
        for elect in np.unique(self.data.electID):
            electDF = self.data[self.data.electID == elect]
            if len(electDF) > 1: # Impossible to bipolar reference with a single electrode, so skip
                # Delete odd electrodes closest to the outside of the brain
                if is_odd(len(electDF)):
                    electDF = electDF.iloc[0:-1]
                electDF.reset_index(drop=True, inplace=True)
                # Label anode-cathode pairs
                electDF['isCathode'] = 1
                electDF['isCathode'][0::2] = 0        
                # Compute average coordinates 
                electDF_bipolar = electDF[:len(electDF)].groupby(electDF.index[:len(electDF)] // 2).mean()
                # Check that 'isCathode' value == 0.5 given dummy coding 
                if not (len(electDF_bipolar.isCathode.unique()) == 1 or electDF_bipolar.isCathode.unique()[0] == 0.5):
                     raise ValueError(f'Error for {subID} {elect}! Anode-Cathode incorrectly coded')
                # Delete columns: Number, Cathode, ElectID, Channel
                electDF_bipolar.drop(['Channel', 'Number', 'electID', 'isCathode'], axis=1, inplace=True)
                # Create new label from Contact ID 
                anode = (electDF_bipolar.Contact - 0.5).astype(int)
                cathode = (electDF_bipolar.Contact + 0.5).astype(int)
                electDF_bipolar['anode'] = anode
                electDF_bipolar['cathode'] = cathode            
                electDF_bipolar['label'] = anode.astype(str).str.cat(cathode.astype(str), sep = '-')
                # Append
                data_bipolar.append(electDF_bipolar)
        self.data_bipolar = pd.concat(data_bipolar)
        return
                              
    def convertCoord(self, template, chanType, template_label = 'CIT'): 
        if chanType == 'all': 
            currData = self.data
        elif chanType == 'bipolar':
            currData = self.data_bipolar
        # Extract and invert affine from template 
        niimg = nlimg.load_img(template) 
        invAffine = np.linalg.inv(niimg.affine)
        # Extract coordinates from data
        x_coord = np.array(currData.filter(like = template_label).filter(like = 'X').iloc[:,0])
        y_coord = np.array(currData.filter(like = template_label).filter(like = 'Y').iloc[:,0])
        z_coord = np.array(currData.filter(like = template_label).filter(like = 'Z').iloc[:,0])
        # Convert coordinates in template space to x,y,z (image-space)
        x,y,z = nlimg.coord_transform(x_coord,y_coord,z_coord, invAffine)
        # Assign to the relevant dataframe
        if chanType == 'all': 
            self.data = currData.assign(x=x.astype(int), y=y.astype(int), z=z.astype(int))       
        elif chanType == 'bipolar':
            self.data_bipolar = currData.assign(x=x.astype(int), y=y.astype(int), z=z.astype(int))            
        return
    
        
    def maskCoordinates(self, templateMask):
        niimg = nlimg.load_img(templateMask) 
        niimg_data = nlimg.get_data(niimg)
        coordinates = np.array(self.data.loc[:,['x','y','z']])
        self.data = self.data.assign(GM=[niimg_data[coordinates[i][0], coordinates[i][1], coordinates[i][2]] for i in np.arange(len(coordinates))])
        return 

    def maskGM(self): 
        include = np.zeros(len(self.data_bipolar),dtype=int)            
        # Mask out electrodes if both parents were in grey matter
        for ch in np.arange(len(self.data_bipolar)):
            anode = self.data_bipolar.anode.iloc[ch]
            cathode = self.data_bipolar.cathode.iloc[ch]
            if bool(int(self.data.GM.iloc[np.where(self.data.Contact == anode)])) or bool(int(self.data.GM.iloc[np.where(self.data.Contact == cathode)])):
                include[ch] = 1
        self.data_bipolar['GM'] = include
                
        # Delete electrodes not in grey matter 
        self.data_bipolar= self.data_bipolar[self.data_bipolar.GM == 1]
        return
            

def create_ROI_mask(dataframe, cort_xml, cortMask, subcort_xml, subcortMask, voxP_thresh):
    # Define coordinates 
    coordinates = np.array(dataframe.loc[:,['x','y','z']],dtype=int)
    
    # Initialize dataframe to store ROI flags
    roiDF = pd.DataFrame()
    # Iterate over cortical ROIs 
    cort_img = nlimg.load_img(cortMask)     
    ROI_cortical = ET.parse(cort_xml).getroot()
    for ROI in ROI_cortical[1]:
        ROI_idx = int(ROI.attrib['index'])
        ROI_label = ROI.text
        print(f'Idx: {ROI_idx} -- ROI: {ROI_label}')
        # Load in the correct volume
        niimg_data = int()
        niimg_data = nlimg.get_data(cort_img)[:,:,:,ROI_idx]
        # Assign voxel to ROI 
        roiDF[ROI_label] = [niimg_data[coordinates[i][0], coordinates[i][1], coordinates[i][2]] for i in np.arange(len(coordinates))]

    # Iterate over subcortical ROIs 
    subcort_img = nlimg.load_img(subcortMask)
    ROI_subcortical = ET.parse(subcort_xml).getroot()
    for ROI in ROI_subcortical[1]:
        ROI_idx = int(ROI.attrib['index'])
        ROI_label = ROI.text
        if not ("White Matter" in ROI_label or "Cortex" in ROI_label):
            print(f'Idx: {ROI_idx} -- ROI: {ROI_label}')
            # Load in the correct volume
            niimg_data = int()
            niimg_data = nlimg.get_data(subcort_img)[:,:,:,ROI_idx]
            # Assign voxel to ROI 
            roiDF[ROI_label] = [niimg_data[coordinates[i][0], coordinates[i][1], coordinates[i][2]] for i in np.arange(len(coordinates))]
        
    # Threshold according to voxP_thresh
    roiDF.where((roiDF > voxP_thresh), 0, inplace=True)
        
    # Binarize mask inclusion values if to below/above voxP_thresh and maxP
    for i in np.arange(len(roiDF)):
        # Each voxel can only be ascribed a one ROI (max probability)
        if np.max(roiDF.iloc[i,:]) != 0: 
            maxCol_idx = np.argmax(roiDF.iloc[i,:])
            roiDF.iloc[i,:] = 0
            roiDF.iloc[i,maxCol_idx] = 1
    return(roiDF)
