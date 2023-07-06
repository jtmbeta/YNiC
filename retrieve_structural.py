#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 09:45:50 2023

@author: jtm545
"""

import sys
import os
import os.path as op
import pathlib
import errno
import glob
import re
import json

import scipy.io as scipyio
import pandas as pd
import numpy as np

  
# R numbers
with open('./RNUMBERS.txt', 'r') as f:
    RNUMBERS = f.read().splitlines()
    
# YNiC project ID
PROJECT = 'P1470'

# Image file extension
EXT = '.nii.gz'

# Override
RNUMBERS = ['R6152', 'R4176']


#%% A useful function
    
def force_symlink(file, target):
    """Force overwrite if symlink target file already exists.
    
    Args:
        file (str): Full path to file that will be symlinked.
        target (str): Full path to new symlink.

    Returns:
        None
    """
    try:
        os.symlink(file, target)
    except OSError as e:
        if e.errno == errno.EEXIST:
            os.remove(target)
            os.symlink(file, target)
    finally:
        print('{} --> {}'.format(file, target))
    return None


def sort_structural(f):
    '''Sort the structural files so we can select the highest number'''
    num = int(re.findall(r'\d+(?=_T1)', f)[0])
    return num
    
           
#%% Retrieve structural and run the brain extraction tool
structural_dir = '/scratch/groups/Projects/P1470/fsl/structural'
if not op.exists(structural_dir):
    os.mkdir(structural_dir)

print("--------- Structural ---------")

for rnum in RNUMBERS:
    
    # These if statements find the most recent structural image for the subject
    if rnum == 'R4197':
        pattern = '/mnt/siemensdata/{}/*P1459/*.nii.gz'.format(rnum)
    elif rnum == 'R3154':
        pattern = '/mnt/siemensdata/{}/*P1459/*.nii.gz'.format(rnum)
    elif rnum == 'R4482':
        pattern = '/mnt/siemensdata/{}/*P1382/*.nii.gz'.format(rnum)
    elif rnum == 'R6095':
        pattern = '/mnt/siemensdata/{}/*P1466/*.nii.gz'.format(rnum)
    elif rnum == 'R6101':
        pattern = '/mnt/siemensdata/{}/*P1467/*.nii.gz'.format(rnum)
    elif rnum == 'R6152':
        pattern = '/mnt/siemensdata/{}/*P1459/*.nii.gz'.format(rnum)
    elif rnum == 'R4176':
        pattern = '/mnt/siemensdata/{}/*P1322/*.nii.gz'.format(rnum)
    else:
        pattern = '/mnt/siemensdata/{}/*{}/*.nii.gz'.format(rnum, PROJECT)
        
    files = [f for f in glob.glob(pattern)]
    struct = [f for f in files if 'T1' in f]
    struct.sort(key=sort_structural)
    f = struct[-1]
    target = '{o}/{r}_T1.nii.gz'.format(o=structural_dir, r=rnum)
    force_symlink(f, target)
    
    # Run BET with default params (for now) on T1 structural image
    bet_output = target.replace(EXT, '') + '_brain' + EXT
    cmd = 'bet {} {}'.format(target, bet_output)
    print('!{}'.format(cmd))
    os.system(cmd)
        
