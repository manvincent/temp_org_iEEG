
import numpy as np
from copy import deepcopy as dcopy
from joblib import Parallel, delayed
import multiprocessing
num_cores = multiprocessing.cpu_count()
from scipy.stats import sem
from skimage import measure
from mne.decoding import GeneralizingEstimator
from sklearn.metrics import make_scorer


class DecodeModel_temporal_gen(object):
    def __init__(self, X_folds, y_folds, classifier, alpha_FWE = 0.05, num_perm = 1000, **kwargs):
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
        self.alpha_FWE = alpha_FWE
        self.num_perm = num_perm
        self.clf = classifier
        self.generalize_condition = False
        if 'generalize_condition' in kwargs:
            self.generalize_condition = kwargs['generalize_condition']
            self.X_folds_gen = kwargs['X_folds_gen']
            self.y_folds_gen = kwargs['y_folds_gen']


    def CV_train(self, curr_input, modelType, score_metric = 'roc_auc'):
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
        if not isinstance(score_metric, str):
            score_metric = make_scorer(score_metric)

        fold_decoders = np.empty(self.nfolds, dtype=object)
        for f in np.arange(self.nfolds):
            time_gen = GeneralizingEstimator(self.clf, n_jobs=num_cores-1, scoring=score_metric, verbose=False)
            time_gen.fit(curr_input[f,0], self.y_folds[f,0])
            fold_decoders[f] = dcopy(time_gen) 
        self.fold_decod = fold_decoders 
        return 

    def CV_test(self, curr_input, curr_target, score_metric = 'roc_auc'):
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
                    
        temp_gen_acc = np.ones((self.nfolds, self.n_time, self.n_time), dtype=float) * 0.5
        for f in np.arange(self.nfolds):            
            temp_gen_acc[f,:,:] = self.fold_decod[f].score(curr_input[f,1], curr_target[f,1])
        
        # Compute mean and sem across folds
        acc_mean = np.mean(temp_gen_acc, axis = 0)
        acc_sem = sem(temp_gen_acc, axis = 0)
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
        [np.random.shuffle(target_shuffled[i,0]) for i in np.arange(self.nfolds)]        
        [np.random.shuffle(target_shuffled[i,1]) for i in np.arange(self.nfolds)]
        
        if not self.generalize_condition:         
            curr_X = self.X_folds               
        elif self.generalize_condition:
            curr_X = self.X_folds_gen
        
        # Re-compute the CV accuracy  with the shuffled design
        H0_perm_acc, _  = self.CV_test(curr_X, target_shuffled)                    
        return(H0_perm_acc)


    def criticalValue(self, null, alpha):
        # Only interested in the upper tail (don't want < 0.5 accuracy)
        cutoff = alpha*100
        crit = np.nanpercentile(null, 100-(cutoff), axis = 0)
        return(crit)


    def permutationTest_cluster(self, modelType = 'logistic'):
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
                # Create list of unique clusters
                clustList = np.unique(null_clust[perm,:,:])
                clustList = clustList[np.nonzero(clustList)]                
                # Get cluster statistics for each cluster
                eff_clust_sumAcc = np.zeros(len(clustList), dtype=float)
                for clustIdx, clustID in enumerate(clustList):
                    clust_train, clust_test = np.where(null_clust[perm,:,:] == clustID)
                    eff_clust_sumAcc[clustIdx] = np.sum(np.abs(null[perm, clust_train, clust_test] - crit[clust_train, clust_test]))                
                # Get max cluster statistic across clusters, for this permutation
                if eff_clust_sumAcc.size != 0:
                    null_maxClust[perm] = np.max(eff_clust_sumAcc)                    
            return null_maxClust


        def clustChar(clusters, stats, crit):
            """
                Computes cluster characteristics [sum(abs(t-values))] of a clusterised vector or matrix

            """
            # Create list of unique clusters            
            clustList = np.unique(clusters[:,:])
            clustList = clustList[np.nonzero(clustList)]
            # Get cluster statistics for each cluster            
            clust_sumAcc = np.zeros(len(clustList), dtype=float)
            for clustIdx, clustID in enumerate(clustList):
                clust_train, clust_test = np.where(clusters == clustID)
                clust_sumAcc[clustIdx] = np.sum(np.abs(stats[clust_train, clust_test] - crit[clust_train, clust_test]))
            return clust_sumAcc, clustList



        # Train model across folds
        self.CV_train(self.X_folds, modelType)


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
        if not self.generalize_condition:
            acc, sem = self.CV_test(self.X_folds, self.y_folds)            
        elif self.generalize_condition:
            acc, sem = self.CV_test(self.X_folds_gen, self.y_folds_gen)
            
        # Threshold real data
        acc_bin = (acc > H0_upper_crit)
        # Determine cluster labels
        acc_clust = measure.label(acc_bin, connectivity = 2)
        # Extract cluster statistic [sum(abs(t-values))]
        acc_clustChar, clustID = clustChar(acc_clust, acc, H0_upper_crit)

        # Create mask of significant clusters (clustChar > maxClust_upper_crit)
        clust_mask = clustID[np.where(acc_clustChar > maxClust_upper_crit)]        
        acc_masked = np.zeros(acc.shape, dtype = float)
        for sig_clust in clust_mask:
            acc_masked[np.where(acc_clust == sig_clust)] = 1
        # Mask will be a binary mask (for contour plotting)
                
        return(acc, acc_masked, sem, H0_maxClust, maxClust_upper_crit, H0_upper_crit)

    def compute_accuracy(self, modelType = 'logistic'):
        # Train model across folds
        self.CV_train(self.X_folds, modelType)
        # Compute CV acc of real target
        if not self.generalize_condition:
            acc, sem = self.CV_test(self.X_folds, self.y_folds)            
        elif self.generalize_condition:
            acc, sem = self.CV_test(self.X_folds_gen, self.y_folds_gen)
        return(acc, sem)