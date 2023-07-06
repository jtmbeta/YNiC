#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 08:39:23 2023

@author: jtm545

Visualise motion parameters for each subject with common minmax scaling.
"""

import glob

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_context('paper', font_scale=1.2)


# R numbers
with open('../jtm/RNUMBERS.txt', 'r') as f:
    RNUMS = f.read().splitlines()
    
target = './featout/{}_FMRI_{}.feat/mc/prefiltered_func_data_mcf.par'
mcdata = []

for r in RNUMS:
    for f in ['1', '2', '3', '4']:
        fname = target.format(r, f)
        try:
            df = pd.read_table(fname, header=None, sep='\s+')
            df['RNUM'] = r
            df['FRUN'] = f
            mcdata.append(df)
            
        except:
            continue
        
mcdata = pd.concat(mcdata)
mcdata.columns = ['xrot', 'yrot', 'zrot', 'xmov', 'ymov', 'zmov', 'RNUM', 'FRUN']
mcdata.index.name = 'volume'
mcdata = mcdata.reset_index().melt(id_vars=['RNUM', 'FRUN', 'volume'])     
mcdata['Motion Type'] = mcdata.variable.str[1:]
mcdata['Motion Type'] = mcdata['Motion Type'].replace({'rot': 'Rotation', 'mov': 'Translation'})
mcdata.variable = mcdata.variable.str[0]
mcdata = mcdata.rename(columns={'volume': 'Volume', 'variable': 'Direction'})
    
# Used to scale axis
minmax = mcdata.groupby('Motion Type')['value'].agg(['min', 'max'])
minmax = minmax + (minmax * .1)
minmaxrot = tuple(minmax.loc['Rotation'])
minmaxtran = tuple(minmax.loc['Translation'])     
   
for r in RNUMS:
    try:
        data = mcdata.loc[mcdata.RNUM==r]

        # Rotation
        g = sns.relplot(
            data=data,
            x='Volume', y='value',
            hue='Direction', row='Motion Type', col='FRUN',
            kind='line', height=4, aspect=1.5, facet_kws=dict(sharey=False)
            )
        
        for ax in g.axes[0]:
            ax.set_ylim(minmaxrot)
            
        for ax in g.axes[1]:
            ax.set_ylim(minmaxtran)
            ax.set_xlabel('Volume (TR = 3 s)')
       
        g.axes[0, 0].set_ylabel('Radians')
        g.axes[1, 0].set_ylabel('mm')

            
        g.savefig('./figs/headmotion/{}_nf.svg'.format(r))
        
    except:
        continue

        
