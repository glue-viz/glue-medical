from glue_medical import setup
from glue_medical.nifti.nifti_factory import nifti_reader

setup()

nifti_reader('MRBrainTumor2.nii.gz')