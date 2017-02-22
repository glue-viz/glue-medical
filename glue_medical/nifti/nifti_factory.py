from __future__ import absolute_import, division, print_function

import os

import nibabel as nib

from glue.core.data import Data
from glue.config import data_factory
from ..medical_coordinates import Coordinates4DMatrix
from ..utils import flip

__all__ = ['is_nifti_file', 'nifti_reader']


def is_nifti_file(filename):
    """
    Given that nifti files generall only have two file extensions, checking
    their validity is merely a matter of checking for those extensions.
    """
    try:
        if os.path.isdir(filename):
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
    label = label.split('.nii')[0]
    return label


@data_factory(
    label='NIFTI file (.nii or .nii.gz)',
    identifier=is_nifti_file,
    priority=100,
)
def nifti_reader(filepath):
    """
    Reads in a NIFTI file. Uses an affine matrix extracted from nibabel to perform coordinate changes.
    """

    nifti_data = nib.load(filepath)
    matrix = nifti_data.affine
    axis_labels = ['Axial', 'Coronal', 'Saggital']
    array = nifti_data.get_data()

    # NIFTI files are stored with the array indices transposed from the usual
    # Numpy convention of having the first dimension as the last index. But
    # before we transpose the data, we should go through and check whether
    # the matrix has negative diagonal elements, since for those we can flip
    # the data array and adjust the transformation matrix - this will ensure
    # that coordinates always increase to the right/top.
    # Check for negative diagonal matrix elements and flip the data and adjust the
    # transformation
    for idx in range(array.ndim):
        if matrix[idx, idx] < 0:
            matrix[idx, :] = -matrix[idx, :]
            matrix[-1, :] += array.shape[idx] * matrix[idx, :]
            array = flip(array, idx)

    # We now transpose the array so that it has the expected Numpy axis order
    array = array.transpose()

    # Set up the coordinate object using the matrix - for this we keep the
    # matrix in the original order (as well as the axis labels)
    coords = Coordinates4DMatrix(matrix, axis_labels)

    data = [Data(label=nifti_label(filepath))]

    data[0].affine = matrix
    data[0].coords = coords
    data[0].add_component(component=array, label='array')

    return data
