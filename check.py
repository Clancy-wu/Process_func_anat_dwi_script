import os
from glob import glob
import nibabel as nib

all_subs = glob(f'BIDS/sub-*')
sub_dir = all_subs[1]

def check_length(nii_file):
    if os.path.exists(nii_file):
        nii_len = nib.load(nii_file).shape[-1]
    else:
        nii_len = 0
    return nii_len

def check_file(sub_dir):
    sub_name = os.path.basename(sub_dir)
    bold_file = f'{sub_dir}/func/{sub_name}_task-rest_bold.nii.gz'
    t1_file = f'{sub_dir}/anat/{sub_name}_T1w.nii.gz'
    t2_file = f'{sub_dir}/anat/{sub_name}_T2w.nii.gz'
    dwi_file = f'{sub_dir}/dwi/{sub_name}_dwi.nii.gz'
    bold = check_length(bold_file)
    t1 = check_length(t1_file)
    t2 = check_length(t2_file)
    dwi = check_length(dwi_file)
    print(f'name: {sub_name}, bold: {bold}, t1: {t1}, t2: {t2}, dwi: {dwi}')

for sub_dir in all_subs:
    check_file(sub_dir)


all_subs = [i for i in glob(f'fmriprep/sub-sub*') if 'html' not in i]

def show_len_sub(sub_path):
    sub_files = glob(f'{sub_path}/func/*.nii.gz')
    sub_name = os.path.basename(sub_path)
    sub_len = len(sub_files)
    print(f'{sub_name}: {sub_len}')

for sub_path in all_subs:
    show_len_sub(sub_path)



sub_xcpd = [x for x in os.listdir('xcpd_nifti_143') if 'sub-' in x and 'html' not in x] # 143
sub_fmriprep = [x for x in os.listdir('fmriprep_148') if 'sub-' in x and 'html' not in x] # 148


a = [ k for k in sub_fmriprep if k not in sub_xcpd]
os.makedirs('xcpd_list', exist_ok=True)
for sub in a:
    sub_name = sub.replace('sub-sub', 'sub')
    os.system(f'touch xcpd_list/{sub_name}')