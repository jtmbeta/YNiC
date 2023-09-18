#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 13:49:24 2022

@author: jtm545

Script to run the *first* level fsl analysis for each R-number and functional 
run. Uses the featsetup file (.fsf) for a single subject/functional run and
then replaces the relevant information so that all the file paths are correct
for the case in question. Finally, it uses the 'clusterFeat' YNiC utility to 
send all jobs to run simultaneously on the cluster. To check that it has worked 
properly, type qstat in a terminal and there should be a list of jobs. 
Alternatively, click on the YNiC cluster monitor and there should be a green 
square for every job that was submitted. The full analysis (registration and 
stats) can take a few hours to run but if only running stats it shyouldn't take
too long.

21/07/2023 (JTM) - We want to re-run the analysis without using BET on the fMRI 
images in case it is removing areas of the brain that we are interested in, so
I have added a few global options at the top of the script to allow this. Much
easier than manually modifying the fsf files. 

"""

import os
import os.path as op
import re

# FEAT options
# Some useful top-level options to include are B0 unwarping, BET, analysis
# level, etc.

# Whether to run BET on fMRI data
FMRI_BET = 1
# Escape braclets!


# Set to False to run the full analysis, including registration
ONLYSTATS = True

# FEAT options
# If running an analysis with different options, add the following suffix
# to the feat directory so you can keep track
OUT_DIR_SUFFIX = ''  # Append this to the name of the feat dir


# Save the temporary design files here
FSFDIR = '/scratch/groups/Projects/P1470/fsl/fsfs'
if not op.exists(FSFDIR):
    os.mkdir(FSFDIR)

# Get participant Rnumbers
with open('../RNUMBERS.txt', 'r') as f:
    RNUMBERS = f.read().splitlines()

# Override
#RNUMBERS = ['R6273', 'R6281', 'R4176']

# The four functional runs
FUNCTIONALRUN = ['1', '2', '3', '4']

# Loop over rnumbers.
for rnum in RNUMBERS:
    # Rnumbers with fieldmaps can include B0 unwarping
    if ONLYSTATS:  # But not when only running stats
        LMS_DESIGN_FILE = '/scratch/groups/Projects/P1470/fsl/featsetup/R3154_level_1_LMS_stats.fsf'
        MEL_DESIGN_FILE = '/scratch/groups/Projects/P1470/fsl/featsetup/R3154_level_1_MEL_stats.fsf' 
    else:
        LMS_DESIGN_FILE = '/scratch/groups/Projects/P1470/fsl/featsetup/R3154_level_1_LMS_B0.fsf'
        MEL_DESIGN_FILE = '/scratch/groups/Projects/P1470/fsl/featsetup/R3154_level_1_MEL_B0.fsf' 
    
    # R-numbers without fieldmaps can not include B0 unwarping
    if rnum in ['R6273', 'R6281', 'R4176'] and not ONLYSTATS:
        LMS_DESIGN_FILE = '/scratch/groups/Projects/P1470/fsl/featsetup/R3154_level_1_LMS_no_B0.fsf'
        MEL_DESIGN_FILE = '/scratch/groups/Projects/P1470/fsl/featsetup/R3154_level_1_MEL_no_B0.fsf' 
    
    # Loop over functional runs.
    for frun in FUNCTIONALRUN:
        
        # The first two functional runs were always the LMS blocks so we need
        # to select the LMS featsetup file.
        if frun in ['1', '2']:
            print(f'{rnum}, Block {frun}, Lms')
            design_file = LMS_DESIGN_FILE
            
        # The second two scans were melanopsin so here we select the MEL
        # featsetup file.
        elif frun in ['3', '4']:
            print(f'{rnum}, Block {frun}, Mel')
            design_file = MEL_DESIGN_FILE
            
        # Load contents of the featsetup file so we can change the bits that
        # we need to.
        with open(design_file, 'r') as f:
            content = f.read()
            
        # Substitute R number using regular expression. The re.M flag simply
        # ensures that the search and substitution is applied to every line 
        # (so we get all of the R-numbers, wherever they may be).
        content_new = re.sub('R\d\d\d\d', rnum, content, flags=re.M)
        
        # Substitute fMRI run number. This is essentially the same as above
        # only with a different search pattern that targets the number 
        # identifying the functional run.
        content_new = re.sub('FMRI_\d', 'FMRI_' + frun, content_new, flags=re.M)
        
        # Substitute event file block number
        content_new = re.sub('block\d', 'block' + frun, content_new, flags=re.M)
        
        # -------------------- Set top level Feat options ------------------- #
        
        
        # Whether to run BET on fMRI data
        content_new = re.sub(
                    'set\sfmri\(bet_yn\)\s\d', 
                    f'set fmri(bet_yn) {FMRI_BET}', 
                    content_new, flags=re.M
                    )
                
        # Append a suffix to the output directory if required
        if OUT_DIR_SUFFIX:
            content_new = re.sub(
                    'featout/R\d\d\d\d_FMRI_\d',
                    "featout/{}_FMRI_{}{}".format(rnum, frun, OUT_DIR_SUFFIX), 
                    content_new, flags=re.M
                    )

        # Set
        #if not FMRI_BET:
        #    content_new = content_new.replace('set fmri(bet_yn) 1', 'set fmri(bet_yn) 0')
        
        # Write out new fsf file
        fname = op.join(FSFDIR, f'tmp_{rnum}_{frun}.fsf')
        with open(fname, 'w') as f:
            f.write(content_new)                     
        
        # Submit job to cluster                    
        cmd = 'clusterFeat {}'.format(fname)
        print('Running: ', cmd)
        os.system(cmd)
            


    
