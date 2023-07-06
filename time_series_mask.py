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

TR = 3.
baseline = 6.
featdir = '/scratch/groups/Projects/P1459/jtm/featout/'

# run for a single R number
with open('../RNUMBERS.txt', 'r') as f:
    RNUMBERS = f.read().splitlines()
    
#RNUMBERS = ['R2268']


#%% Calculate pct change from mean for each functional run
ROI = 'lgn_thomas'
STAT = 'pct'

dfs = []
for rnum in RNUMBERS:
    for frun in [1, 2, 3, 4]:
        frundir = op.join(featdir, f'{rnum}_FMRI_{frun}.feat')
        fpath = op.join(frundir, f'meants_{ROI}_{STAT}.txt')
        ts = np.loadtxt(fpath)
        
#        lgn_pct_f = op.join(frundir, 'meants_lgn_pct.txt')
#        ts = np.loadtxt(lgn_pct_f)
#        lgn_z_f = op.join(frundir, 'meants_lgn_z.txt')
#        ts = np.loadtxt(lgn_z_f)        
#        mt_pct_f = op.join(frundir, 'meants_mt_pct.txt')
#        ts = np.loadtxt(mt_pct_f)        
#        mt_z_f = op.join(frundir, 'meants_mt_z.txt')
#        mt_z_ts = np.loadtxt(mt_z_f)   
        
        # Get the conditions
        event_file = glob.glob(f'/scratch/groups/Projects/P1459/jtm/eventfiles/{rnum}/{rnum}_conditions_block_{frun}.txt')
        conditions = pd.read_csv(event_file[0])
        
        trials = []
        for idx, row in conditions.iterrows():
            #print(idx, row)
            onset = row.onset
            if onset==0.0:
                t = ts[int(onset/3):int(onset/3+9)]
                t = np.hstack([np.array(np.nan), t])
                t = t-t[1]
                trials.append(t)
            else:
                t = ts[int(onset/3)-1:int(onset/3+9)]
                t = t-t[1]
                trials.append(t)
            
        df = pd.DataFrame(trials).join(conditions)
        df['Rnum'] = rnum
        df['Frun'] = frun
        df['Ocular'] = 'Bin'
        df.loc[df.collapsed_condition.str.contains('Mon'), 'Ocular'] = 'Mon'
        df['Con'] = df.collapsed_condition.str.strip('MonBin')
        
        df = df.melt(
                value_vars=[0,1,2,3,4,5,6,7,8,9],
                var_name=['TR'],
                id_vars=['collapsed_condition', 'Rnum', 'Frun', 'Ocular', 'Con', 'onset'],
                value_name='BOLD'
                )
        
        df['TR'] = df['TR'].sub(1)
        dfs.append(df)

new = (
       pd.concat(dfs)
       .reset_index(drop=True)
       .sort_values(by=['Rnum', 'Frun', 'onset'])
       .groupby(by=['Rnum', 'collapsed_condition', 'Con', 'Ocular', 'TR'], as_index=False)
       .mean()
       .drop(columns=['onset', 'Frun'])
       )
new['Time (s)'] = new['TR'].mul(3)

pal = sns.color_palette('gray')
g = sns.catplot(
        data=new, x='Time (s)', y='BOLD', col='Con',palette=[pal[0], pal[-2]],
        units='Rnum', hue='Ocular', kind='point', capsize=.1, dodge=.15
        )
g.axes[0][0].set_ylabel('% BOLD signal change')
g.despine(offset=2, trim=True)
for ax in g.axes[0]:
    ax.axvspan(1,5,color='k',alpha=.05)

# Save the fig
g.savefig('../figs/{}_{}_change_new_thomas_lgn.png'.format(ROI, STAT), dpi=300)
