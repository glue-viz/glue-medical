from glue_medical import setup
from glue_medical.nifti.nifti_factory import nifti_reader
from glue_medical.nrrd.nrrd_factory import nrrd_reader


setup()

x = nrrd_reader('MRBrainTumor2.nrrd')

print x

# from glue.core.data_factories.helpers import auto_data
# auto_data('C:/Users/abeers/Pictures/ModelScreenshot.PNG')
# auto_data('C:/Users/abeers/Pictures/ModelScreenshot.png')
# img_data('C:/Users/abeers/Pictures/ModelScreenshot.PNG')