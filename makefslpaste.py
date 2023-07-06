#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 17:03:46 2023

Generate two text files containing the cope files and EV matrix to be pasted
into the feat GUI for third-level analysis.

@author: jtm545
"""

import os
import os.path as op
import glob
import re
import numpy as np


# Be sure to set these values appropriately.
NCONTRASTS = 2
NSUBJECTS = 13

evs = np.tile(np.eye(NCONTRASTS, dtype=int), (NSUBJECTS, 1))
print('These are the EVs for third-level analysis:\n\n', evs, '\n')
np.savetxt('../EV_paste.txt', evs, delimiter='\t', fmt='%i')

#copes = glob.glob('../featout/R*Off_3mm.gfeat/cope?*.feat/stats/cope*')
copes = glob.glob('../featout/R*FMRI.gfeat/cope?*.feat/stats/cope*')

def cope_sort(f):
    rnumber = int(re.findall(r'(?<=R)\d\d\d\d', f)[0])
    cope = int(re.findall(r'(?<=t/cope)\d+', f)[0])
    return [rnumber, cope]

# We want the copes to be in a sensible order. Here the sort key is 
# Rnumber:Cope
copes = sorted([op.abspath(c) for c in copes], key=cope_sort)
print('These are the copes for third-level analysis:\n\n', copes, '\n')

with open('../copefiles.txt' , 'w') as f:
    for c in copes:
        f.write(c + '\n')
        
print('Number of inputs (copes): {}'.format(len(copes)))
print(' -> Copy and paste into FSL from: ../copefiles.txt')
print('Number of main EVs: {}'.format(NCONTRASTS))
print(' -> Copy and paste into FSL from: ../EV_paste.txt')
