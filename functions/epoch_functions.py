import pandas as pd
import mne
import numpy as np

class Epoch(object):

    def __init__(self, data):
        """
            Creates an 'Epoch' class that applies epoching and averaging functions on the contiuous data via its sub-functions.
            Functions applied on a given class instance will adjust in-place
            Args:
                data: the continuous preprocessed MNE-type data object
                event_id: a {key:value} dict of event labels {keys} and their corresponding codes {values}
        """
        self.data = data

    def epochData(self, mne_events, epoch_lock, tmin, tmax, **kwargs):
        """
            Epoch data and embed a stimulus channel in the mne data structure
            Args:
                mne_events: the corresponding external (np) events array
                epoch_lock: a {key:value} pair from event_id to set as t=0 for a set of epochs, or dict of these pairs
                tmin: the period before the event corresponding to t=0
                tmax: the period after the event corresponding to t=0
        """
        # Check to see if baseline normalisation will be performed
        if 'baseline_bool' in kwargs:
            baseline_bool = kwargs['baseline_bool']
        else:
            baseline_bool = False
        if baseline_bool:
            if 'baseline_tmin' in kwargs:
                baseline_tmin = kwargs['baseline_tmin']
            else:
                raise KeyError('Baseline tmin not specified ')
            if 'baseline_tmax' in kwargs:
                baseline_tmax = kwargs['baseline_tmax']
            else:
                raise KeyError('Baseline tmax not specified ')

        ## Epoching section
        # Combine the events into a stimulus channel
        if not ('STI' in self.data.info['ch_names']):
            stimChan_info = mne.create_info(['STI'], self.data.info['sfreq'], ['stim'])
            stim_data = np.zeros((1, len(self.data.times)))
            stim_data[0,mne_events[np.where(mne_events[:,0] >= 0),0].astype(int)] = mne_events[np.where(mne_events[:,0] >= 0),2]
            stim_raw = mne.io.RawArray(stim_data, stimChan_info)
            self.data.add_channels([stim_raw], force_update_info=True)

        # Specify colors and an event_id dictionary for the legend
        # Visualize events and save event figure
        event_fig = mne.viz.plot_events(mne_events, self.data.info['sfreq'], 0, event_id=epoch_lock, show=False)

        # Epoch the data
        epoching_events = mne.find_events(self.data, stim_channel = 'STI', initial_event=True, shortest_event=1)
        # N.B. the sample index for the 'events' array doesn't match the manual events indices,
        # because it compensates for data cropping. Use this (rather than manual events) for epoching, etc
        if not baseline_bool:
            epochedData = mne.Epochs(self.data, events=epoching_events, event_id=epoch_lock, tmin=tmin, tmax=tmax, baseline=None, preload=True, reject=None)
        else:
            epochedData = mne.Epochs(self.data, events=epoching_events, event_id=epoch_lock, tmin=tmin, tmax=tmax, baseline=(baseline_tmin, baseline_tmax), preload=True, reject=None)

        return(epochedData, event_fig)
