from glue_medical import setup
from glue_medical.nifti.nifti_factory import nifti_reader
from glue_medical.nrrd.nrrd_factory import nrrd_reader
from glue_medical.dicom.dicom_factory import dicom_reader

setup()

x = nifti_reader('MRBrainTumor2.nii.gz')
y = nrrd_reader('MRBrainTumor2.nrrd')
z = dicom_reader('./glue_medical/tests/data/dicom_directory')

print x
print y
print z

# from glue.core.data_factories.helpers import auto_data
# auto_data('C:/Users/abeers/Pictures/ModelScreenshot.PNG')
# auto_data('C:/Users/abeers/Pictures/ModelScreenshot.png')
# img_data('C:/Users/abeers/Pictures/ModelScreenshot.PNG')