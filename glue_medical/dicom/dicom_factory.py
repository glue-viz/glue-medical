from __future__ import absolute_import, division, print_function

import os
import glob
from collections import defaultdict

try:
    import pydicom
except ImportError:
    import dicom as pydicom
import numpy as np

from glue.logger import logger
from glue.core.data import Data
from glue.config import data_factory
from ..medical_coordinates import Coordinates4DMatrix
from ..utils import flip, create_glue_affine, grab_files_recursive


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

def dicom_object_label(dicom, tags):

    """
    We want to identify dicoms by their tags, but not every DICOM file has every tag.
    This provides an option to cycle through a list of tags until a winning identifier
    is found.
    """

    for tag in tags:
        try:
            return dicom.data_element(tag).value
        except:
            continue

    return 'Unknown Series'


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
    Read a DICOM file or a directory with DICOM files.

    Some considerations about DICOM:
    There are many situations where DICOMs from different imaging series may
    be in the same folder, or DICOMs from the same imaginge series might be in
    different folders. Because of this, there should be functionality to recursively
    search directories, and/or load multiple files at once.

    The latter case in which DICOMs from one series are split across multiple filenames
    is less likely. However, there is another bizarre DICOM convention that will likely
    make recursive file-searching and multiple file-loading more attractive. Most DICOM folders
    are given totally inscrutable names, like a series of 20-30 numbers divided by periods.
    It is basically impossible to tell which series is which, or which scan date is which, by
    the folder name alone. Thus, it is unlikely that a user will be loading a specific folder
    directly, but rather the high-level patient folder that contains ALL imaging series available
    for this patient. This will contain many different imaging series that will need to be parsed
    at some later point.

    Lastly, there are always many edge-cases with DICOM, which makes it important to have
    relatively friendly error-catching. I have yet to find a DICOM reader which can handle
    every sort of DICOM file, and because DICOM tags are non-standardized, the tags that we
    expect to extract information may not be present, or present under some other name. While
    non-Python packages like ITK and 3D-Slicer can navigate these pitfalls relatively well,
    there is no good solution in Python as far as I know (would love to be proven wrong though..)
    """

    if os.path.isdir(source):

        # We first iterate through all available files (non-recursively for now).
        # check if they are DICOM files, and if so, sort them into a dictionary based
        # on the "SeriesInstanceUID" DICOM tag. This tag should be unique to a specific
        # imaging set, but it may be necessary to check multiple tags to establish uniqueness
        # for particularly strange image sets.
        unique_series = defaultdict(list)
        for filename in sorted(grab_files_recursive(source)):
            if is_dicom_file(filename):
                dicom_object = pydicom.read_file(filename)
                UID = dicom_object.data_element('SeriesInstanceUID').value
                unique_series[UID] += [dicom_object]

        # If there are no DICOM files, we raise an error.
        if len(unique_series) == 0:
            raise Exception("No DICOM files found in directory: {0}".format(source))

        # We then grab output volumes and store them in a dict based on 'SeriesDescription',
        # which should be a good identifier of the imaging data in question. We can also include
        # "PatientName" for specifity's sake.
        output_data = []
        for UID, current_dicoms in unique_series.iteritems():

            # Check if there is only one DICOM file. At some future point, orientation information should
            # be passed on to the 2D data too, but for now this will do.
            if len(current_dicoms) == 1:
                output_data += [Data(array=current_dicoms[0].pixel_array, label=dicom_object_label(current_dicoms[0], ['SeriesDescription']))]

            else:
                # Sort DICOMs by Instance Number. This is usually a proxy for slice order.
                dicom_instances = [x.data_element('InstanceNumber').value for x in current_dicoms]
                current_dicoms = [x for _,x in sorted(zip(dicom_instances,current_dicoms))]
                first_dicom, last_dicom = current_dicoms[0], current_dicoms[-1]

                try:

                    # Extract patient position information from the DICOM header required for affine creation.
                    output_affine = np.eye(4)
                    first_image_position_patient = np.array(first_dicom.data_element('ImagePositionPatient').value).astype(float)
                    last_image_position_patient = np.array(last_dicom.data_element('ImagePositionPatient').value).astype(float)
                    image_orientation_patient = np.array(first_dicom.data_element('ImageOrientationPatient').value).astype(float)
                    pixel_spacing_patient = np.array(first_dicom.data_element('PixelSpacing').value).astype(float)

                    # Create DICOM Space affine from DICOM header. For more information on this process, see:
                    # http://nipy.org/nibabel/dicom/dicom_orientation.html
                    output_affine[0:3, 0] = pixel_spacing_patient[0] * image_orientation_patient[0:3]
                    output_affine[0:3, 1] = pixel_spacing_patient[1] * image_orientation_patient[3:6]
                    output_affine[0:3, 2] = (first_image_position_patient - last_image_position_patient) / (1 - len(current_dicoms))
                    output_affine[0:3, 3] = first_image_position_patient

                    # Transformations from DICOM affine to NIFTI affine format.
                    # DICOM data is stored in [columns, rows], rather than [rows, columns]. We first fix this.
                    rc_flip = np.eye(4)
                    rc_flip[0:2,0:2] = [[0,1],[1,0]]
                    
                    # Left and right are also flipped in DICOM data. This may be a natural consequence of the previous
                    # transformation -- not sure yet.
                    neg_flip = np.eye(4)
                    neg_flip[0:2,0:2] = [[-1,0],[0,-1]]
                    
                    # Apply transformations in (LR_FLIP * AFFINE * ROW_COLUMN_FLIP) format.
                    output_affine = np.matmul(neg_flip, np.matmul(output_affine, rc_flip))

                    # Create 3D array data from DICOMs. There are some instances I've found where corrupted data (maybe?)
                    # is not the same shape as the rest of the data. We error check slices for this reason.
                    output_shape = current_dicoms[0].pixel_array.shape
                    output_array = []
                    print(output_shape)
                    for i in xrange(len(current_dicoms)):
                        try:
                            output_array += [current_dicoms[i].pixel_array]
                        except:
                            logger.info("Error loading slice at position", i, "for UID", UID)
                    output_array = np.stack(output_array, -1)

                    # Greater than 3D data is not supported.
                    axis_labels = ['Axial', 'Coronal', 'Saggital']
                    if output_array.ndim > 3:
                        for i in xrange(3, output_array.ndim + 1):
                            axis_labels += ['Axis' + str(i)]

                    # I create a "glue_affine", which is a regularized internal orientation for affine matrices in glue.
                    # This is because I found some differences from what I understand to be orientation conventions in
                    # the medical world, and what they seemed to be in glue. To make things easy, I just transfer those
                    # conventions into the same orientation every time. This solution is a bit circuitous, so this code
                    # should be revisited.
                    glue_array, glue_affine = create_glue_affine(output_array, output_affine)

                    # Set up the coordinate object using the matrix - for this we keep the
                    # matrix in the original order (as well as the axis labels)
                    coords = Coordinates4DMatrix(glue_affine, axis_labels)

                    data = [Data(label=dicom_object_label(current_dicoms[0], ['SeriesDescription']))]

                    data[0].affine = glue_affine
                    data[0].export_affine = output_affine
                    data[0].export_array = output_array
                    data[0].coords = coords
                    data[0].add_component(component=glue_array, label='array')

                    output_data += data

                except:

                    logger.info("Error loading DICOM series at..", UID)

        return output_data

    else:

        ds = pydicom.read_file(source)
        data = [Data(array=ds.pixel_array, label=dicom_label(source))]

        return data
