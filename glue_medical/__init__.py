from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    __version__ = 'undefined'

__all__ = ['__version__', 'setup']


def setup():
    from .dicom_factory import dicom_reader  # noqa
    from .dicom_importer import import_dicom_directory_as_slices  # noqa
