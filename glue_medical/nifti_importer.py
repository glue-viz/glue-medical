# Since the open dataset dialog of glue can't select folders (and this would
# be confusing anyway), we add an 'Import datasets as slices' plugin. In
# future, this could be generalized to support other formats.

from glue.config import importer
from glue.external.qt import QtGui
from glue.utils.qt import messagebox_on_error

from .nifti_factory import nifti_reader


@messagebox_on_error("Error loading NIFTI data")
def load(nifti_file):
    return nifti_reader(nifti_file)

@importer("Import NIFTI data as a single array")
def import_nifti_file_as_slices():

    caption = ('Select directory containing DICOM files to load as slices of a'
               'single array')

    dialog = QtGui.QFileDialog(caption=caption)
    dialog.setFileMode(QtGui.QFileDialog.AnyFile)

    nifti_file = dialog.exec_()

    if nifti_file == QtGui.QDialog.Rejected:
        return []

    nifti_file = dialog.selectedFiles()
    
    return load(nifti_file[0])
