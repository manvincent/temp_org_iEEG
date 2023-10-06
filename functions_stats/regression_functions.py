#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 09:55:10 2019

@author: vman
"""

from sklearn import linear_model                       
import numpy as np

class LinearRegression(linear_model.LinearRegression):
    """
    LinearRegression class after sklearn's, but calculate t-statistics for model coefficients (betas).
    Adapted from: https://gist.github.com/brentp/5355925
    Adapted for 3D data 
    """

    def __init__(self, fit_intercept=False):        
        super(LinearRegression, self)\
                .__init__(fit_intercept=False)

    def fit(self, X, y, n_jobs=1):
        self = super(LinearRegression, self).fit(X, y, n_jobs)

        sse = np.sum((self.predict(X) - y) ** 2, axis=0) / float(X.shape[0] - X.shape[1])
        if isinstance(sse, float): 
            self.se = np.array([np.sqrt(np.diagonal(sse * np.linalg.inv(np.dot(X.T, X))))])
        else: 
            self.se = np.array([np.sqrt(np.diagonal(sse[i] * np.linalg.inv(np.dot(X.T, X))))
                                                        for i in range(sse.shape[0])])

        self.t = self.coef_ / self.se
        
        return self


