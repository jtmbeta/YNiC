#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 11:54:04 2023

@author: jtm545
"""

import os
import os.path as op
import shutil


# Make directory for button responses 
buttonresps = '/scratch/groups/Projects/P1470/fsl/buttonresps'
if not op.exists(buttonresps):
    os.mkdir(buttonresps)

# Get participant Rnumbers
with open('../RNUMBERS.txt', 'r') as f:
    RNUMBERS = f.read().splitlines()
    
# Override
#RNUMBERS = ['R4176']

for rnum in RNUMBERS:
    
    for frun in ['1', '2', '3', '4']:
        
        # Get the responses
        src_fpath = '/groups/Projects/P1470/Subjects/{}/00{}/responses.csv'.format(rnum, frun)
        dst_fpath = '/scratch/groups/Projects/P1470/fsl/buttonresps/{}_00{}_buttons.csv'.format(rnum, frun)
        
        try:
            shutil.copy(src_fpath, dst_fpath)
        except IOError as io_err:
            os.makedirs(os.path.dirname(dst_fpath))    
            shutil.copy(src_fpath, dst_fpath)        

        # Get the events
        src_fpath = '/groups/Projects/P1470/Subjects/{}/00{}/events.csv'.format(rnum, frun)
        dst_fpath = '/scratch/groups/Projects/P1470/fsl/buttonresps/{}_00{}_events.csv'.format(rnum, frun)
        
        try:
            shutil.copy(src_fpath, dst_fpath)
        except IOError as io_err:
            os.makedirs(os.path.dirname(dst_fpath))    
            shutil.copy(src_fpath, dst_fpath)   
        
