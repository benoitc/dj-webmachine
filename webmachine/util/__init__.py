# -*- coding: utf-8 -
#
# This file is part of dj-apipoint released under the MIT license. 
# See the NOTICE for more information.

import random
import time

CHARS = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
def keygen(len):
    return ''.join([random.choice(CHARS) for i in range(len)])

def generate_timestamp():
    """Get seconds since epoch (UTC)."""
    return int(time.time())

def generate_random(length=8):
    """Generate pseudorandom number."""
    return ''.join([str(random.randint(0, 9)) for i in range(length)])

def coerce_put_post(request):
    """
    Django doesn't particularly understand REST.
    In case we send data over PUT, Django won't
    actually look at the data and load it. We need
    to twist its arm here.
    
    The try/except abominiation here is due to a bug
    in mod_python. This should fix it.

    function from Piston
    """
    if request.method == "PUT":
        # Bug fix: if _load_post_and_files has already been called, for
        # example by middleware accessing request.POST, the below code to
        # pretend the request is a POST instead of a PUT will be too late
        # to make a difference. Also calling _load_post_and_files will result 
        # in the following exception:
        #   AttributeError: You cannot set the upload handlers after the upload has been processed.
        # The fix is to check for the presence of the _post field which is set 
        # the first time _load_post_and_files is called (both by wsgi.py and 
        # modpython.py). If it's set, the request has to be 'reset' to redo
        # the query value parsing in POST mode.
        if hasattr(request, '_post'):
            del request._post
            del request._files
        
        try:
            request.method = "POST"
            request._load_post_and_files()
            request.method = "PUT"
        except AttributeError:
            request.META['REQUEST_METHOD'] = 'POST'
            request._load_post_and_files()
            request.META['REQUEST_METHOD'] = 'PUT'
            
        request.PUT = request.POST

def serialize_list(value):
    if value is None:
        return
    if isinstance(value, unicode):
        return str(value)
    elif isinstance(value, str):
        return value
    else:
        return ', '.join([str(v) for v in value])

