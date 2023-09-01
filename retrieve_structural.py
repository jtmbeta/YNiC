#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 09:45:50 2023

@author: jtm545

This script finds all of the structural images for a list of R-numbers and
symlinks them into the structural folder. It also runs the FSL brain extraction
tool on each structural image with default settings and saves the output in the 
same folder with the _brain.nii.gz suffix. If default brain extraction does not
yield good results, it should be done separately (-f and -g parameters can be)
played with to find optimal results.


"""

import os
import os.path as op
import errno
import glob
import re

  
# R numbers
with open('./RNUMBERS.txt', 'r') as f:
    RNUMBERS = f.read().splitlines()
    
# YNiC project ID
PROJECT = 'P1470'

# Image file extension
EXT = '.nii.gz'

# Override
RNUMBERS = ['R6307']

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
    # Use fancy regex 'lookahead' pattern to extract number in T1 filepath
    # (we want the highest number)
    num = int(re.findall(r'\d+(?=_T1)', f)[0])
    return num
    
           
#%% Retrieve structural and run the brain extraction tool
structural_dir = '/scratch/groups/Projects/P1470/fsl/structural'
if not op.exists(structural_dir):
    os.mkdir(structural_dir)

print("--------- Structural ---------")

# Loop over R-numbers
for rnum in RNUMBERS:
    
    # Most of the participants in P1470 have existing structural scans. These
    # if statements find the relevant stru ctural image from an alternative 
    # project directory.
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
    elif rnum == 'R5619':
        pattern = '/mnt/siemensdata/{}/*P1459/*.nii.gz'.format(rnum)
    elif rnum == 'R5621':
        pattern = '/mnt/siemensdata/{}/*P1353/*.nii.gz'.format(rnum)
    elif rnum == 'R6128':
        pattern = '/mnt/siemensdata/{}/*/*T1*.nii.gz'.format(rnum)
    elif rnum == 'R6307':
        pattern = '/mnt/siemensdata/{}/*/*T1*.nii.gz'.format(rnum)
    else:
        pattern = '/mnt/siemensdata/{}/*{}/*.nii.gz'.format(rnum, PROJECT)
    
    # List of matching files     
    files = [f for f in glob.glob(pattern)]
    
    # Filter the filelist (we only want T1)
    struct = [f for f in files if 'T1' in f]
    
    # Get the desired file
    struct.sort(key=sort_structural)
    f = struct[-1]
    
    # Create symlink
    target = '{o}/{r}_T1.nii.gz'.format(o=structural_dir, r=rnum)
    force_symlink(f, target)
    
    # Run BET with default params on T1 structural image
    bet_output = target.replace(EXT, '') + '_brain' + EXT
    cmd = 'bet {} {}'.format(target, bet_output)
    print('!{}'.format(cmd))
    os.system(cmd)
        
