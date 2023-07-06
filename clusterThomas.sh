#!/usr/bin/env bash

set -eu

rnum=R6128
echo $rnum
#touch ~/"$1".txt 
#echo "Created $1.txt"

# Define paths
structural=/scratch/sg9/P1459/jtm/structural
thomasmasks=/scratch/sg9/P1459/jtm/thomasmasks_test

outdir="$thomasmasks/${rnum}"

# Check for $rnumber directory
if [ ! -d "$outdir" ]; then
  echo $outdir
  mkdir -p "$outdir"
  echo "Made directory: $outdir"
fi

# Move to the working directory
cd "$outdir"
ln -s "${structural}/${rnum}_T1.nii.gz" .
thomas_csh_mv "${rnum}"_T1.nii.gz


