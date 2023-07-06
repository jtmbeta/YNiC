#!/usr/bin/env bash

# Use this script to symlink the reg directories before combining the
# functional runs for the StimVsOff analysis

set -eu

standard_mt=/scratch/groups/Projects/P1459/jtm/featout/group_level_3_n\=36.gfeat/mt_mask.nii.gz
featpath=/scratch/groups/Projects/P1459/jtm/featout/

cat RNUMBERS.txt | while read rnum
do
for frun in 1 2 3 4; do
  echo $frun
  echo $rnum
  ln -sfT $featpath/${rnum}_FMRI_${frun}.feat/reg $featpath/${rnum}_FMRI_${frun}_StimVsOff.feat/reg 
done
done
