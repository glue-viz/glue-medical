from __future__ import absolute_import, division, print_function

import os
import glob

from ...external.nrrd import
import numpy as np

from glue.logger import logger
from glue.core.data import Data
from glue.config import data_factory
from ..medical_coordinates import Coordinates4DMatrix


__all__ = ['is_nifti_file', 'nifti_reader']


def is_nrrd_file(filename):
    """
    Given that nifti files generall only have two file extensions, checking
    their validity is merely a matter of checking for those extensions.
    """
    try:
        if os.path.isdir(filename):
            return False
        if filename.endswith('.nrrd'):
            return True
        else:
            return False
    except Exception:
        return False


def nrrd_label(filename):
    """
    This function just returns the name of the file without the .nii or .nii.gz extension.
    """
    label = os.path.basename(os.path.normpath(filename))
    label = label.split('.nrrd')[0]
    return label

@data_factory(
    label='NRRD file (.nrrd)',
    identifier=is_nrrd_file,
    priority=100,
)
def nrrd_reader(filepath):

    """
    Reads in a NIFTI file. Uses an affine matrix extracted from nibabel to perform coordinate changes.
    """

    nifti_data = nib.load(filepath)
    matrix = nifti_data.affine
    axis_labels = ['Saggital','Coronal','Axial']
    array = nifti_data.get_data()

    coords = Coordinates4DMatrix(matrix, axis_labels)

    data = [Data(label=nifti_label(filepath))]

    data[0].affine = matrix
    data[0].coords = coords
    data[0].add_component(component=array, label='array')

    return data
