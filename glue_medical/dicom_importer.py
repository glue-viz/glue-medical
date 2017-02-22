# Since the open dataset dialog of glue can't select folders (and this would
# be confusing anyway), we add an 'Import datasets as slices' plugin. In
# future, this could be generalized to support other formats.

from qtpy import QtGui

from glue.config import importer
from glue.utils.qt import messagebox_on_error

from .dicom_factory import dicom_reader


@messagebox_on_error("Error loading DICOM data")
def load(directory):
    return dicom_reader(directory)


@importer("Import DICOM directory as single array")
def import_dicom_directory_as_slices():

    caption = ('Select directory containing DICOM files to load as slices of a'
               'single array')

    dialog = QtGui.QFileDialog(caption=caption)
    dialog.setFileMode(QtGui.QFileDialog.Directory)

    directory = dialog.exec_()

    if directory == QtGui.QDialog.Rejected:
        return []

    directory = dialog.selectedFiles()

    return load(directory[0])
