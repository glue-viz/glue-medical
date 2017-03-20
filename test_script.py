from glue_medical import setup
from glue_medical.nifti.nifti_factory import nifti_reader

from glue_medical.nrrd.nrrd_factory import nrrd_reader


setup()

nrrd_reader('MRBrainTumor2.nrrd')