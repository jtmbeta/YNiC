#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 13:49:24 2022

Credit to Becky Lowndes for original automate_analysis.py script

Notes
  - R3154 is missing functional runs

@author: jtm545
"""

import getopt
import os
import os.path as op
import subprocess
import re


# The four functional runs
FUNCTIONALRUN = [str(i) for i in range(1, 5)]
#FUNCTIONALRUN = ['3']
# Set to False to run the full analysis, including registration
ONLYSTATS = False

if ONLYSTATS:
    LMS_DESIGN_FILE = '/scratch/groups/Projects/P1470/fsl/featsetup/R3154_level_1_LMS_stats.fsf'
    MEL_DESIGN_FILE = '/scratch/groups/Projects/P1470/fsl/featsetup/R3154_level_1_MEL_stats.fsf' 
else:
    LMS_DESIGN_FILE = '/scratch/groups/Projects/P1470/fsl/featsetup/R3154_level_1_LMS.fsf'
    MEL_DESIGN_FILE = '/scratch/groups/Projects/P1470/fsl/featsetup/R3154_level_1_MEL.fsf' 

# Save the temporary design files here
FSFDIR = '/scratch/groups/Projects/P1470/fsl/fsfs'
if not op.exists(FSFDIR):
    os.mkdir(FSFDIR)

# Get participant Rnumbers
with open('../RNUMBERS.txt', 'r') as f:
    RNUMBERS = f.read().splitlines()

# Override
RNUMBERS = ['R6269']

# Loop over rnumbers and functional runs
for rnum in RNUMBERS:
    for frun in FUNCTIONALRUN:
        # These are the LMS blocks
        if frun in ['1', '2']:
            print(f'{rnum}, Block {frun}, Lms')
            design_file = LMS_DESIGN_FILE
        # These are the melanopsin blocks
        elif frun in ['3', '4']:
            print(f'{rnum}, Block {frun}, Mel')
            design_file = MEL_DESIGN_FILE
            
        # Adjust analysis files
        with open(design_file, 'r') as f:
            content = f.read()
            
        # Substitute R number
        content_new = re.sub('R\d\d\d\d', rnum, content, flags=re.M)
        
        # Substitute fMRI run number
        content_new = re.sub('FMRI_\d', 'FMRI_' + frun, content_new, flags=re.M)
        
        # Substitute event file block number
        content_new = re.sub('block\d', 'block' + frun, content_new, flags=re.M)

        # Write out new fsf file
        fname = op.join(FSFDIR, f'tmp_{rnum}_{frun}.fsf')
        with open(fname, 'w') as f:
            f.write(content_new)                     
        
        # Submit job to cluster                    
        cmd = 'clusterFeat {}'.format(fname)
        print('Running: ', cmd)
        os.system(cmd)
            


    
