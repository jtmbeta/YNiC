#!/usr/bin/env bash

# Use this script to create individual subject masks for MT via linear 
# backprojection from standard space.

set -eu

# Rnumbers
rnumbers=/scratch/groups/Projects/P1459/jtm/RNUMBERS.txt

# Base directories
featpath=/scratch/groups/Projects/P1459/jtm/featout
mt_loc_dir="$featpath"/group_level_3_n\=36.gfeat

# First, make the mask from the functional localiser (zstat7)
cluster -i "$mt_loc_dir"/cope1.feat/stats/zstat7 \
  -t 7 --no_table -o "$mt_loc_dir"/mt_cluster_index

fslmaths -dt int "$mt_loc_dir"/mt_cluster_index \
  -thr 1 -uthr 1 -bin "$mt_loc_dir"/mt_mask_right

fslmaths -dt int "$mt_loc_dir"/mt_cluster_index \
  -thr 2 -uthr 2 -bin "$mt_loc_dir"/mt_mask_left

fslmaths "$mt_loc_dir"/mt_mask_right.nii.gz \
  -add "$mt_loc_dir"/mt_mask_left.nii.gz "$mt_loc_dir"/mt_mask.nii.gz

# Now, here's the path to the mt_mask that we just created in standard space
standard_mt="$mt_loc_dir"/mt_mask.nii.gz

while read rnum; do
  echo $rnum
  # Make MT mask
  flirt -in "$standard_mt" \
    -ref "$featpath"/"$rnum"_FMRI_1.feat/reg/highres.nii.gz \
    -applyxfm \
    -init "$featpath"/"$rnum"_FMRI_1.feat/reg/standard2highres.mat \
    -o "$featpath"/"$rnum"_FMRI_1.feat/mt_mask_highres.nii.gz
  
  # Rebinaryise
  fslmaths "$featpath"/"$rnum"_FMRI_1.feat/mt_mask_highres.nii.gz \
    -bin "$featpath"/"$rnum"_FMRI_1.feat/mt_mask_highres_bin.nii.gz  

  # resample to func space
  flirt -in "$featpath"/"$rnum"_FMRI_1.feat/mt_mask_highres_bin.nii.gz \
    -ref "$featpath"/"$rnum"_FMRI_1.feat/filtered_func_data.nii.gz \
    -applyxfm \
    -init "$featpath"/"$rnum"_FMRI_1.feat/reg/highres2example_func.mat \
    -interp nearestneighbour \
    -o "$featpath"/"$rnum"_FMRI_1.feat/mt_mask_func_bin.nii.gz

  # Copt to other feat dirs
  for frun in 2 3 4; do
    cp "$featpath"/"$rnum"_FMRI_1.feat/mt_mask_highres_bin.nii.gz \
      "$featpath"/"$rnum"_FMRI_"$frun".feat/mt_mask_highres_bin.nii.gz
    cp "$featpath"/"$rnum"_FMRI_1.feat/mt_mask_func_bin.nii.gz \
      "$featpath"/"$rnum"_FMRI_"$frun".feat/mt_mask_func_bin.nii.gz
  done
done < "$rnumbers"

