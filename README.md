# YNiC

Experiment scripts and analysis code from YNiC projects `P1459` and `P1470` (see the different branches). 

## The YNiC cluster trope

Here's a neat way of using the YNiC cluster. It works well for pretty much any task, but is ideally suited to repetitive tasks that make use of neuroimaging command line tools and take a while to complete.

As an example, suppose you want to use the FSL command line tools to warp a mask back from standard space into functional space for many individual scans, but you do not have the inverse of the non-linear `transform highres2standard_warp` volume ([the problem described here](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FNIRT/UserGuide#Transforming_an_image_.28.27.27e.g..27.27_a_mask.29_in_standard_space_into_functional_space)). The script to create this volume for an individual scan would look something like this:

```bash
#!/usr/bin/env bash

# fsl_invwarp
# This is the invwarp command for a single subject/scan.

invwarp \
  --ref=/scratch/groups/Projects/P1470/fsl/featout/R6307_FMRI_4.feat/reg/highres \
  --warp=/scratch/groups/Projects/P1470/fsl/featout/R6307_FMRI_4.feat/reg/highres2standard_warp \
  --out=/scratch/groups/Projects/P1470/fsl/featout/R6307_FMRI_4.feat/reg/highres2standard_warp_inv
```

Now, to run this command in a serial fashion on a local machine for 18 subjects, each with four functional scans, you could use variable substitution within loops:

```bash
#!/usr/bin/env bash

# Rnumbers stored in a text file
rnumbers=/scratch/groups/Projects/P1470/fsl/RNUMBERS.txt

while read rnum; do
  for frun in {1..4}; do
    invwarp \
      --ref=/scratch/groups/Projects/P1470/fsl/featout/"$rnum"_FMRI_"$frun".feat/reg/highres \
      --warp=/scratch/groups/Projects/P1470/fsl/featout/"$rnum"_FMRI_"$frun".feat/reg/highres2standard_warp \
      --out=/scratch/groups/Projects/P1470/fsl/featout/"$rnum"_FMRI_"$frun".feat/reg/highres2standard_warp_inv
  done
done < "$rnumbers"

```

However, this particular commmand can take in excess of 10 minutes to run for an individual scan, so you are faced with around 12 hours of compute time. The solution is as follows:

1. Create the original script from above and call it `fsl_invwarp`. This script completes the task for a single subject. Don't forget to run `chmod a+x fsl_invwarp`.
2. Create another script called `cluster_fsl_invwarp` as follows (again, don't forget to change permissions):

```bash
#!/usr/bin/env bash

# cluster_fsl_invwarp
# Run the fsl_invwarp script on the cluster for all R-numbers and functional runs

# Rnumbers stored in a text file
rnumbers=/scratch/groups/Projects/P1470/fsl/RNUMBERS.txt

while read rnum; do
  for frun in {1..4}; do
    echo $rnum
    echo $frun
    # Modify the script in place
    sed -i -E "s/R[0-9]{4}_FMRI_[0-9]/${rnum}_FMRI_${frun}/g" fsl_invwarp
    qsub -j y -o /scratch/home/j/jtm545/logs fsl_invwarp
  done
done < "$rnumbers"
```

3. Understand what is happening. Basically, the above script uses the [`sed`](https://en.wikipedia.org/wiki/Sed) (Stream EDitor) command with [regular expressions](https://en.wikipedia.org/wiki/Regular_expression) to modify the `fsl_invwarp` script in-place (`-i`), and then submits it to the cluster with `qsub` following the [YNiC guidance for using the cluster](https://www.ynic.york.ac.uk/docs/ITPages/IT/ClusterScripts).

4. Run the script. 
```bash
./fsl_cluster_invwarp
```

5. Enjoy!
