import os
import glob
import shutil
import zipfile
import requests

from ..dicom_factory import is_dicom, dicom_reader

ROOT = os.path.join(os.path.dirname(__file__), 'data')


def test_dicom(tmpdir):

    # We can't include the data in the repository because of the license

    zip_filename = tmpdir.join('BRAINIX.zip').strpath

    data = requests.get('http://www.osirix-viewer.com/datasets/DATA/BRAINIX.zip')

    with open(zip_filename, 'wb') as f:
        f.write(data.content)

    zf = zipfile.ZipFile(zip_filename)
    zf.extractall(tmpdir.strpath)

    base_dir = os.path.join(tmpdir.strpath, 'BRAINIX', 'BRAINIX')

    # Because the paths contain unicode, and extractall can mess with it,
    # we get the next directory level programmatically
    new_base_dir = glob.glob(os.path.join(base_dir, '*'))[0]
    base_dir = os.path.join(base_dir, 'datasets')
    
    # We now rename it to avoid issues
    os.rename(new_base_dir, base_dir)

    assert not is_dicom(base_dir)
    assert is_dicom(os.path.join(base_dir, 'T1-3D-FFE-C - 801'))
    assert is_dicom(os.path.join(base_dir, 'T1-3D-FFE-C - 801', 'IM-0001-0054.dcm'))

    data = dicom_reader(os.path.join(base_dir, 'T1-3D-FFE-C - 801'))[0]
    assert data.shape == (100, 256, 256)

    data = dicom_reader(os.path.join(base_dir, 'T1-3D-FFE-C - 801', 'IM-0001-0054.dcm'))[0]
    assert data.shape == (256, 256)

    hete_dir = os.path.join(tmpdir.strpath, 'heterogeneous')

    os.mkdir(hete_dir)

    shutil.copy2(os.path.join(base_dir, 'T1-3D-FFE-C - 801', 'IM-0001-0054.dcm'),
                 os.path.join(hete_dir, 'file1.dcm'))

    shutil.copy2(os.path.join(base_dir, 'sT2W-FLAIR - 401', 'IM-0001-0017.dcm'),
                 os.path.join(hete_dir, 'file2.dcm'))

    datasets = dicom_reader(hete_dir)
    assert len(datasets) == 2
    assert datasets[0].label == 'file1'
    assert datasets[0].shape == (256, 256)
    assert datasets[1].label == 'file2'
    assert datasets[1].shape == (288, 288)
