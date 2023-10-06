#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 23:34:16 2020

@author: vman
"""

import numpy as np
from copy import deepcopy as dcopy
from joblib import Parallel, delayed
import multiprocessing
num_cores = multiprocessing.cpu_count()
from mne.decoding import SlidingEstimator
from scipy.stats import sem
from skimage import measure
from sklearn.metrics import roc_auc_score, accuracy_score, mean_squared_error, make_scorer
from sklearn.base import TransformerMixin
from sklearn.preprocessing import StandardScaler, RobustScaler


def orthogonalize(orth_against_reg, orth_to_reg, curr_design):
    # Pull out subset of design with only reg to be orthogonalized against (gets shared variance)
    orth_against_design = curr_design[:, orth_against_reg]
    # Pull out subset of design with only reg to be orthogonalized (gets residual variance)
    orth_to_design = curr_design[:, orth_to_reg]

    # Orthogonalize regressors of interest given specified to/against indices
    slope = np.diagonal(np.linalg.lstsq(orth_against_design, orth_to_design, rcond=-1)[0])
    orth_to_design_ = orth_to_design - orth_against_design*slope

    # construct new matrix with orthogonalized regressors
    curr_design_orth = curr_design.copy()
    curr_design_orth[:, orth_to_reg] = orth_to_design_
    return(curr_design_orth)


class DecodeModel(object):
    def __init__(self, X_folds, y_folds, classifier, modelType = 'logistic', alpha_FWE = 0.05, num_perm = 1000, **kwargs):
        '''
        Creates a 'DecodeModel' class that implements permutation-based cross-validation.

        Parameters
        ----------
        features : array (n_trials, nd_features, n_time)
            The X matrix of decoding model..
        target : array (n_trials,)
            The binarized target (label) variable for classification.
        classifier : object
            The base estimator to fit on data (sklearn class)
        alpha_FWE : float, optional
            FWE for cluster-based m.c. permutation test. The default is 0.05.
        num_perm : int, optional
            Number of permutations for null distributions.
        
        Returns
        -------
        None.

        '''

        self.X_folds = X_folds
        self.y_folds = y_folds
        self.nfolds = X_folds.shape[0]
        self.n_time = self.X_folds[0,0].shape[-1]
        # Define score metric contingent on model type
        if modelType == 'logistic':
            self.score = 'roc_auc' 
        elif modelType == 'linear': 
            self.score = make_scorer(mean_squared_error)
    
        self.alpha_FWE = alpha_FWE
        self.num_perm = num_perm
        self.clf = classifier
      

    def CV_train(self, curr_input):
        '''
        Parameters
        ----------
        curr_input : array, shape (nfolds, 2) * (n_samples, nd_features, n_time)
            Input values (either the full feature matrix or a subset of features)
        modelType: 'string'
            'logistic' (default) or 'linear'
        score_metric : loss function, optional
            Can be string or sklearn.metrics function. The default is 'roc_auc'.

        Returns
        -------
        None.

        '''                    
        # Fit decoder across folds
        fold_decoders = np.empty(self.nfolds, dtype=object)
        for f in np.arange(self.nfolds):
            dims = len(curr_input[f,0].shape)
            if dims == 3:
                time_decod = SlidingEstimator(self.clf, n_jobs=num_cores, scoring=self.score, verbose=False)
                time_decod.fit(curr_input[f,0], self.y_folds[f,0])
                fold_decoders[f] = dcopy(time_decod)
            elif dims == 2:
                static_decod = self.clf
                static_decod.fit(curr_input[f,0], self.y_folds[f,0])
                fold_decoders[f] = dcopy(static_decod)
        self.fold_decod = fold_decoders
        return

    def CV_test(self, curr_input, curr_target):
        '''
        Parameters
        ----------
        curr_input : array, shape (nfolds, 2) * (n_samples, nd_features, n_time)
            Input values (either the full feature matrix or a subset of features)
        curr_target: array, shape (nfolds, 2) * (n_samples)
            Target values (either the data or shuffled version)

        Returns
        -------
        acc_mean : ndarray of shape (num_perms, n_time)
            Mean CV accuracy across folds
        acc_sem : ndarray of shampe (num_perms, n_time)
            Standard error of shape mean of CV accuracy across folds

        '''

        # Unpack fitted decoder across folds and score against current target
        acc_array = np.empty(self.nfolds, dtype=object)
        corr_array = np.empty(self.nfolds, dtype=object)
        dims = len(curr_input[0,0].shape)
        if dims == 3:
            for f in np.arange(self.nfolds):
                # Compute score
                acc_array[f] = self.fold_decod[f].score(curr_input[f,1], curr_target[f,1])
            fold_acc = np.vstack(acc_array)
            # If linear decoder, comptue correlation between y_test and y_pred
            if self.score != 'roc_auc':                            
                for f in np.arange(self.nfolds):
                    # Compute r(y_predict, y_test)
                    pred =  self.fold_decod[f].predict(curr_input[f,1])
                    corr_array[f] = np.apply_along_axis(lambda x: np.corrcoef(x, curr_target[f,1])[0, 1], axis=0, arr=pred)                
                fold_corr = np.vstack(corr_array)
                corr_mean = np.mean(fold_corr, axis=0)
                corr_sem = sem(fold_corr, axis = 0)                        
        elif dims == 2:
            for f in np.arange(self.nfolds):
                if self.score == 'roc_auc':
                    predict_target = self.fold_decod[f].predict_proba(curr_input[f,1])[:,1]
                    acc_array[f] = roc_auc_score(curr_target[f,1],
                                                      predict_target)
                elif self.score == 'acc':
                    predict_target = self.fold_decod[f].predict(curr_input[f,1])
                    acc_array[f] = accuracy_score(curr_target[f,1],
                                                      predict_target)                            
            fold_acc = acc_array.astype(float)

        # Compute mean and sem across folds
        acc_mean = np.mean(fold_acc, axis = 0)
        acc_sem = sem(fold_acc, axis = 0)
        
        return(acc_mean, acc_sem)


    def permute(self, perm):
        '''
        Shuffles the target vector and computes a permuted CV mean acc
        Parameters
        ----------
        perm : int
            permutation iteration

        Returns
        -------
        H0_perm_acc : ndarray of shape (num_perms, n_time)
            Mean CV accuracy for current permutation

        '''
        # Shuffle the target (y) vector
        target_shuffled = dcopy(self.y_folds)
        # For the training set 
        [np.random.shuffle(target_shuffled[i,0]) for i in np.arange(self.nfolds)]
        # For the test set
        [np.random.shuffle(target_shuffled[i,1]) for i in np.arange(self.nfolds)]
        # Re-train with shuffled labels 
        self.CV_train(self.X_folds, target_shuffled)
        # Re-compute the CV accuracy  with the shuffled design
        H0_perm_acc, _  = self.CV_test(self.X_folds, target_shuffled)                
        return(H0_perm_acc)


    def criticalValue(self, null, alpha):
        # Only interested in the upper tail (don't want < 0.5 accuracy)
        cutoff = alpha*100
        crit = np.nanpercentile(null, 100-(cutoff), axis = 0)
        return(crit)


    def permutationTest_cluster(self):
        """
            Performs nonparametric CV and m.c. cluster correction
            Permutation test computes the null distribution of cv accuracy on a random target vector,
            Corrects for multiple comparisons of clustered data (uses max CLUSTER of permuted null)
        """
        def maxClustChar(self, null_clust, null, crit):
            """
                Evalutes cluster characteristics across permutations (null_clust) and
                computes the max cluster according to [sum(abs(t-values))].
                Returns distribution of max clusters (null_maxClust)
            """
            null_maxClust = np.zeros((self.num_perm), dtype=float)
            for perm in np.arange(self.num_perm):
                clustList = np.unique(null_clust[perm,:])
                clustList = clustList[np.nonzero(clustList)]
                eff_clust_sumAcc = np.zeros(len(clustList), dtype=float)
                for clustIdx, clustID in enumerate(clustList):
                    clust_timepoints = np.where(null_clust[perm,:] == clustID)
                    eff_clust_sumAcc[clustIdx] = np.sum(np.abs(null[perm, clust_timepoints] - crit[clust_timepoints]))
                if eff_clust_sumAcc.size != 0:
                    null_maxClust[perm] = np.max(eff_clust_sumAcc)
            return null_maxClust


        def clustChar(clusters, stats, crit):
            """
                Computes cluster characteristics [sum(abs(t-values))] of a clusterised vector or matrix

            """
            clustList = np.unique(clusters[:])
            clustList = clustList[np.nonzero(clustList)]

            clust_sumAcc = np.zeros(len(clustList), dtype=float)
            for clustIdx, clustID in enumerate(clustList):
                clust_timepoints = np.where(clusters == clustID)
                clust_sumAcc[clustIdx] = np.sum(np.abs(stats[clust_timepoints] - crit[clust_timepoints]))
            return clust_sumAcc, clustList
        
        # Train model across folds
        self.CV_train(self.X_folds)

        # Permute for the null hypothesis
        H0_perm_acc = np.array(Parallel(n_jobs=num_cores)(delayed(self.permute)(perm) for perm in np.arange(self.num_perm)))

        # Determine the precluster threshold value according to permuted distribution respective to each (time) sample
        H0_upper_crit = self.criticalValue(H0_perm_acc, 0.05)

        # Apply threshold to binarize
        H0_bin = (H0_perm_acc > H0_upper_crit)
        # Determine cluster label
        H0_clust = np.array([measure.label(H0_bin[perm,:]) for perm in np.arange(self.num_perm)])
        # Extract max cluster statistic
        H0_maxClust = maxClustChar(self, H0_clust, H0_perm_acc, H0_upper_crit)
        # Compute corrected critical values for the coefficients
        maxClust_upper_crit = self.criticalValue(H0_maxClust, self.alpha_FWE)

        # Compute CV acc of real target
        acc, sem = self.CV_test(self.X_folds, self.y_folds)
        # Threshold real data
        acc_bin = (acc > H0_upper_crit)
        # Determine cluster labels
        acc_clust = measure.label(acc_bin)
        # Extract cluster statistic [sum(abs(t-values))]
        acc_clustChar, clustID = clustChar(acc_clust, acc, H0_upper_crit)

        # Create mask of significant clusters (clustChar > maxClust_upper_crit)
        acc_masked = np.ones(acc.shape, dtype = float) * 0.5
        clust_mask = clustID[np.where(acc_clustChar > maxClust_upper_crit)]
        acc_masked[np.where(np.in1d(acc_clust,clust_mask))] = acc[np.where(np.in1d(acc_clust,clust_mask))]

        return(acc, acc_masked, sem, H0_maxClust, maxClust_upper_crit, H0_upper_crit, H0_perm_acc)


    def compute_accuracy(self):
        # Train model across folds
        self.CV_train(self.X_folds)
        # Compute out-of-sample CV acc
        acc, sem = self.CV_test(self.X_folds, self.y_folds)
        return(acc, sem)
    
   
    def compute_CI_test(self, CI = 95, n_bootstrap = 500):
        # Unpack fitted decoder across folds and score against current target
        boot_acc_array = np.empty(self.nfolds, dtype=object)
        # Define CI bounds 
        upbnd = 100 - (100 - CI)/2
        lowbnd = 100 - upbnd 
        # Train model across folds
        self.CV_train(self.X_folds)
        
        for f in np.arange(self.nfolds):       
            idx = np.arange(self.y_folds[f,1].shape[0])
            boot_test_acc = [] 
            for b in np.arange(n_bootstrap):
                # Get bootstrap indices
                pred_idx = np.random.choice(idx, size=idx.shape[0], replace=True)
                # Index the y_test
                curr_target = self.y_folds[f,1][pred_idx]
                # Score according to bootstrapped y-test trials
                test_acc = self.fold_decod[f].score(self.X_folds[f,1][pred_idx,:,:], curr_target)
                boot_test_acc.append(test_acc)
            # Save object of bootstrapped accuracies per fold
            boot_distr = np.vstack(boot_test_acc)          
            boot_acc_array[f] = boot_distr
        
        # Stack the bootstrapped accuracies (n_folds x n_bootstraps x n_timepoints)
        boot_acc = np.stack(boot_acc_array)
        mean_folds = np.mean(boot_acc,axis=0)
        upper = np.percentile(mean_folds, upbnd, axis=0)
        lower = np.percentile(mean_folds, lowbnd, axis=0)
        return(boot_acc, mean_folds, upper, lower)
        
    def compute_CI_train(self, CI = 95, n_bootstrap = 500): 
        
        # Initialize containers for bootstrapped accuracies and CI (across folds)
        boot_acc_array = np.empty(self.nfolds, dtype=object)
        
        # Specify weight for pessimism correction and define CI bounds 
        weight = 1 - 1/np.e
        upbnd = 100 - (100 - CI)/2
        lowbnd = 100 - upbnd 
                                    
        # Iterative over folds 
        for f in np.arange(self.nfolds):       
            # Get indicies for random choice
            idx = np.arange(self.y_folds[f,0].shape[0])                
            # Iterate over bootstraps
            boot_test_acc = [] 
            for b in np.arange(n_bootstrap):
                
                # Get bootstrap indices for train and validation sets
                train_idx = np.random.choice(idx, size=idx.shape[0], replace=True)
                valid_idx = np.setdiff1d(idx, train_idx, assume_unique=False)
                
                # Create new train and validation sets 
                X_train, y_train = self.X_folds[f,0], self.y_folds[f,0]
                
                boot_train_X, boot_train_y = X_train[train_idx], y_train[train_idx]                
                boot_valid_X, boot_valid_y = X_train[valid_idx], y_train[valid_idx]
                
                # Re-train model in this bootstrap          
                time_decod = SlidingEstimator(self.clf, n_jobs=num_cores, scoring=self.score, verbose=False)
                time_decod.fit(boot_train_X, boot_train_y)
                
                # Score according to bootstrapped training trials
                valid_acc = time_decod.score(boot_valid_X, boot_valid_y) # out-of-bag
                train_acc = time_decod.score(X_train, y_train) # in-sample (resubstitution)
                
                # Compute weighted score of (in-sample) train and bootstrap validation acc
                boot_acc = weight * valid_acc + (1.0 - weight) * train_acc
                boot_test_acc.append(boot_acc)
                
            # Save object of bootstrapped accuracies per fold
            boot_distr = np.vstack(boot_test_acc)          
            boot_acc_array[f] = boot_distr
                        
        # Stack the bootstrapped accuracies (n_folds x n_bootstraps x n_timepoints)
        boot_acc = np.stack(boot_acc_array)
        mean_folds = np.mean(boot_acc,axis=0)
        upper = np.percentile(mean_folds, upbnd, axis=0)
        lower = np.percentile(mean_folds, lowbnd, axis=0)
        return(boot_acc, mean_folds, upper, lower)

    def feature_importance(self):
              
        total_features = self.X_folds[0,0].shape[1]
        # Iterate over features for leave-one-feature-out CV
        feature_acc = np.empty(total_features, dtype = object)
        for f in np.arange(total_features):
            # Create X feature input matrix with left-out feature
            left_out_X_folds = np.empty_like(self.X_folds)
            for i in np.arange(self.X_folds.shape[0]):
                for j in np.arange(self.X_folds.shape[1]):
                    left_out_X_folds[i,j] = np.delete(self.X_folds[i,j], f, axis=1)

            # Train model across folds
            self.CV_train(left_out_X_folds)
            
            # Compute left-out CV
            feature_acc[f], _ = self.CV_test(left_out_X_folds, self.y_folds)

        return feature_acc
    

# Modified from https://stackoverflow.com/questions/50125844/how-to-standard-scale-a-3d-matrix by Kilian Batzner
class NDScaler(TransformerMixin):
    def __init__(self, scalerType, **kwargs):
        if scalerType == 'StandardScaler':
            self._scaler = StandardScaler(copy=True, **kwargs)
        elif scalerType == 'RobustScaler':
            self._scaler = RobustScaler(copy=True, **kwargs)
        else:
            raise Exception('Scaler type improperly specified')
        self._orig_shape = None

    def fit(self, X, **kwargs):
        X = np.array(X)
        # Save the original shape to reshape the flattened X later
        # back to its original shape
        if len(X.shape) > 1:
            self._orig_shape = X.shape[1:]
        X = self._flatten(X)
        self._scaler.fit(X, **kwargs)
        return self

    def transform(self, X, **kwargs):
        X = np.array(X)
        X = self._flatten(X)
        X = self._scaler.transform(X, **kwargs)
        X = self._reshape(X)
        return X

    def _flatten(self, X):
        # Reshape X to <= 2 dimensions
        if len(X.shape) > 2:
            n_dims = np.prod(self._orig_shape)
            X = X.reshape(-1, n_dims)
        return X

    def _reshape(self, X):
        # Reshape X back to it's original shape
        if len(X.shape) >= 2:
            X = X.reshape(-1, *self._orig_shape)
        return X

