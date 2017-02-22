from __future__ import absolute_import, division, print_function

import os
import glob

import nibabel as nib
import numpy as np

from glue.logger import logger
from glue.core.data import Data
from glue.config import data_factory


__all__ = ['is_nifti_file', 'nifti_reader']


def is_nifti_file(filename):
    """
    Given that nifti files generall only have two file extensions, checking
    their validity is merely a matter of checking for those extensions.
    """
    try:
        if os.path.isdir(filename)
            return False
        if filename.endswith('.nii') or filename.endswith('.nii.gz'):
            return True
        else:
            return False
    except Exception:
        return False


def nifti_label(filename):
    """
    This function just returns the name of the file without the .nii or .nii.gz extension.
    """
    label = os.path.basename(os.path.normpath(filename))
    label = str.split(label, '.nii')[0]
    return label

@data_factory(
    label='NIFTI file (.nii or .nii.gz)',
    identifier=is_nifti_file,
    priority=100,
)
def nifti_reader(source):

    """
    Reads in a NIFTI file.
    """

    nifti_data = nib..load(filepath)
    data = [Data(array=nifti_data.get_data(), label=nifti_label(source))]

    return data
