import os
from shutil import copy, move
from glob import glob

fmriprep_dir = 'fmriprep'
temp_mask = '/home/clancy/TemplateFlow/tpl-MNI152NLin2009cAsym/tpl-MNI152NLin2009cAsym_res-02_desc-brain_mask.nii.gz'

### main
import json
brain_mask_description = {
    "mask source": "tpl-MNI152NLin2009cAsym_res-02_desc-brain_mask.nii.gz",
    "Author": "Kang Wu"
    }

def replace_standard_mask(sub_name):
    old_masks = glob(f'{fmriprep_dir}/{sub_name}/func/{sub_name}_*_space-MNI152NLin2009cAsym_res-2_desc-brain_mask.nii.gz')
    for old_mask in old_masks:
        # old_mask
        old_mask_json = old_mask.replace('brain_mask.nii.gz', 'brain_mask.json')
        new_mask = old_mask.replace('brain_mask.nii.gz', 'brain_mask_orig.nii.gz')
        new_mask_json = old_mask_json.replace('brain_mask.json', 'brain_mask_orig.json')
        move(old_mask, new_mask)
        move(old_mask_json, new_mask_json)
        copy(temp_mask, old_mask)
        with open(old_mask_json, 'w') as json_file:
            json.dump(brain_mask_description, json_file, indent=4)
    return 0

all_subs = [x for x in os.listdir(fmriprep_dir) if 'sub-' in x and 'html' not in x]
for sub_name in all_subs:
    replace_standard_mask(sub_name)
print('all finished.')
