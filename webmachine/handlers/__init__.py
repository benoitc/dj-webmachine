# -*- coding: utf-8 -
#
# This file is part of dj-webmachine released under the MIT license. 
# See the NOTICE for more information.

"""
Interfaces for handling content in CRUD  resources.

To add your own handlers, use the WEBMACHINE_SERIALIZERS setting::

    WEBMACHINE_HANDLERS = [
        
        ("path.to.csv.handler", "text/csv", "csv"),
        ("path.to.txt.handler", "text/plain", "txt"),
   ]


handler is an object inheriting from webmachine.handlers.base.Serializer. 

"""
from django.conf import settings
from django.utils import importlib

BUILTIN_HANDLERS = [
    ("webmachine.handlers.json.JsonHandler", "application/json", "json"),
]

_handlers = {}


def register_handler(modname, ctype, sufx, handlers=None):
    mod = _import_handler(modname)
    if handlers is None:
        _handlers[ctype] = (mod, sufx)
    else:
        handlers[ctype] = (mod, sufx)


def get_handler(ctype, resource):
    if not _handlers:
        _load_handlers()
    return _handlers[ctype][0](resource)

def get_suffix(ctype):
    if not _handlers:
        _load_handlers()
    return _handlers[ctype][1]

def get_handlers():
    if not _handlers:
        _load_handlers()

    return _handlers


def _import_handler(path):
    module, obj = path.rsplit(".", 1)
    mod = importlib.import_module(module)
    handler = eval(obj, mod.__dict__)
    if handler is None:
        raise ImportError("failed to import handler '%s'" % path)
    return handler


def _load_handlers():
    """
    Register built-in and settings-defined handlers. This is done lazily so
    that user code has a chance to (e.g.) set up custom settings without
    needing to be careful of import order.
    """
    global _handlers
    handlers = {}
    for modname, ctype, sufx in BUILTIN_HANDLERS:
        register_handler(modname, ctype, sufx, handlers)
    if hasattr(settings, "WEBMACHINE_HANDLERS"):
        for modname, ctype, sufx in settings.WEBMACHINE_SERIALIZERS:
            register_handler(modname, ctype, sufx, handlers)
    _handlers = handlers
