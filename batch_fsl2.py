#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 13:49:24 2022

@author: jtm545
"""

import os
import os.path as op
import re

# THIS IS GOING TO BE THE SUBJECT AVERAGE SCRIPT

FUNCTIONALRUN = [str(i) for i in range(1, 5)]

# The example featsetup file for one subject
designfile = '/scratch/groups/Projects/P1470/fsl/featsetup/R3154_level_2.fsf'

# Where we will put all of the featsetup files
fsfdir = '/scratch/groups/Projects/P1470/fsl/fsfs'

# Get all of the R numbers
with open('../RNUMBERS.txt', 'r') as f:
    RNUMBERS = f.read().splitlines()

# Run for a single R number
#RNUMBERS = ['R3154']
    
for rnum in RNUMBERS:
    # Adjust analysis files
    with open(designfile, 'r') as f:
        content = f.read()
        
    # Substitute R number - that's it for level 2
    content_new = re.sub('R\d\d\d\d', rnum, content, flags=re.M)

    # Write out new fsf file
    fname = op.join(fsfdir, f'tmp_{rnum}_level_2.fsf')
    with open(fname, 'w') as f:
        f.write(content_new)                     
        
    cmd = 'clusterFeat {}'.format(fname)
    print('Running: ', cmd)
    os.system(cmd)
            


    
