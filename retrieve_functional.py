#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 10:27:54 2023

@author: jtm545

Script to retrieve the functional data for each subject. The files are 
symlinked into the fmnri folder. 
"""

import os
import re
import os.path as op
import errno
import glob


#%%
# R numbers
with open('../RNUMBERS.txt', 'r') as f:
    RNUMBERS = f.read().splitlines()
    
# YNiC project ID
PROJECT = 'P1470'

# Image file extension
EXT = '.nii.gz'

# Override
#RNUMBERS = []

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


def func_sort(f):
    '''Sort list of fmri files.
    
    We want the ones with the highest numbers
    '''
    frun = int(re.findall(r'(?<=FMRI)\d+', f)[0])
    pre_num = int(re.findall(r'\d+(?=_FMRI)', f)[0])
    return [pre_num, frun]

#%% Retrieve fMRI
# Symlink all functional runs into a local directory. There may be some
# exceptions to be dealt with, such as multiple functional runs with the same
# name (e.g., when a block had to be restarted). These can be dealt with 
# on a per-R basis, or by selecting the files with the highest numbers. 

fmri_dir = '/scratch/groups/Projects/P1470/fsl/fmri'
if not op.exists(fmri_dir):
    os.mkdir(fmri_dir)
    

print("--------- Functional ---------")

    
for rnum in RNUMBERS:
    pattern = '/mnt/siemensdata/{}/*{}/*FMRI**.nii.gz'.format(rnum, PROJECT)
    fmri_files = glob.glob(pattern)
    fmri_files.sort(key=func_sort)
    print(fmri_files)
    
    # Sometimes there can be extra fMRI files that we don't need. These are
    # usually 'false starts' and can be recognised by having a smaller size.
    # We remove them here.
    if rnum=='R6269':
        fmri_files.remove('/mnt/siemensdata/R6269/20230601130701_P1470/7_FMRI3_XPQ124.nii.gz')
    
    for run, f in enumerate(fmri_files[-4:]):            
        #frun = re.search('(?<=FMRI)\d', f).group()
        target = '{o}/{r}_FMRI_{run}.nii.gz'.format(
                o=fmri_dir, r=rnum, run=run+1)
        force_symlink(f, target)
        