#!/usr/bin/env python

from __future__ import print_function

from setuptools import setup, find_packages

entry_points = """
[glue.plugins]
glue_medical=glue_medical:setup
"""

try:
    import pypandoc
    LONG_DESCRIPTION = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    with open('README.md') as infile:
        LONG_DESCRIPTION = infile.read()

with open('glue_medical/version.py') as infile:
    exec(infile.read())

setup(name='glue_medical',
      version=__version__,
      description='Plugin for glue to support medical data',
      long_description=LONG_DESCRIPTION,
      url="https://github.com/glue-viz/glue-medical",
      author='',
      author_email='',
      packages = find_packages(),
      package_data={},
      entry_points=entry_points,
      install_requires=['numpy', 'glueviz', 'pydicom']
    )
