import os
import os.path as op
import glob
import re

import pandas as pd
import seaborn as sns



pattern = '/scratch/groups/Projects/P1470/fsl/featout/*.feat/featquery*'
featquery_dirs = glob.glob(pattern)

featquery_headers = [
    "num",
    "stats_image", 
    "#voxels",
    "is_min",
    "is_10%", 
    "is_mean", 
    "is_median",
    "is_90%",
    "is_max", 
    "is_stddev",
    "pom_vox_fMRI_x",
    "pom_vox_fMRI_y",
    "pom_vox_fMRI_z",
    "pom_mm_standard_x",
    "pom_mm_standard_y",
    "pom_mm_standard_z"
    ]

image_map = {
    "stats/pe1": "BinLow",
    "stats/pe3": "MonHigh",
    "stats/pe5": "BinHigh"
}

list_of_dfs = []
for fqd in featquery_dirs:
    report = op.join(fqd, 'report.txt')
    df = pd.read_table(report, header=None, delimiter=' ')
    df.columns = featquery_headers
    df['rnum'] = re.search("R\d\d\d\d", fqd)[0]
    df['frun'] = re.search("(?<=FMRI_)[1-4]", fqd)[0]
    df['roi'] = re.search("(?<=featquery_)[A-Z].+$", fqd)[0]
    #df['cope'] = re.search("cope\d.feat", fqd)[0]

    list_of_dfs.append(df)

gdf = pd.concat(list_of_dfs).reset_index(drop=True)
gdf['Condition'] = 'LMS'
gdf.loc[gdf.frun.isin(['3','4']), 'Condition'] = 'MEL'
gdf['Ocularity'] = ''
gdf.loc[gdf.stats_image=='stats/pe1', 'Ocularity'] = 'BinLow'
gdf.loc[gdf.stats_image=='stats/pe3', 'Ocularity'] = 'MonHigh'
gdf.loc[gdf.stats_image=='stats/pe5', 'Ocularity'] = 'BinHigh'

gavdf = gdf.groupby(['rnum', 'Condition', 'Ocularity', 'roi'], as_index=False).mean() 

sns.catplot(
    data=gavdf, 
    x='roi', y='is_mean', 
    units='rnum', 
    kind='bar', 
    col='Condition', 
    hue='Ocularity',
    hue_order=['BinLow', 'MonHigh', 'BinHigh'],
    ci=68
    )