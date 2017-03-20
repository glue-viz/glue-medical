import os
import glob
import shutil
import zipfile
import requests

from ..dicom_factory import is_dicom, dicom_reader

DATA = os.path.join(os.path.dirname(__file__), 'data')


def test_dicom(tmpdir):

    empty_dir = tmpdir.strpath

    assert not is_dicom(empty_dir)
    assert is_dicom(os.path.join(DATA, 'dicom_directory'))
    assert is_dicom(os.path.join(DATA, 'CT_small.dcm'))

    data = dicom_reader(os.path.join(DATA, 'dicom_directory'))[0]
    assert data.shape == (7, 16, 16)

    data = dicom_reader(os.path.join(DATA, 'CT_small.dcm'))[0]
    assert data.shape == (128, 128)

    datasets = dicom_reader(os.path.join(DATA, 'dicom_heterogeneous_directory'))
    assert len(datasets) == 2
    assert datasets[0].label == 'file1'
    assert datasets[0].shape == (128, 128)
    assert datasets[1].label == 'file2'
    assert datasets[1].shape == (16, 16)
