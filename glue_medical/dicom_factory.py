from __future__ import absolute_import, division, print_function

import os
import glob

try:
    import pydicom
except ImportError:
    import dicom as pydicom
import numpy as np

from glue.logger import logger
from glue.core.data import Data
from glue.config import data_factory


__all__ = ['is_dicom', 'dicom_reader']


def is_dicom_file(filename):
    """
    This function is used to check whether a file is in the DICOM format. We
    do this by checking that bytes 129 to 132 are DICM. See

    http://stackoverflow.com/questions/4792727/validating-dicom-file

    for more details
    """
    try:
        with open(filename, 'rb') as f:
            f.read(128)
            if f.read(4) == b'DICM':
                return True
            else:
                return False
    except Exception:
        return False


def dicom_label(filename):
    """
    This function just returns the name of the file without the .dcm extension
    if present. We don't strip off any other extensions in case they are part
    of the name and not actually an extension.
    """
    label = os.path.basename(os.path.normpath(filename))
    if label.endswith('.dcm'):
        label = label[:-4]
    return label



def is_dicom(source):
    """
    Determine if the source is either a DICOM file or a directory that
    contains at least one DICOM file.
    """
    if os.path.isdir(source):
        for filename in glob.glob(os.path.join(source, '*')):
            if is_dicom_file(filename):
                return True
        return False
    else:
        return is_dicom_file(source)


@data_factory(
    label='DICOM file or directory',
    identifier=is_dicom,
    priority=100,
)
def dicom_reader(source):
    """
    Read a DICOM file or a directory with DICOM files
    """

    if os.path.isdir(source):

        # We are dealing with a directory which should contain DICOM files. At
        # this point, we need to check whether the directory contains zero,
        # one, or more DICOM datasets.

        arrays = {}
        for filename in glob.glob(os.path.join(source, '*')):
            if is_dicom_file(filename):
                logger.info("Reading DICOM data from {0}".format(filename))
                ds = pydicom.read_file(filename)
                arrays[dicom_label(filename)] = ds.pixel_array
            else:
                logger.info("Not a DICOM file: {0}".format(filename))

        # If there are no DICOM files, we raise an error, and if there is one
        # then we are done!

        if len(arrays) == 0:
            raise Exception("No DICOM files found in directory: {0}".format(source))
        elif len(arrays) == 1:
            label = list(arrays.keys())[0]
            return [Data(array=arrays[label], label=label)]

        # We now check whether all the shapes of the DICOM files are the same,
        # and if so, we merge them into a single file.

        labels = sorted(arrays)
        ref_shape = arrays[labels[0]].shape

        for label in labels[1:]:

            if arrays[label].shape != ref_shape:
                break

        else:

            # Since we are here, the shapes of all the DICOM files match, so
            # we can construct a higher-dimensional array.

            # Make sure arrays are sorted while constructing array
            array = np.array([arrays[label] for label in labels])

            # We flip the array here on that in most cases we expect that the
            # scan will start at the top of e.g. the body and move downwards.
            array = array[::-1]

            return [Data(array=array, label=dicom_label(source))]

        # If we are here, the shapes of the DICOM files didn't match, so we
        # simply return one Data object per DICOM file.
        return [Data(array=arrays[label], label=label) for label in labels]

    else:

        ds = pydicom.read_file(source)
        data = [Data(array=ds.pixel_array, label=dicom_label(source))]

    return data
