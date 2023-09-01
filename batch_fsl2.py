#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 13:49:24 2022

@author: jtm545

Script to run the *second* level fsl analysis for each R-number. The purpose of 
this analysis is to combine each subject's functional runs. The featsetup file
is therefore configured to run a fixed effects. The 'clusterFeat' YNiC utility 
is used to send all jobs to run simultaneously on the cluster (one for each 
subject). To check that it has worked properly, type qstat in a terminal and 
there should be a list of jobs. Alternatively, click on the YNiC cluster 
monitor and there should be a green square for every job that was submitted.
This analysis level shouldn't take longer than 20 minutes to run.

"""

import os
import os.path as op
import re


# This is the path to the featsetup file for the second level analysis
designfile = '/scratch/groups/Projects/P1470/fsl/featsetup/R3154_level_2.fsf'

# Save the temporary design files here
FSFDIR = '/scratch/groups/Projects/P1470/fsl/fsfs'
if not op.exists(FSFDIR):
    os.mkdir(FSFDIR)
    
# Get participant Rnumbers
with open('../RNUMBERS.txt', 'r') as f:
    RNUMBERS = f.read().splitlines()

# Override
#RNUMBERS = ['R6307']

# The four functional runs
FUNCTIONALRUN = ['1', '2', '3', '4']
    
# Loop over rnumbers.
for rnum in RNUMBERS:
    
    # Load the content of the featsetup file
    with open(designfile, 'r') as f:
        content = f.read()
        
        # Substitute R number using regular expression. The re.M flag simply 
        # ensures that the search and substitution is applied to every line 
        # (so we get all of the R-numbers, wherever they may be). This is all
        # we need to do for this analysis.
        content_new = re.sub('R\d\d\d\d', rnum, content, flags=re.M)

    # Write out new fsf file
    fname = op.join(FSFDIR, f'tmp_{rnum}_level_2.fsf')
    with open(fname, 'w') as f:
        f.write(content_new)                     

    # Submit job to cluster                    
    cmd = 'clusterFeat {}'.format(fname)
    print('Running: ', cmd)
    os.system(cmd)
            


    
