# -*- coding: utf-8 -
#
# This file is part of dj-webmachine released under the MIT license. 
# See the NOTICE for more information.

import datetime

# import json
try:
    _json = __import__('json') 
except ImportError:
    try:
        import simplejson as _json
    except ImportError:
        import django.utils.simplejson as _json

from django.core.serializers.json import DjangoJSONEncoder

from webmachine.handlers import base

def json_decode(data, model=None):
    return _json.loads(data)

def json_encode(obj):
    return _json.dumps(obj, cls=DjangoJSONEncoder)

class JsonHandler(base.Handler):

    def encode(self, data):
        return json_encode(data)


    def decode(self, data):
        return json_decode(data)


