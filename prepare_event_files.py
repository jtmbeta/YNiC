#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 09:44:58 2023

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



#LOGFILE = True
#if LOGFILE:
#    if op.exists('logfile.txt'):
#        os.remove('logfile.txt')
#    sys.stdout = open('logfile.txt', 'w')
    
# R numbers
with open('../RNUMBERS.txt', 'r') as f:
    RNUMBERS = f.read().splitlines()

# Override
RNUMBERS = ['R6152', 'R4176']

# YNiC project ID
PROJECT = 'P1470'

# Image file extension
EXT = '.nii.gz'


# Melanopsin condition mapping
mel_conds = {
        'MonLMEL': 'MonHighMel',
        'MonRMEL': 'MonHighMel',
        'BinOff': 'BinLowMel',
        'BinMEL': 'BinHighMel'
        }

# LMS condition mapping
lms_conds = {
        'MonLLMS': 'MonHighLms',
        'MonRLMS': 'MonHighLms',
        'BinOff': 'BinLowLms',
        'BinLMS': 'BinHighLms'
        }


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


#%% Prepare EV files (onset, duration, weighting)
# This is experiment-specific stuff to extract the event info from the .mat
# files produced by the psyctoolbox script and turn them into three-column EV
# files for FSL.

# Results from the psychtoolbox script are saved here
exptdir = '/groups/Projects/P1470/Subjects'

# New folder for eventfiles if not already
eventfile_dir = '/scratch/groups/Projects/P1470/fsl/eventfiles'
if not op.exists(eventfile_dir):
    os.mkdir(eventfile_dir)

# Loop over R numbers
for rnum in RNUMBERS:
    
    # New folder for RNUMBER
    R_event_dir = op.join(eventfile_dir, rnum)
    if not op.exists(R_event_dir):
        os.mkdir(R_event_dir)
        
    # Get the info json, which contain the lighthub blocking time value
    with open(op.join(exptdir, rnum, 'rinfo.json')) as fh:
        rinfo = json.load(fh)
    
    # Process the times for each block
    for block in [1, 2, 3, 4]:
        
        df = pd.read_csv(op.join(exptdir, rnum, f'00{block}', 'events.csv'))
        
        # New condition codes
        df['Condition'] = ''
        
        # This is the time that the LightHub blocks the script before stimulus
        # presentation begins. Here, I am dividing it by two and adding to the
        # onset times, which should get us closer to the actual stimulus onset
        # times.
        try:
            delta = rinfo[f'00{block}'].get('LightHub_blocking_time') / 2
        except:
            delta = .5  # Sensible default in case of missing data
        
        # Add corrected onsets to DF
        df['Corrected_onset'] = df.Onset.add(delta)
        
        if df.Event.str.contains('MEL').any():
            df['Condition'] = df.Event.map(mel_conds)
        else:
            df['Condition'] = df.Event.map(lms_conds)
        
        # Just what we are interseted in for now
        stim_info = df.loc[~df.Condition.isna(), :]
             
        # Weights are set to 1 for fsl EV files
        stim_info['Weights'] = 1.0
        
        # Save EV file for each stimulus type
        out_dir = op.join(eventfile_dir, rnum)
        
        # Make event files
        for c in stim_info.Condition.unique():
            ev_fname = (
                    '{o}/{r}_conditions_block{b}_{con}.txt'
                    .format(o=out_dir, r=rnum, b=block, con=c)
                    )
            ev_cols = ['Corrected_onset', 'Duration', 'Weights']
            new = stim_info.loc[stim_info.Condition==c, ev_cols]
            np.savetxt(ev_fname, new.values, delimiter='\t')