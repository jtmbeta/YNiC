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


#options = {i: f for i, f in enumerate(glob.glob('./featsetup/*.fsf'))}
#
#def choose_analysis(options):
#    print(options)
#    print('Which analysis?')

FUNCTIONALRUN = [str(i) for i in range(1, 5)]

#DESIGN_FILE = '/scratch/groups/Projects/P1459/jtm/featsetup/R2268_level_1.fsf'
DESIGN_FILE = '../featsetup/R2268_level_1_stats.fsf' 
DESIGN_FILE = '../featsetup/R2268_level_1.fsf'
DESIGN_FILE = '../featsetup/R2268_level_2.fsf'

FSFDIR ='../fsfs/'

# Get participant Rnumbers
with open('../RNUMBERS.txt', 'r') as f:
    RNUMBERS = f.read().splitlines()

# Override
#RNUMBERS = ['R2268']

for rnum in RNUMBERS:
    for frun in FUNCTIONALRUN:
        # Adjust analysis files
        with open(DESIGN_FILE, 'r') as f:
            content = f.read()
        # Substitute R number
        content_new = re.sub('R\d\d\d\d', rnum, content, flags=re.M)
        # Substitute fMRI run number
        content_new = re.sub('FMRI_\d', 'FMRI_' + frun, content_new, flags=re.M)
        # Substitute event file block number
        content_new = re.sub('block\d', 'block' + frun, content_new, flags=re.M)

        # Write out new fsf file
        fname = FSFDIR + 'tmp_' + rnum + '_' + frun + '.fsf'
        with open(fname, 'w') as f:
            f.write(content_new)                     
                            
        cmd = 'clusterFeat {}'.format(fname)
        print('Running: ', cmd)
        os.system(cmd)
            


    
