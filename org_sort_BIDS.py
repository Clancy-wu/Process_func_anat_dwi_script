import os
import re
from glob import glob
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
def run(f, this_iter):
    with ProcessPoolExecutor(max_workers=15) as executor:
        results = list(tqdm(executor.map(f, this_iter), total=len(this_iter)))
    return results

all_dir = glob(f'org_dicom/*/*/*/*') # 212

def one_dir_sort(dir_path):
    dicom_command = f'/home/clancy/MRIcroGL/Resources/dcm2niix -f "%t_%c_%d_%n" -p y -z y -ba n {dir_path}'
    return os.system(dicom_command)

run(one_dir_sort, all_dir)
print('end.')

# read json file
import json
import pandas as pd

all_json = glob(f'org_dicom/*/*/*/*/*.json') # 212
json_file = all_json[1]
def get_json_info(json_file):
    json_info = json_file.split('/')
    trial_type = json_info[2]
    mri_type = json_info[3]
    sub_name = json_info[4]

    with open(json_file, 'r') as jf:
        jf_data = json.load(jf)
        aa = jf_data['PatientName']
        bb = jf_data['AcquisitionDateTime']
        cc = jf_data['ProtocolName']
    
    return json_file,trial_type,mri_type,sub_name,aa,bb,cc

future_result = run(get_json_info, all_json)
col_name = ['file','trial','mri','subject','subname','scantime','protocol']
df = pd.DataFrame(future_result, columns=col_name)
df.to_csv('org_dicom_info.csv', index=None)

############################################
from shutil import copy

all_subs = ['sub-'+"{:03}".format(i) for i in range(1, 31)]

def copy_nii_json(old_dir, new_path_name):
    os.makedirs(os.path.dirname(new_path_name), exist_ok=True)
    func_file = glob(f'{old_dir}/*.nii.gz')[0]
    json_file = glob(f'{old_dir}/*.json')[0]
    copy(func_file, f'{new_path_name}.nii.gz')
    copy(json_file, f'{new_path_name}.json')
    return 0

def org_dicom_org_bids(sub_name):
    sub_number = re.findall(r'sub-(\d+)', sub_name)[0]
    ## control before: run01
    control_before_dir = f'org_dicom/control/control_before/FunRaw/Sub_{sub_number}'
    control_before_newname = f'org_bids/{sub_name}/func/{sub_name}_task-rest_run-01_bold'
    _ = copy_nii_json(control_before_dir, control_before_newname)
    ## control after: run02
    control_after_dir = f'org_dicom/control/control_after/FunRaw/Sub_{sub_number}'
    control_after_newname = f'org_bids/{sub_name}/func/{sub_name}_task-rest_run-02_bold'
    _ = copy_nii_json(control_after_dir, control_after_newname)
    ## sd before: run03
    sd_before_dir = f'org_dicom/SD/SD_before/FunRaw/Sub_{sub_number}'
    sd_before_newname = f'org_bids/{sub_name}/func/{sub_name}_task-rest_run-03_bold'
    _ = copy_nii_json(sd_before_dir, sd_before_newname)
    ## sd after: run04
    sd_after_dir = f'org_dicom/SD/SD_after/FunRaw/Sub_{sub_number}'
    sd_after_newname = f'org_bids/{sub_name}/func/{sub_name}_task-rest_run-04_bold'
    _ = copy_nii_json(sd_after_dir, sd_after_newname)
    ## T1
    anat_newdir = f'org_bids/{sub_name}/anat'
    os.makedirs(anat_newdir, exist_ok=True)
    anat_old = f'org_dicom/SD/SD_before/T1Raw/Sub_{sub_number}'
    anat_old_nii = glob(f'{anat_old}/*.nii.gz')[0]
    anat_old_json = glob(f'{anat_old}/*.json')[0]
    copy(anat_old_nii, f'{anat_newdir}/{sub_name}_T1w.nii.gz')
    copy(anat_old_json, f'{anat_newdir}/{sub_name}_T1w.json')
    return 0

for sub in all_subs:
    print(sub)
    org_dicom_org_bids(sub)

# dataset_description
dataset_description = {
    "Name": "Sleep deprivation and acupuncture",
    "Date": "20250616T0952",
    "Notation": "For each func run: 01=Control Before, 02=Control After, 03=SD Before 04=SD After",
    "Notation2": "Before-After=Acupuncture, Control-SD=Sleep Deprivation",
    "BIDSVersion": "1.4.1",
    "Author": "Kang Wu",
    "Acknowledgements": "No",
    }
with open(os.path.join('org_bids/dataset_description.json'), 'w') as json_file:
    json.dump(dataset_description, json_file, indent=4)

############################################
# remove 10 time points
from nilearn import image
from glob import glob
def time_remove(func_nii, remove_time):
    func_img = image.load_img(func_nii)
    func_img_remove = image.index_img(func_img, slice(int(remove_time), func_img.shape[3]) )
    return func_img_remove

all_files = glob('org_bids/*/*/*')
from shutil import copy
for file in all_files:
    file_new = file.replace('org_bids', 'BIDS')
    os.makedirs(os.path.dirname(file_new), exist_ok=True)
    if 'func' in file and '.nii.gz' in file:
        remove_img = time_remove(file, remove_time=10)
        remove_img.to_filename(file_new)
    else:
        copy(file, file_new)
print('finished.')

## can run fmriprep
