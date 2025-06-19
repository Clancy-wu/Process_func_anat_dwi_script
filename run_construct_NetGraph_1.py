from nilearn import image, regions
import numpy as np
import os
import re
from glob import glob
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
from itertools import product
import pandas as pd

#######################################################
# functions to compute correlation matrix
def run(f, this_iter):
    with ProcessPoolExecutor(max_workers=15) as executor:
        results = list(tqdm(executor.map(f, this_iter), total=len(this_iter)))
    return results

def create_func_network(func_file):
    # atlas and out dir
    TempleFlow_dir = '/home/clancy/TemplateFlow'
    func_atlas = f'{TempleFlow_dir}/tpl-MNI152NLin2009cAsym/BN_Atlas246_2mm_tpl-MNI152NLin2009cAsym.nii.gz'
    out_dir = 'NetFunc'
    os.makedirs(out_dir, exist_ok=True)

    sub_name = re.findall(r'(sub-.*)_task', os.path.basename(func_file))[0]
    sub_run = re.findall(r'run-(\d+)', os.path.basename(func_file))[0]

    # keep_masked_labels=False has been deprecated
    # df[0] = (TimePoints, Regions)
    df = regions.img_to_signals_labels(func_file, labels_img=func_atlas, background_label=0, strategy='mean')
    df_cor = pd.DataFrame(df[0]).corr(method='pearson') # (Regions, Regions)
    df_cor.replace(1, 0, inplace=True) # make diagonal to be zero
    df_cor = df_cor.fillna(0) # make some outlier labels to be zero
    df_cor_z = np.arctanh(df_cor) # make fisherz transform
    df_out_name = os.path.join(out_dir, f'PearCorZ_{sub_name}_{sub_run}.txt')
    df_cor_z.to_csv(df_out_name, header=None, index=None, sep=' ')

#######################################################
# functional network construction
all_files = glob(f'xcpd_nifti/sub-*/func/sub-*_task-rest_run-*_space-MNI152NLin2009cAsym_res-2_desc-denoisedSmoothed_bold.nii.gz')
run(create_func_network, all_files)
print('finished.')

# information for network construction
Id=[]; Group=[]
for file in all_files:
    sub_name = re.findall(r'(sub-.*)_task', os.path.basename(file))[0]
    sub_run = re.findall(r'run-(\d+)', os.path.basename(file))[0]

    sub_id = f'name_{sub_name}_run_{sub_run}'
    sub_group = f'run_{sub_run}'

    Id.append(sub_id); Group.append(sub_group)

df = pd.DataFrame({
    'participant_id': Id,
    'group': Group
})
df = df.sort_values(by=['participant_id'])
df.to_csv('run_construct_NetGraph_info.csv', index=None)

######## end. author@kangwu.