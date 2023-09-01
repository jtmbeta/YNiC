#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 12:27:56 2023

@author: jtm545
"""


import os
import os.path as op
import shutil

import pandas as pd


# Make directory for button responses 
buttonresps = '/scratch/groups/Projects/P1470/fsl/buttonresps'
if not op.exists(buttonresps):
    os.mkdir(buttonresps)

# Get participant Rnumbers
with open('../RNUMBERS.txt', 'r') as f:
    RNUMBERS = f.read().splitlines()
    
# Override
#RNUMBERS = ['R4176']
    
df = pd.DataFrame()
for rnum in RNUMBERS:
    
    for frun in ['1', '2', '3', '4']:
        events_fpath = '/scratch/groups/Projects/P1470/fsl/buttonresps/{}_00{}_events.csv'.format(rnum, frun)
        btns_fpath = '/scratch/groups/Projects/P1470/fsl/buttonresps/{}_00{}_buttons.csv'.format(rnum, frun)
        evs = pd.read_csv(events_fpath)
        btns = pd.read_csv(btns_fpath)
        btns = btns.loc[btns.event=='press']
        
        for idx, row in btns.iterrows():
            
            # TODO: filter successive button events when the button is held
            # down, tackle edge cases such as when the first event
            
            
            # Find the most recent event preceding a button press
            previous_evs = (evs.Onset - row.time)
            previous_evs = previous_evs.loc[previous_evs < 0]
            event_idx = previous_evs.abs().idxmin()
            
            new = pd.concat([evs.loc[event_idx], row])
#            if event_idx == 0:  # False start
#                new['buttonRT'] = -1
#            else:
            new['buttonRT'] = new.time - new.Onset
            new['Rnum'] = rnum
            new['Frun'] = frun
            
            # 
            df = df.append(new.to_frame().T)

df.buttonRT = df.buttonRT.astype('float')
mean = df.buttonRT.mean()
sd = df.buttonRT.std()
mad = df.buttonRT.mad()
ut = mean + (2*mad)
lt = mean - (2*mad)

# Plot
ax = df.buttonRT.plot(kind='hist', bins=200)
for t in [lt, ut]:
    ax.axvline(t, color='k')
ax.set(xlabel='RT (s)')