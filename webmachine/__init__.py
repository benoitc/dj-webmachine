# -*- coding: utf-8 -
#
# This file is part of dj-webmachine released under the MIT license. 
# See the NOTICE for more information.


version_info = (0, 2, 0)
__version__ = ".".join(map(str, version_info))


try:
    from webmachine.api import WM, wm
    from webmachine.resource import Resource
except ImportError:
    import traceback
    traceback.print_exc()

def autodiscover():
    """
    Auto-discover INSTALLED_APPS resource.py modules and fail silently when
    not present. This forces an import on them to register any resource bits they
    may want.
    """

    from django.conf import settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule

    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        # Attempt to import the app's resource module.
        try:
            import_module('%s.resources' % app)
        except:
            if module_has_submodule(mod, 'resources'):
                raise 
