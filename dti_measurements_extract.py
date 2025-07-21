import os
import ants
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor

def dwi_measurements_generate(sub_name):
    dwi_b = f"qsiprep_142/{sub_name}/dwi/{sub_name}_space-T1w_desc-preproc_dwi.b"
    dwi_mask = f"qsiprep_142/{sub_name}/dwi/{sub_name}_space-T1w_desc-brain_mask.nii.gz"
    dwi_prepare = f"qsiprep_142/{sub_name}/dwi/{sub_name}_space-T1w_desc-preproc_dwi.nii.gz"
    os.makedirs('Results_mni/temp', exist_ok=True) # for process
    os.makedirs('Results_mni/FA', exist_ok=True) # FA
    os.makedirs('Results_mni/MD', exist_ok=True) # mean ADC
    os.makedirs('Results_mni/AD', exist_ok=True) # principal Diffusion

    #### ants transform
    t12mni_trans = ants.read_transform(f'qsiprep_142/{sub_name}/anat/{sub_name}_from-T1w_to-MNI152NLin2009cAsym_mode-image_xfm.h5')
    ref_mni = ants.image_read('/home/clancy/TemplateFlow/tpl-MNI152NLin2009cAsym/tpl-MNI152NLin2009cAsym_res-02_desc-brain_mask.nii.gz')
    #### tensor
    dwi_tensor = f"Results_mni/temp/{sub_name}_space-T1w_dwitensor.nii.gz"
    os.system(f"dwi2tensor -grad {dwi_b} -mask {dwi_mask} {dwi_prepare} {dwi_tensor} -quiet")

    #### FA
    fa_t1 = dwi_tensor.replace('tensor', 'tensor_fa')
    os.system(f"tensor2metric -mask {dwi_mask} -fa {fa_t1} {dwi_tensor} -quiet")
    fa_mni = f'Results_mni/FA/{sub_name}_space-MNI152NLin2009cAsym_fa.nii.gz'
    fa_t1_img = ants.image_read(fa_t1)
    fa_mni_img = t12mni_trans.apply_to_image(fa_t1_img, reference=ref_mni, interpolation='linear')
    ants.image_write(fa_mni_img, fa_mni, ri=False) # ri: if True, return image. This allows for using this function in a pipeline

    #### MD: mean ADC
    md_t1 = dwi_tensor.replace('tensor', 'tensor_md')
    os.system(f"tensor2metric -mask {dwi_mask} -adc {md_t1} {dwi_tensor} -quiet") # mean adc
    md_mni = f'Results_mni/MD/{sub_name}_space-MNI152NLin2009cAsym_md.nii.gz'
    md_t1_img = ants.image_read(md_t1)
    md_mni_img = t12mni_trans.apply_to_image(md_t1_img, reference=ref_mni, interpolation='linear')
    ants.image_write(md_mni_img, md_mni, ri=False)

    #### AD
    ad_t1 = dwi_tensor.replace('tensor', 'tensor_ad')
    os.system(f"tensor2metric -mask {dwi_mask} -ad {ad_t1} {dwi_tensor} -quiet") # mean adc
    ad_mni = f'Results_mni/AD/{sub_name}_space-MNI152NLin2009cAsym_ad.nii.gz'
    ad_t1_img = ants.image_read(ad_t1)
    ad_mni_img = t12mni_trans.apply_to_image(ad_t1_img, reference=ref_mni, interpolation='linear')
    ants.image_write(ad_mni_img, ad_mni, ri=False)
    
    os.remove(dwi_tensor); os.remove(fa_t1); os.remove(md_t1), os.remove(ad_t1)
    return 0

def run(f, this_iter):
    with ProcessPoolExecutor(max_workers=15) as executor:
        results = list(tqdm(executor.map(f, this_iter), total=len(this_iter)))
    return results


all_subs = [x for x in os.listdir('qsiprep_142') if 'sub-sub' in x and 'html' not in x]

run(dwi_measurements_generate, all_subs)
print('finished.')
