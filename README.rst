Experimental Glue medical plugin
================================

|Build Status|

Requirements
------------

Note that this plugin requires `glue <http://glueviz.org/>`__ to be
installed - see `this
page <http://glueviz.org/en/latest/installation.html>`__ for
instructions on installing glue.

In addition, this plugin requires the
`GDCM <http://gdcm.sourceforge.net/>`__ and
`pydicom <http://pydicom.readthedocs.io/en/stable/>`__ packages to be
installed. If you are using conda, you can easily install these with::

    conda install -c conda-forge gdcm pydicom

Installing
----------

To install the latest version of this plugin, you can do::

    pip install glue-medical

This will auto-register the plugin with Glue.

Using
-----

At the moment, this plugin provides a reader for DICOM files. You can
give glue either a DICOM file or a directory containing DICOM files. For
example, you can start glue using::

    glue mydata.dcm

or::

    glue directory_with_dicom_files

and you can also load files from inside glue. It is not yet possible to
load a directory from the 'Open Data Set' menu in glue.

At the moment, if all the shapes of the DICOM files match inside the
directory, we combine the arrays into an array with a higher
dimensionality (for example we combine 2d arrays into a single 3d
array). In future, we will make it possible for users to control this
behavior.

Testing
-------

To run the tests, do::

    pytest glue_medical

at the root of the repository. This requires the
`pytest <http://pytest.org>`__ module to be installed.

.. |Build Status| image:: https://github.com/glue-viz/glue-medical/actions/workflows/ci_workflows.yml/badge.svg
   :target: https://github.com/glue-viz/glue-medical/actions/workflows/ci_workflows.yml
