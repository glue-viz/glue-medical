def setup():
    from .dicom.dicom_factory import dicom_reader
    from .dicom.dicom_importer import import_dicom_directory_as_slices
    from .nifti.nifti_factory import nifti_reader
    import nifti.nifti_exporter
    from .nrrd.nrrd_factory import nrrd_reader
