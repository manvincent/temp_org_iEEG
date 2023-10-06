#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 14:07:17 2019

@author: vman
"""

import mne
import numpy as np
import multiprocessing
num_cores = multiprocessing.cpu_count()
from scipy.stats import entropy  
from matplotlib import pyplot as plt
  
class Preprocess(object):
    
    def __init__(self, data, events):
        """
            Creates a 'Preprocess' class that applies signal processing procedures on the data via its sub-functions.
            Functions applied on a given class instance will adjust in-place
            Args:
                data: the continuous/raw MNE-type data object
                events: a numpy array of event codes and indices (wrt task timeseries), in the MNE-compatible format (n_events * 3 array)
        """
        self.data = data
        self.events = events
            
        
    def downSample(self, high_cutoff): 
        """
            Downsamples data to 2 x the highest frequency, given by the high_cutoff parameter
            (Nyquist theorem)
            Args:
                high_cutoff: the highest inteded frequency for analysis, also input into band(low)-pass filtering
        """
        self.data, self.events = self.data.resample((high_cutoff * 2)+1, npad='auto', events = self.events, n_jobs=num_cores)
        return
           

    def trimNonTask(self, taskStart_code, taskEnd_code, trialStart_code, trialEnd_code, timings):
        """
            Subsets the continuous data to include only the task segment
            Args: 
                taskStart_code: the event/trigger code corresponding to the start of the task
                taskEnd_code: the event/trigger code corresponding to the end of the task
                timings: an array of real timings (in seconds) corresponding to all events
        """
        # Check that the timings array matches the MNE-compatible event structure 
        if (len(timings) != np.shape(self.events)[0]):
            raise Exception("Error! Number of times does not match number of events")
        
        # Find the real times corresponding to the task start and task end event codes
        # Check if there is a taskStart code in the recorded events
        if np.where(self.events[:,2] == taskStart_code)[0].size > 0:          
            startCode = taskStart_code
        else: 
            startCode = trialStart_code 
        taskStart_time = timings[np.where(self.events[:,2] == startCode)][0]
                    
        # Check if they finished the task
        if np.where(self.events[:,2] == taskEnd_code)[0].size > 0:
            endCode = taskEnd_code
        else: 
            endCode = trialEnd_code 
        taskEnd_time = timings[np.where(self.events[:,2] == endCode)][-1]
        
        # Crop the continuous data from task-start to task-end
        self.data.crop(tmin = taskStart_time, tmax = taskEnd_time) # Includes a few samples after task end (via rounding)
        
        # Adjust the mne-event structure so that the task start code corresponds to index 0 
        self.events[:,0] = self.events[:,0] - self.events[:,0][np.where(self.events[:,2] == startCode)][0]
        
        # Adjust the real-time array so that the task start index corresponds to 0.0 seconds
        timings = timings - taskStart_time
    
        return(timings)
        

    def cleanEvents(self, expEnd_code, guessResp_code, card1_code, timings):         
        # Remove non-task events in events and times
        remove_indices = np.where((self.events[:,0] < 0) | (self.events[:,2] == expEnd_code))[0]
        self.events = np.delete(self.events ,remove_indices, axis=0).astype(int)
        timings = np.delete(timings, remove_indices, axis=0)        

        # Find missing trials in the event codes
        guessIdx = np.where(self.events[:,2] == guessResp_code)[0]
        cardIdx = np.where(self.events[:,2] == card1_code)[0]        

        # Identified where there is a code for a guess but none for card1
        nanIdx = guessIdx[np.where([i+1 not in cardIdx for i in guessIdx])[0]]

        # Remove the guess RT, the guess onset, and trial start code
        nanIdx = np.concatenate([nanIdx, nanIdx-1, nanIdx-2])                                        
        self.events = np.delete(self.events, nanIdx, axis=0)
        timings = np.delete(timings, nanIdx, axis=0)

        return(timings)
        
              
        
    def bandpassFilter(self, low_cutoff, high_cutoff):
        """
            General-purpose bandpass filter (can do high/low/band pass together or separately)
            Args: 
                low_cutoff: the lowest frequency allowed (high-pass filtering)
                high_cutoff: the highest frequency allowed (low-pass filtering)
        """
        self.data.filter(l_freq = low_cutoff, h_freq = high_cutoff, n_jobs = num_cores, method="fir", fir_design="firwin")
        return


    def ICAclean(self, uniform_threshold):
        """
            Perform ICA-based denoising by looking for uniformly (across-channel) distributed noise sources 
            For each IC, computes the KL divergence of the distribution over channels from a uniform distribution 
            Args: 
                uniform_threshold: The KL-divergence value against which bad ICs will be compared. ICs with KL-d values lower than the threshold will be discarded
        """
        ## Perform ICA on the channels
        # Initialize ICA parameters
        num_chans = self.data.info['nchan']
        num_ICs = num_chans
        ICA_object = mne.preprocessing.ICA(n_components = num_ICs, method = 'fastica', random_state=89)
        # Compute ICA on the continuous channel timeseries
        ICA_object.fit(self.data)
        # Extract the (absolute value) weight matrix (i.e. ICA topomap for components) (n_channels, n_components)
        weight_matrix = np.abs(ICA_object.get_components())
        
        # Compute the KL divergence for each IC (distributed over channels)
        kl_divergence = np.empty(num_ICs, dtype=float)
        for ic in np.arange(num_ICs):
            ic_uniform = np.repeat(np.mean(weight_matrix[:,ic]),num_chans)
            kl_divergence[ic] = entropy(weight_matrix[:,ic],ic_uniform)

       
        # Identify the noise components 
        ICA_object.exclude = []
        # Find index of bad component
        badComp_index = np.where(kl_divergence < uniform_threshold)[0]
        # Add to the list of bad components for this ICA object
        ICA_object.exclude.extend(badComp_index)
        # Delete bad component from data
        ICA_object.apply(self.data)
        
        ## Plot for QC
        # Specify bad components by plot color
        colors = np.repeat('g',num_ICs)
        colors[badComp_index] = 'r'

        # Create a plot of the ICA-artifact label results
        fig, (ax0, ax1) = plt.subplots(1,2)
        im = ax0.imshow(weight_matrix,cmap='jet')
        fig.colorbar(im,ax=ax0)
        ax0.set_title('ICA matrix (n_chan, n_comp)')
        ax1.bar(x=np.arange(num_ICs), height=kl_divergence, color=colors.tolist());
        ax1.axhline(y=uniform_threshold,xmin=0,xmax=num_ICs, color='black', linewidth=5)
        ax1.set_title("KL Divergence from uniform")
        fig.tight_layout()
        return(fig)
        
def referenceChans(mne_raw, refChans):
    """
        Reference the channels to the specified 'refChans' input. 
        Whether refChans refers to the mean across all channels or a specific subset, is specified at the higher layer
        Args: 
            refChans: a list of strings denoting the channel labels that will serve as reference
    """
    mne_raw.set_eeg_reference(ref_channels = refChans)
    return(mne_raw)

def referenceBipolar(mne_raw, anodes, cathodes):
    """
        Bipolar electrode referencing, taking adjacent channels as 'anodes' and 'cathodes'. 
        Returns n_chan/2 signals, for each depth electrode
        Args: 
            anode: a list of strings denoting the channel labels that will serve as 'anodes'
            cathode: a list of strings denoting the channel labels that will serve as 'cathodes'
    """
    mne.set_bipolar_reference(mne_raw, anodes, cathodes, copy=False)
    return(mne_raw)

def referenceNone(mne_raw):
    """
        Explicit set no re-referencing
        """
    mne_raw.set_eeg_reference(ref_channels = [])
    return(mne_raw)

    
 
            
            