# -*- coding: utf-8 -
#
# This file is part of dj-apipoint released under the Apache 2 license. 
# See the NOTICE for more information.


import os

if os.environ.get('release') != "true":

    minor_tag = ""
    try:
        from apipoint.util import popen3

        stdin, stdout, stderr = popen3("git rev-parse --short HEAD --")
        error = stderr.read()
        if not error:
            git_tag = stdout.read()[:-1]
            minor_tag = ".%s-git" % git_tag
    except OSError:        
        pass
else:
    minor_tag = ""
    

version_info = (0, 1, "0%s" % minor_tag)
__version__ = ".".join(map(str, version_info))

