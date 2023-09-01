#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 16:30:29 2019

@author: vman
"""
import numpy as np
import pickle
import fnmatch




def save_obj(obj, name ):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name ):
    with open(name, 'rb') as f:
        return pickle.load(f)

def multi_filter(names, patterns):
    """Generator function which yields the names that match one or more of the patterns."""
    for name in names:
        if any(fnmatch.fnmatch(name, pattern) for pattern in patterns):
            yield name

def is_odd(num):
   return num % 2 != 0
