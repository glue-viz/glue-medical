from __future__ import absolute_import, division, print_function

import os
import glob

from ..external import nrrd
import numpy as np

from glue.logger import logger
from glue.core.data import Data
from glue.config import data_factory
from ..medical_coordinates import Coordinates4DMatrix
from ..utils import flip, create_glue_affine

__all__ = ['is_nrrd_file', 'nrrd_reader']


def is_nrrd_file(filename):
    """
    There are actually two nrrd extensions, but one may required a header -- follow up.
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
    Reads in a NRRD file. Uses an affine matrix extracted from pynrrd to perform coordinate changes.
    """

    nrrd_data, nrrd_header = nrrd.read(filepath)
    array = nrrd_data

    # The components for an affine matrix in NRRD format are stored in separate parts of the
    # nrrd_header dictionary. We combine them here through various operations.
    affine_matrix = np.eye(4)
    affine_matrix[0:-1,0:-1] = np.array(nrrd_header['space directions'], dtype=float)
    affine_matrix[0:-1,-1] = np.array(nrrd_header['space origin'])

    # Axis flipping and transposing will be determined by decoding the strings in
    # nrrd_header['space']. Not 100% sure if this works in every case.
    spacing_info = str.split(nrrd_header['space'], '-')
    for axis, row in enumerate(affine_matrix[0:-1]):
        if spacing_info[axis] in ['left', 'posterior', 'inferior']:
            affine_matrix[axis, :] *= -1

    # I am not sure how 4D data or tensor data is represented in NRRD format. 
    axis_labels = ['Axial', 'Coronal', 'Saggital']
    if array.ndim > 3:
        for i in xrange(3, array.ndim + 1):
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

    data = [Data(label=nrrd_label(filepath))]

    data[0].affine = glue_affine
    data[0].export_affine = affine_matrix
    data[0].export_array = array
    data[0].coords = coords
    data[0].add_component(component=glue_array, label='array')

    return data