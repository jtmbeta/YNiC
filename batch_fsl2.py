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
import re

# THIS IS GOING TO BE THE SUBJECT AVERAGE SCRIPT

FUNCTIONALRUN = [str(i) for i in range(1, 5)]

# The example featsetup file for one subject
designfile = '/scratch/groups/Projects/P1459/jtm/featsetup/R2268_level_2.fsf'

# Where we will put all of the featsetup files
analysisdir ='/scratch/groups/Projects/P1459/jtm/fsfs/'

# For now...
#problems = ['R3154', 'R5912']
#for p in problems:
#    RNUMBERS.remove(p)
    
#RNUMBERS = ['R6169']
    
# run for a single R number
with open('../RNUMBERS.txt', 'r') as f:
    RNUMBERS = f.read().splitlines()

#RNUMBERS = ['R6172']
    
for rnum in RNUMBERS:
    # Adjust analysis files
    with open(designfile, 'r') as f:
        content = f.read()
        
    # Substitute R number - that's it for level 2
    content_new = re.sub('R\d\d\d\d', rnum, content, flags=re.M)

    # Write out new fsf file
    fname = analysisdir + rnum + '_FMRI_' + 'level_2.fsf'
    with open(fname, 'w') as f:
        f.write(content_new)                     
        
    cmd = 'clusterFeat {}'.format(fname)
    print('Running: ', cmd)
    os.system(cmd)
            


    
