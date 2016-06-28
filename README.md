Experimental Glue medical plugin
==============================

[![Build Status](https://travis-ci.org/glue-viz/glue-medical.svg)](https://travis-ci.org/glue-viz/glue-medical?branch=master)
[![Build status](https://ci.appveyor.com/api/projects/status/kerfkvju3umn75q0/branch/master?svg=true)](https://ci.appveyor.com/project/astrofrog/glue-medical/branch/master)

Requirements
------------

Note that this plugin requires [glue](http://glueviz.org/) to be installed -
see [this page](http://glueviz.org/en/latest/installation.html) for
instructions on installing glue.

In addition, this plugin requires the
[pydicom](http://pydicom.readthedocs.io/en/stable/) package to be installed.
This is easily installed with::

    pip install pydicom

and it will also be installed automatically when you install this plugin (see
below).

Installing
----------

To install the latest developer version from the git repository, you can do:

    pip install https://github.com/glue-viz/glue-medical/archive/master.zip

This will auto-register the plugin with Glue.

Using
-----

At the moment, this plugin provides a reader for DICOM files. You can give
glue either a DICOM file or a directory containing DICOM files. For example,
you can start glue using:

    glue mydata.dcm

or

    glue directory_with_dicom_files

and you can also load files from inside glue. It is not yet possible to load
a directory from the 'Open Data Set' menu in glue.

At the moment, if all the shapes of the DICOM files match inside the directory,
we combine the arrays into an array with a higher dimensionality (for example
we combine 2d arrays into a single 3d array). In future, we will make it
possible for users to control this behavior.

Testing
-------

To run the tests, do:

    py.test glue_medical

at the root of the repository. This requires the [pytest](http://pytest.org)
module to be installed.
