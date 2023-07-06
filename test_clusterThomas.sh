#!/usr/bin/env bash

set -eu 

#source /scratch/groups/Projects/P1459/jtm/scripts/clusterThomas.sh

# Loop over R-numbers
while read rnum; do
  echo $rnum 
  sed -i "s/R..../$rnum/" clusterThomas.sh
  qsub clusterThomas.sh
done < ../RNUMBERS.txt
