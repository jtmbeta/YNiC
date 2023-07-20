#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 17:03:46 2023

@author: jtm545

Script to generate two text files containing the cope files and EV matrix to be
pasted into the feat GUI for third-level analysis. Without this, you would need 
to select them all manually, which takes forever. Be sure to specify the right 
number of subjects and contrasts.

"""

import os.path as op
import glob
import re
import numpy as np


# Be sure to set these values appropriately.
NCONTRASTS = 4  # The number of contrasts specified in the featsetup file(s).
NSUBJECTS = 17  # The number of subjects in the third-level analysis.

# Create the design matrix.
evs = np.tile(np.eye(NCONTRASTS, dtype=int), (NSUBJECTS, 1))
print('These are the EVs for third-level analysis:\n\n', evs, '\n')
np.savetxt('../EV_paste.txt', evs, delimiter='\t', fmt='%i')

# List all of the cope files
copes = glob.glob('../featout/R*FMRI.gfeat/cope?*.feat/stats/cope*')

# Make a handy function
def cope_sort(f):
    '''Function to sort copefiles in a principled way (required for feat)'''
    # Use fancy regex 'lookbehind' pattern to extract R-number and cope from
    # filenames (sort by these values).
    rnumber = int(re.findall(r'(?<=R)\d\d\d\d', f)[0])
    cope = int(re.findall(r'(?<=t/cope)\d+', f)[0])
    return [rnumber, cope]

# We want the copes to be in a sensible order. Here the sort key is
# Rnumber:Cope
copes = sorted([op.abspath(c) for c in copes], key=cope_sort)
print('These are the copes for third-level analysis:\n\n', copes, '\n')

# Put the list of cope files in a text file.
with open('../copefiles.txt' , 'w') as f:
    for c in copes:
        f.write(c + '\n')
        
# Provide some feedback on what just happened.
print('Number of inputs (copes): {}'.format(len(copes)))
print(' -> Copy and paste into FSL from: ../copefiles.txt')
print('Number of main EVs: {}'.format(NCONTRASTS))
print(' -> Copy and paste into FSL from: ../EV_paste.txt')
