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

popen3 = None
try:#python 2.6, use subprocess
    import subprocess
    subprocess.Popen  # trigger ImportError early
    closefds = os.name == 'posix'
    
    def popen3(cmd, mode='t', bufsize=0):
        p = subprocess.Popen(cmd, shell=True, bufsize=bufsize,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
            close_fds=closefds)
        p.wait()
        return (p.stdin, p.stdout, p.stderr)
except ImportError:
    subprocess = None
    try:
        popen3 = os.popen3
    except ImportError:
        popen3 = None

DEVELOP = "develop" in sys.argv

version = __version__
if DEVELOP and popen3 is not None:
    minor_tag = ""
    try:
        stdin, stdout, stderr = popen3("git rev-parse --short HEAD --")
        error = stderr.read()
        if not error:
            git_tag = stdout.read()[:-1]
            minor_tag = ".%s-git" % git_tag
    except OSError:        
        pass
    version = "%s%s" % (version, minor_tag)



setup(
    name = 'dj-webmachine',
    version = version,
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
        'License :: OSI Approved :: MIT License',
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
        'django'
    ],
    
    test_suite = 'nose.collector',

)
