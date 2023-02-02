#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 13:49:24 2022

Credit to Becky Lowndes for original automate_analysis.py script

Notes
  - R3154 is missing functional runs

@author: jtm545
"""

import os
import os.path as op
import subprocess
import re



# Get participant Rnumbers
with open('../jtm/RNUMBERS.txt', 'r') as f:
    RNUMBERS = f.read().splitlines()

FUNCTIONALRUN = [str(i) for i in range(1, 5)]

#DESIGN_FILE = '/scratch/groups/Projects/P1459/jtm/featsetup/R2268_level_1.fsf'
DESIGN_FILE = './featsetup/R2268_level_1_stats.fsf'

FSFDIR ='./fsfs/'


# For now...
problems = ['R3154', 'R5912']
for p in problems:
    RNUMBERS.remove(p)

# Override and run for only these RNUMBERS
RNUMBERS = ['R6152']  
    
for rnum in RNUMBERS:
    for frun in FUNCTIONALRUN:
        # Adjust analysis files
        with open(DESIGN_FILE, 'r') as f:
            content = f.read()
        # Substitute R number
        content_new = re.sub('R\d\d\d\d', rnum, content, flags=re.M)
        # Substitute fMRI run number
        content_new = re.sub('FMRI_\d', 'FMRI_'+ frun, content_new, flags=re.M)
        # Substitute event file block number
        content_new = re.sub('block\d', 'block'+ frun, content_new, flags=re.M)

        # Write out new fsf file
        fname = FSFDIR + rnum + '_FMRI_' + frun + '_level_1_stats.fsf'
        with open(fname, 'w') as f:
            f.write(content_new)                     
                            
        cmd = 'clusterFeat {}'.format(fname)
        print('Running: ', cmd)
        os.system(cmd)
            
            


    
