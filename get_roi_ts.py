#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 10:38:34 2023

@author: jtm545
"""
import re
import glob
import os.path as op

import pandas as pd
import numpy as np
import seaborn as sns

sns.set_context('paper', font_scale=1.5)

ROIs = ['SCN', 'CSF', 'V1']
TR = 3.
baseline = 6.
featdir = '/scratch/groups/Projects/P1470/fsl/featout/'


# run for a single R number
with open('../RNUMBERS.txt', 'r') as f:
    RNUMBERS = f.read().splitlines()
    
#RNUMBERS = ['R3154']


#%% Calculate pct change from mean for each functional run

dfs = []
for rnum in RNUMBERS:
    for frun in [1, 2, 3, 4]:
        
        frundir = op.join(featdir, f'{rnum}_FMRI_{frun}.feat')
        event_file = f'/groups/Projects/P1470/Subjects/{rnum}/00{frun}/events.csv'
        evs = pd.read_csv(event_file)[['Onset', 'Event']]
        evs = evs.loc[evs.Event!='LMS']
        evs['Event'] = evs.Event.str.replace('MonL', 'Mon')
        evs['Event'] = evs.Event.str.replace('MonR', 'Mon')
        block = 'LMS' if frun in [1,2] else 'MEL'
        
        
        for roi in ROIs:
            
            fpath = op.join(frundir, f'{roi}_meants.txt')
            ts = np.loadtxt(fpath)
            
            for con in evs.Event.unique():
                con_evs = evs[evs.Event==con]
                
                for t in con_evs.Onset:
                    idx_start = int(t/TR)
                    idx_end = int(idx_start+33/TR)
                    fmri_ts = ts[idx_start:idx_end]
                    fmri_ts = fmri_ts - fmri_ts[0]
                    
                    df = {
                            'rnum': rnum,
                            'frun': frun,
                            'block': block,
                            'condition': con,
                            'roi': roi,
                            'BOLD%': fmri_ts,
                            'Time': np.arange(0, 33, 3)
                            }
                    dfs.append(pd.DataFrame(df))
                    
# Big df
df = pd.concat(dfs)
        
df.loc[df.block=='LMS', 'condition'] = df.loc[df.block=='LMS', 'condition'].str.replace('BinOff', 'LowLMS')
df.loc[df.block=='MEL', 'condition'] = df.loc[df.block=='MEL', 'condition'].str.replace('BinOff', 'LowMEL')

g = sns.catplot(x='Time', y='BOLD%', data=df[df.block=='MEL'], units='rnum', kind='point', col='roi', hue='condition', capsize=.1, dodge=.15)
g = sns.catplot(x='Time', y='BOLD%', data=df[df.block=='LMS'], units='rnum', kind='point', col='roi', hue='condition', capsize=.1, dodge=.15)



new = df.groupby(by=['rnum', 'block_type', 'condition', 'roi', 'Time'], as_index=False).mean()
g = sns.catplot(x='Time', y='BOLD%', data=new, kind='point', col='roi', hue='condition', capsize=.1, dodge=.15)
   
