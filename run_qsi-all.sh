#!/bin/bash
my_path=`pwd`
for_each -nthreads 8 BIDS/sub-* : docker run -ti --rm \
    -v $my_path:/work \
    -u $(id -u):$(id -g) \
    -v /home/clancy/TemplateFlow:/opt/templateflow \
    -e TEMPLATEFLOW_HOME=/opt/templateflow \
    pennbbl/qsiprep:v0.19.1 \
    /work/BIDS/ /work/ participant --participant-label PRE \
	--skip_bids_validation \
	--nthreads 1 --omp-nthreads 2 \
	-w /work/qsiprep_work \
	--recon-only \
	--recon_input /work/qsiprep_142 \
	--recon_spec /work/kw_mrtrix_singleshell_ss3t_ACT-hsvs.json \
	--anat-modality T1w \
	--ignore fieldmaps \
	--anatomical-template MNI152NLin2009cAsym \
	--output-resolution 2 \
	--freesurfer-input /work/freesurfer \
	--fs-license-file /work/license.txt \
	--resource-monitor \
	--stop-on-first-crash

