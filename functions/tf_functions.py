# -*- coding: utf-8 -*-


import mne
import numpy as np

class TimeFrequency(object):

    def __init__(self, data):
        """
            Creates a 'TimeFrequency' class that applies TF decomposition procedures on the data via its sub-functions.
            Functions applied on a given class instance will adjust in-place
            Args:
                data: the result of a time frequency decomp via complex Morlet convolution
        """
        self.MNE_struct_trials = data
        self.complex = self.MNE_struct_trials._data

    def extractPower(self):
        """
            Computes power from the result of the complex Morlet convolution.
            Power = abs(complex) ** 2
                  = complex .* conj(complex)
            Keeps each trial/epoch separate.
        """

        self.TFR_power_trials = np.multiply(self.complex,np.conj(self.complex)).real
        return

    def extractPhase(self):
        """
            Computes phase from the result of the complex Morlet convolution.
            Phase = angle(complex)
            Keeps each trial/epoch separate.
        """
        self.TFR_phase_trials = np.angle(self.complex)
        return

    
