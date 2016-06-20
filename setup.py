#!/usr/bin/env python

from os import path
# Always prefer setuptools over distutils
from setuptools import setup, find_packages


setupdict = dict(
   name='xii',
   version='1.0.0',
   description='Easy virtual machine spawning',
   url='https://github.com/felixsch/xii',
   # Author details
   author='Felix Schnizlein',
   author_email='felix@schnizle.in',
   license='GPL-3.0',
   # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
   classifiers=[
      'Development Status :: 5 - Production/Stable'
      #
      # The license:
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      # Supported Python versions:
      'Programming Language :: Python :: 2.7'
   ],
   keywords='xii',
   include_package_data = True,
   packages=find_packages('src'),
   package_dir={'': 'src'},
   extras_require={
        'test': ['pytest', 'coverage'],
   },
   entry_points={
        'console_scripts': [
            'xii=xii:main',
        ],
    },
)

setup(**setupdict)
