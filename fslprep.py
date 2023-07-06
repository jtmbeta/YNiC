# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import sys
import os
import os.path as op
import pathlib
import errno
import glob
import re

import scipy.io as scipyio
import pandas as pd
import numpy as np



#LOGFILE = True
#if LOGFILE:
#    if op.exists('logfile.txt'):
#        os.remove('logfile.txt')
#    sys.stdout = open('logfile.txt', 'w')
    
# R numbers
with open('../jtm/RNUMBERS.txt', 'r') as f:
    RNUMBERS = f.read().splitlines()
    
# YNiC project ID
PROJECT = 'P1459'

# Image file extension
EXT = '.nii.gz'

# Dictionary mapping experiment condition codes to names
CONDITIONS = {
        1: 'MonLDisc',
        2: 'MonLGrating',
        3: 'MonLDrift',
        4: 'MonLIsoRG',
        5: 'MonLIsoBY',
        6: 'MonRDisc',
        7: 'MonRGrating',
        8: 'MonRDrift',
        9: 'MonRIsoRG',
        10: 'MonRIsoBY',
        11: 'BinDisc',
        12: 'BinGrating',
        13: 'BinDrift',
        14: 'BinIsoRG',
        15: 'BinIsoBY',
        16: 'BinDisc',
        17: 'BinGrating',
        18: 'BinDrift',
        19: 'BinIsoRG',
        20: 'BinIsoBY'
        }

# For now...
#problems = ['R5912']
#for p in problems:
#    RNUMBERS.remove(p)

# Override and run for only these RNUMBERS
#RNUMBERS = ['R6128','R5871', 'R6172']


#%% A useful function
    
def force_symlink(file, target):
    """Force overwrite if symlink target file already exists.
    
    Args:
        file (str): Full path to file that will be symlinked.
        target (str): Full path to new symlink.

    Returns:
        None
    """
    try:
        os.symlink(file, target)
    except OSError as e:
        if e.errno == errno.EEXIST:
            os.remove(target)
            os.symlink(file, target)
    finally:
        print('{} --> {}'.format(file, target))
    return None

#%% New folders for featsetup and feat output if not already
for f in ['featsetup', 'featout']:
    if not op.exists(f):
        os.mkdir(f)

#%% Prepare EV files (onset, duration, weighting)
# This is experiment-specific stuff to extract the event info from the .mat
# files produced by the psyctoolbox script and turn them into three-column EV
# files for FSL.

# Results from the psychtoolbox script are saved here
exptdir = '/groups/Projects/P1459/Results/'

# New folder for eventfiles if not already
eventfile_dir = 'eventfiles'
if not op.exists(eventfile_dir):
    os.mkdir(eventfile_dir)

# Loop over R numbers
for rnum in RNUMBERS:
    # This .mat file contains the trial orders for each functional run
    trial_orders = scipyio.loadmat(
            op.join(exptdir, '{}_trialOrder.mat'.format(rnum))
            )
    
    # Process the times for each block
    for block in [1, 2, 3, 4]:
                    
        # This has the event start times for each stimulus
        matfile = '/groups/Projects/P1459/Results/{}TimesBlock{}.mat'.format(rnum, block)
        times_block_file = scipyio.loadmat(matfile)
        #event_times = times_block_file.get('eventtimes')[0]
        # Make event times relevant to the start of the experiment
        #event_times = (event_times - event_times[0]).round()
        # Get the list of 20 stimulus onset times. These are 1 to the end in
        # steps of 3
        #event_times = event_times[1::3]
        #print(event_times)
        
        # The event times are in fact always the same as below
        event_times = np.array([
                0., 24., 48., 72., 96.,120.,144., 168., 192., 216., 240., 
                264., 288., 312., 336., 360., 384., 408., 432., 456.
                ])
        
        #TODO: add exceptions to get correct trial orders 
        # No longer required
        
        # Get conditions, collapsing accross mon and bin. For one subject, 
        # we are disregarding the first functional block
        if rnum == 'R6188':
            conditions = trial_orders['R'][0][0][3][block]
        else:
            conditions = trial_orders['R'][0][0][3][block-1]  # -1 (because MATLAB)
        collapse_mon = [6, 7, 8, 9, 10]
        collapse_bin1 = [11, 12, 13, 14, 15]
        collapse_bin2 = [16, 17, 18, 19, 20]
        collapsed_conditions = []
        for c in conditions:
            if c in collapse_mon:
                collapsed_conditions.append(c-5)
            elif c in collapse_bin1:
                collapsed_conditions.append(c-5)
            elif c in collapse_bin2:
                collapsed_conditions.append(c-10)
            else:
                collapsed_conditions.append(c)
                
        # Durations are all 12 s
        durations = np.ones(len(event_times)) * 12
        
        # Weights are set to 1 for fsl EV files
        weights = np.ones(len(event_times))
        
        # Gather stimulus information
        columns = ['onset', 'duration', 'weighting', 'stimcode', 'collapsed_stimcode']
        stim_info = np.array([event_times, durations, weights, conditions, collapsed_conditions]).T
        stim_info = pd.DataFrame(stim_info, columns=columns)
        stim_info['condition'] = stim_info['stimcode'].map(CONDITIONS)
        stim_info['collapsed_condition'] = stim_info['condition'].str.replace('nL', 'n')
        stim_info['collapsed_condition'] = stim_info['collapsed_condition'].str.replace('nR', 'n')
        stim_info['block'] = block
        
        # Save EV file for each stimulus type
        out_dir = op.join(eventfile_dir, rnum)
        pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
        fname = (op.join(out_dir, '{r}_conditions_block_{b}.txt')
                 .format(o=eventfile_dir, r=rnum, b=block))
        stim_info.to_csv(fname)

        for c in stim_info.collapsed_stimcode.unique():
            ev_fname = (
                    './{o}/{r}_conditions_block{b}_{con}.txt'
                    .format(o=out_dir, r=rnum, b=block, con=str(int(c)).zfill(2))
                    )
            ev_cols = ['onset', 'duration', 'weighting']
            df = stim_info.loc[stim_info.collapsed_stimcode==c, ev_cols]
            np.savetxt(ev_fname, df.values, delimiter='\t')
                    
#%% Retrieve and prepare fieldmaps for B0 unwarping in FEAT
fieldmap_dir = 'fieldmaps'
if not op.exists(fieldmap_dir):
    os.mkdir(fieldmap_dir)

print("--------- Field maps ---------")

for rnum in RNUMBERS:
    pattern = '/mnt/siemensdata/{}/*{}/*GRE**.nii.gz'.format(rnum, PROJECT)
    #print(glob.glob(pattern))
    
    for f in glob.glob(pattern):
        
        # Symlink the magnitude images, assuming 'ECHO2' is the best
        if f.endswith('ECHO2.nii.gz'):  # This is the magnitude image
            target = './{}/{}_FMAP_MAG.nii.gz'.format(fieldmap_dir, rnum)
            force_symlink(f, target)
            
            # Run BET on magnitude image using default params. If non-default
            # parameters are required (e.g., for fractional intensity), then 
            # these may be determined manually and included in a text file 
            # that can be read in at this stage.
            bet_output = target.replace(EXT, '') + '_brain' + EXT
            cmd = 'bet {} {}'.format(target, bet_output)
            print('!{}'.format(cmd))
            os.system(cmd)
            
            # Erode image to remove noisy partial volume voxels near the edge 
            # of the brain. As implemented below, this shaves a single voxel 
            # off the edge of the brain for every magnitude image. This may not
            # always be necessary, so eventually we should look at the images
            # and decide which of them actually require this step.
            eroded_output = bet_output.replace(EXT, '') + '_ero' + EXT
            cmd = 'fslmaths {} -ero {}'.format(bet_output, eroded_output)
            print('!{}'.format(cmd))
            os.system(cmd)
            
        # Symlink the phase images, which end with 'MAPPING.nii.gz'
        if f.endswith('MAPPING.nii.gz'):
            target = './{}/{}_FMAP_PHASE.nii.gz'.format(fieldmap_dir, rnum)
            force_symlink(f, target)
            
        # Prepare fieldmap for B0 unwarping. The raw scanner output maps 0-360
        # degrees to an integer between 0-4096. This step is required to
        # convert the image to radians-per-second. 2.46 is the echotime
        # difference of the fieldmap acquisitions.
        cmd = (('fsl_prepare_fieldmap SIEMENS ./{o}/{r}_FMAP_PHASE ' 
               './{o}/{r}_FMAP_MAG_brain_ero ./{o}/{r}_FMAP_RADS 2.46')
        .format(o=fieldmap_dir, r=rnum))
        #print('!{}'.format(cmd))
        os.system(cmd)
            
#%% Retrieve structural and run the brain extraction tool
structural_dir = 'structural'
if not op.exists(structural_dir):
    os.mkdir(structural_dir)

print("--------- Structural ---------")

for rnum in RNUMBERS:
    if rnum == 'R5912':
        pattern = '/mnt/siemensdata/{}/*P1438/*.nii.gz'.format(rnum)
    else:
        pattern = '/mnt/siemensdata/{}/*{}/*.nii.gz'.format(rnum, PROJECT)
        
    files = [f for f in glob.glob(pattern) if '3_T1' in f or '5_T2' in f or '17_T1' in f]
    
    for f in files:
        # Symlink the magnitude T1 structural image
        if '3_T1' in f:
            target = './{o}/{r}_T1.nii.gz'.format(o=structural_dir, r=rnum)
            force_symlink(f, target)
        
        # Symlink the magnitude T2 structural image
        if '5_T2' in f:
            target = './{o}/{r}_T2.nii.gz'.format(o=structural_dir, r=rnum)
            force_symlink(f, target)
            
        # This is for R6142 (repeated structural scan at end)  
        if '17_T1' in f:
            target = './{o}/{r}_T1.nii.gz'.format(o=structural_dir, r=rnum)
            force_symlink(f, target)
        print(target)
        
        # Run BET with default params (for now) on T1 structural image
        bet_output = target.replace(EXT, '') + '_brain' + EXT
        cmd = 'bet {} {}'.format(target, bet_output)
        print('!{}'.format(cmd))
        os.system(cmd)
            

#%% Retrieve fMRI
# Symlink all functional runs into a local directory. There may be some
# exceptions to be dealt with, such as multiple functional runs with the same
# name (e.g., when a block had to be restarted). These can be dealt with 
# on a per-R basis. 

fmri_dir = 'fmri'
if not op.exists(fmri_dir):
    os.mkdir(fmri_dir)
    
def func_sort(f):
    '''Sort list of fmri files.
    
    We want the ones with the highest numbers
    '''
    frun = int(re.findall(r'(?<=FMRI)\d+', f)[0])
    pre_num = int(re.findall(r'\d+(?=_FMRI)', f)[0])
    return [pre_num, frun]


print("--------- Functional ---------")

    
for rnum in RNUMBERS:
    pattern = '/mnt/siemensdata/{}/*{}/*FMRI**.nii.gz'.format(rnum, PROJECT)
    fmri_files = glob.glob(pattern)
    # Deal with exceptions. 
    # e.g., Had to restart the second functional run for R5292
    if rnum == 'R5929': 
        fmri_files = [f for f in fmri_files if not '12_FMRI2' in f]
    if rnum == 'R6160': 
        fmri_files = [f for f in fmri_files if not '11_FMRI1' in f]
    if rnum == 'R3154':  # A few false starts here
        fmri_files = [f for f in fmri_files if re.search('[2349]_FMRI[1234]_XPQ164', f)]
    if rnum == 'R6188':  # Fixated at wrong place in first run
        fmri_files = [f for f in fmri_files if re.search('1[2-5]_FMRI[2-5]_XPQ164', f)]
            
    for run, f in enumerate(sorted(fmri_files, key=func_sort)):            
        #frun = re.search('(?<=FMRI)\d', f).group()
        target = './{o}/{r}_FMRI_{run}.nii.gz'.format(
                o=fmri_dir, r=rnum, run=run+1)
        force_symlink(f, target)
        