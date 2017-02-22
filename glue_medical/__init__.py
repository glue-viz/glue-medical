def setup():
    from .dicom.dicom_factory import dicom_reader
    from .dicom.dicom_importer import import_dicom_directory_as_slices
    from .nifti.nifti_factory import nifti_reader
    from .nifti.nifti_exporter import nifti_writer
    # from .nifti.nifti_factory import nifti_reader
    # from .nrrd.nrrd_factory import nrrd_reader
