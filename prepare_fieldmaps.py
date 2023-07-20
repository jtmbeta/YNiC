#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 09:43:16 2023

@author: jtm545

Script to prepare the gradient fieldmaps for B0 unwarping in the FSL pipeline.
Follow this link for more information on the process:
    
https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FUGUE/Guide#Making_Fieldmap_Images_for_FEAT


"""

import os
import os.path as op
import glob
import errno


#%%

# R numbers
with open('../RNUMBERS.txt', 'r') as f:
    RNUMBERS = f.read().splitlines()

RNUMBERS = ['R4176']
    
# YNiC project ID
PROJECT = 'P1470'

# Image file extension
EXT = '.nii.gz'

# Override
RNUMBERS = ['R6128']

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


#%% Retrieve and prepare fieldmaps for B0 unwarping in FEAT.
    
fieldmap_dir = '/scratch/groups/Projects/P1470/fsl/fieldmaps'
if not op.exists(fieldmap_dir):
    os.mkdir(fieldmap_dir)

print("--------- Field maps ---------")

for rnum in RNUMBERS:
    pattern = '/mnt/siemensdata/{}/*{}/*GRE**.nii.gz'.format(rnum, PROJECT)
    #print(glob.glob(pattern))
    
    for f in glob.glob(pattern):
        
        # Symlink the magnitude images, assuming 'ECHO2' is the best
        if f.endswith('ECHO2.nii.gz'):  # This is the magnitude image
            target = '{}/{}_FMAP_MAG.nii.gz'.format(fieldmap_dir, rnum)
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
            target = '{}/{}_FMAP_PHASE.nii.gz'.format(fieldmap_dir, rnum)
            force_symlink(f, target)
            
        # Prepare fieldmap for B0 unwarping. The raw scanner output maps 0-360
        # degrees to an integer between 0-4096. This step is required to
        # convert the image to radians-per-second. 2.46 is the echotime
        # difference of the fieldmap acquisitions.
        cmd = (('fsl_prepare_fieldmap SIEMENS {o}/{r}_FMAP_PHASE ' 
               '{o}/{r}_FMAP_MAG_brain_ero {o}/{r}_FMAP_RADS 2.46')
        .format(o=fieldmap_dir, r=rnum))
        os.system(cmd)    