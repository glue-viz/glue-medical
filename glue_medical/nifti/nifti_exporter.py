from __future__ import absolute_import, division, print_function

import numpy as np

from glue.core import Subset
from glue.config import data_exporter


__all__ = []


@data_exporter(label='NIFTI Label', extension=['nii', 'nii.gz'])
def nifti_writer(data, filename):
    """
    Write a dataset or a subset to a nifti file.
    Parameters
    ----------
    data: `~glue.core.data.Data` or `~glue.core.subset.Subset`
        The data or subset to export
    """

    if isinstance(data, Subset):
        mask = data.to_mask()
        data = data.data
    else:
        mask = None

    import nibabel as nib

    for cid in data.visible_components:

        comp = data.get_component(cid)

        if comp.categorical:
            # TODO: emit warning
            continue
        else:
            values = comp.data.copy()

        if mask is not None:
            values[~mask] = 0
            values[mask] = 1

        nifti_affine = data.affine
        otuput_nifti = nib.Nifti1Image(values, nifti_affine)
        nib.save(otuput_nifti, filename)