from __future__ import absolute_import, division, print_function

import os

import nibabel as nib
import numpy as np

from glue.core.data import Data
from glue.config import data_factory
from ..medical_coordinates import Coordinates4DMatrix
from ..utils import flip, create_glue_affine

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
    affine_matrix = nifti_data.affine
    array = nifti_data.get_data()

    # Add axis labels as necessary. Traditionally, Niftis files have the time dimension in the fourth
    # axis slot, and the Vector/Tensor dimension in the 5th slot, e.g. for Diffusion Tensor Imaging (DTI)
    axis_labels = ['Axial', 'Coronal', 'Saggital']
    if array.ndim >= 4:
        axis_labels += ['Time']
    if array.ndim >= 5:
        axis_labels += ['Tensor']
    if array.ndim > 6:
        for i in xrange(5, array.ndim + 1):
            axis_labels += ['Axis' + str(i)]

    # I create a "glue_affine", which is a regularized internal orientation for affine matrices in glue.
    # This is because I found some differences from what I understand to be orientation conventions in
    # the medical world, and what they seemed to be in glue. To make things easy, I just transfer those
    # conventions into the same orientation every time. This solution is a bit circuitous, so this code
    # should be revisited.
    glue_array, glue_affine = create_glue_affine(array, affine_matrix)

    # Set up the coordinate object using the matrix - for this we keep the
    # matrix in the original order (as well as the axis labels)
    coords = Coordinates4DMatrix(glue_affine, axis_labels)

    data = [Data(label=nifti_label(filepath))]

    data[0].affine = glue_affine
    data[0].export_affine = affine_matrix
    data[0].export_array = array
    data[0].coords = coords
    data[0].add_component(component=glue_array, label='array')

    return data
