#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of dj-webmachine released under the Apache 2 license. 
# See the NOTICE for more information.

import os
import sys

if not hasattr(sys, 'version_info') or sys.version_info < (2, 5, 0, 'final'):
    raise SystemExit("Compono requires Python 2.5 or later.")

from setuptools import setup, find_packages

from webmachine import __version__

setup(
    name = 'dj-webmachine',
    version = __version__,
    description = 'Minimal Django Resource framework.',
    long_description = file(
        os.path.join(
            os.path.dirname(__file__),
            'README.rst'
        )
    ).read(),
    author = 'Benoit Chesneau',
    author_email = 'benoitc@e-engura.org',
    license = 'BSD',
    url = 'http://github.com/benoitc/dj-webmachine',
    classifiers = [
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Application Frameworks',

    ],
    
    zip_safe = False,
    packages = find_packages(),
    include_package_data = True,
    
    install_requires = [
        'setuptools',
        'django',
    ],
    
    test_suite = 'nose.collector',

)
