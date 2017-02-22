def setup():
    from .dicom_factory import dicom_reader
    from .dicom_importer import import_dicom_directory_as_slices
    from .nifti_factory import nifti_reader
    from .nifti_importer import import_nifti_file_as_slices
