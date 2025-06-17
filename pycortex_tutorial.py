# install pycortex, it supports python3.11, so we can install pycortex in the nilearn conda env.
# remember to install numpy 1.26.1.

import os
import matplotlib.pyplot as plt
import numpy as np
from nilearn import image
import ants

import cortex
############## Method 1
subject = "fsaverage"
xfm = '/home/clancy/miniconda3/envs/nilearn/share/pycortex/db/fsaverage/transforms/atlas_2mm'
file = 'cortisol_brain_zcoef_sub19.nii.gz' # mni2009cAsym
TemplateFlow = '/home/clancy/TemplateFlow'
newmni_fslmni = ants.read_transform(f'{TemplateFlow}/tpl-MNI152NLin6Asym/tpl-MNI152NLin6Asym_from-MNI152NLin2009cAsym_mode-image_xfm.h5')
# ants transform
file_img = ants.image_read(file)
ref_img = ants.image_read(f'{TemplateFlow}/tpl-MNI152NLin6Asym/tpl-MNI152NLin6Asym_res-02_T1w.nii.gz')
file_fsl = newmni_fslmni.apply_to_image(image = file_img, 
                             reference = ref_img, 
                             interpolation='linear')

voxel_vol = cortex.Volume(file_fsl.numpy(), subject, xfm )
#cortex.webgl.show(data=voxel_vol)
# Then we have to get a mapper from voxels to vertices for this transform
mapper = cortex.get_mapper(subject, xfm, 'line_nearest', recache=True)
# Just pass the voxel data through the mapper to get vertex data
vertex_map = mapper(voxel_vol)
# You can plot both as you would normally plot Volume and Vertex data
cortex.quickshow(vertex_map)
plt.show()

############## Method 2
from nilearn.surface import SurfaceImage
from nilearn.datasets import load_fsaverage
fsa = load_fsaverage('fsaverage')
file = 'cortisol_brain_zcoef_sub19.nii.gz' # mni2009cAsym
file_surf = SurfaceImage.from_volume(fsa["pial"], file, inner_mesh=fsa["white_matter"])

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
red_yellow_file = '/usr/local/fsl/fslpython/envs/fslpython/lib/python3.8/site-packages/fsleyes/assets/colourmaps/red-yellow.cmap'
blue_lightblue_file = '/usr/local/fsl/fslpython/envs/fslpython/lib/python3.8/site-packages/fsleyes/assets/colourmaps/blue-lightblue.cmap'
red_yellow_data = np.loadtxt(red_yellow_file)
blue_lightblue_org = np.loadtxt(blue_lightblue_file)
blue_lightblue_data = blue_lightblue_org[::-1]
combined = np.vstack((blue_lightblue_data, red_yellow_data))
cmap_aa = ListedColormap(combined)
vertex_data = cortex.Vertex(np.append(file_surf.data.parts['left'],file_surf.data.parts['right']), 
                              subject, vmax=1, vmin=-1, cmap=cmap_aa)
cortex.quickshow(vertex_data)
plt.show()
