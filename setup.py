#!/usr/bin/env python

import sys
# Always prefer setuptools over distutils
try:
    from setuptools import setup, find_packages
except ImportError:
    print("xii requires setuptools in order to be installed.")
    sys.exit(1)


setupdict = dict(
        name='xii',
        keywords='xii',
        version='1.0.0',
        description='Easy virtual machine spawning',
        url='https://github.com/xii/xii',
        author='Felix Schnizlein',
        author_email='xii@schnizle.in',
        license='GPL-3.0',
        classifiers=[
            'Development Status :: 3 - Alpha'
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Operating System :: POSIX',
            'Topic :: Utilities',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            ],
        install_requires=['paramiko', "PyYAML", 'setuptools', 'pycrypto'],
        include_package_data=True,
        packages=find_packages('src'),
        package_dir={'': 'src'},
        data_files=[('config', ['defaults/config.yml'])],
        entry_points={'console_scripts': ['xii=xii:main']}
        )

setup(**setupdict)
