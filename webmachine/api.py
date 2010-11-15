# -*- coding: utf-8 -
#
# This file is part of dj-webmachine released under the MIT license. 
# See the NOTICE for more information.

"""
webmachine.descriptors

This module allows creation of web Resources based on their description.
Basically you create an ApiDescriptor object defining accepted methods,
accepted query args depending on their methods, used serializers and
functionto manage differents request methods.

This module will also allows automatic building of documentation and
clients.

See ModelDescriptor and QueryDescriptor for generic api descriptor
allowing you to expose models and query.
"""

from webmachine.resource import Resource, RESOURCE_METHODS

def validate_ctype(value):
    if isinstance(value, basestring):
        return [value]
    elif not isinstance(value, list) and value is not None:
        raise TypeError("'%s' should be a list or a string, got %s" %
                (value, type(value)))

    return value


def serializer_cb(serializer, method):
    if hasattr(serializer, method):
        return getattr(serializer, method)
    return serializer

def wrap_ctype(fun, cb):
    def _wrapped(req, resp):
        if req.method == "DELETE":
            return cb(resp._container)
        return cb(fun(req, resp))
    return _wrapped

def build_ctypes(ctypes, fun, method):

    for ctype in ctypes:
        if isinstance(ctype, tuple):
            cb = serializer_cb(ctype[1], method) 
            yield ctype[0], wrap_ctype(fun, cb)
        else:
            yield ctype, fun


class WMResource(Resource):

    def __init__(self, pattern, fun, **kwargs):
        self.set_pattern(pattern, **kwargs)

        methods = kwargs.get('methods') or ['GET', 'HEAD']
        if isinstance(methods, basestring):
            methods = [methods]

        elif not isinstance(methods, (list, tuple,)):
            raise TypeError("methods should be list or a tuple, '%s' provided" % type(methods))

        # associate methods to the function
        self.methods = {}
        for m in methods:
            self.methods[m.upper()] = fun

        # build content provided list
        provided = validate_ctype(kwargs.get('provided') or \
                ['text/html'])
        self.provided = list(build_ctypes(provided, fun, "serialize"))

        # build content accepted list
        accepted = validate_ctype(kwargs.get('accepted'))
        if accepted is not None:
            self.accepted = list(build_ctypes(accepted, fun, "unserialize"))

        self.kwargs = kwargs

        # override method if needed
        for k, v in self.kwargs.items():
            if k in RESOURCE_METHODS:
                setattr(self, k, self.wrap(v))           

    def set_pattern(self, pattern, **kwargs):
        self.url = (pattern, kwargs.get('name'))

    def update(self, fun, **kwargs):
        methods = kwargs.get('methods') or ['GET', 'HEAD']
        if isinstance(methods, basestring):
            methods = [methods]
        elif not isinstance(methods, (list, tuple,)):
            raise TypeError("methods should be list or a tuple, '%s' provided" % type(methods))

        # associate methods to the function
        self.methods = {}
        for m in methods:
            self.methods[m.upper()] = fun

        # we probably should merge here
        provided = validate_ctype(kwargs.get('provided'))
        if provided is not None:
            provided = list(build_ctypes(provided, fun, "serialize"))
            self.provided.extend(provided)
        
        accepted = validate_ctype(kwargs.get('accepted'))
        if accepted is not None:
            accepted = list(build_ctypes(accepted, fun, "unserialize"))
            self.accepted.extend(accepted)

    def wrap(self, f,):
        def _wrapped(req, resp):
            return f(req, resp)
        return _wrapped

    #### resources methods

    def allowed_methods(self, req, resp):
        return self.methods.keys()

    def format_suffix_accepted(self, req, resp):
        if 'formats' in self.kwargs:
            return self.kwargs['formats']
        return []

    def content_types_accepted(self, req, resp):
        if not self.accepted and req.method not in self.methods:
            return None

        fun = self.methods[req.method]
        if not self.accepted:
            return [("text/html", self.wrap(fun))]
       
        return [(c, self.wrap(f)) for c, f in self.accepted]
        
    def content_types_provided(self, req, resp):
        fun = self.methods[req.method]
        if not self.provided:
            return [("text/html", self.wrap(fun))]

        return [(c, self.wrap(f)) for c, f in self.provided]

    def delete(self, req, resp):
        fun = self.methods['DELETE']
        ret = self.wrap(fun)
        if isinstance(ret, basestring):
            resp._container = ret
            return True
        return ret

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url
        url_kwargs = self.kwargs.get('url_kwargs') or {}

        if len(self.url) >2:
            url1 =url(self.url[0], self, name=self.url[1], kwargs=url_kwargs)
        else:
            url1 =url(self.url[0], self, kwargs=url_kwargs)

        return patterns('', url1)


class WM(object):

    def __init__(self, name="webmachine", version=None):
        self.name = name
        self.version = version
        self.resources = {}
        self.routes = []

    def route(self, pattern, **kwargs):
        """ A decorator that is used to register a new resource using
        this function to return response
        
        
        """
        def _decorated(func):
            self.add_route(pattern, func, **kwargs)
            return func
        return _decorated

    def add_route(self, pattern, func, **kwargs):
        if pattern in self.resources:
            res = self.resources[pattern]
            res.update(func, **kwargs)
        else:
            res = WMResource(pattern, func, **kwargs)
        self.resources[pattern] = res

        self.routes.append((pattern, func, kwargs))
        # associate the resource to the function
        setattr(func, "_wmresource", res)


    def get_urls(self):
        from django.conf.urls.defaults import patterns
        urlpatterns = patterns('')
        for pattern, resource in self.resources.items():
            urlpatterns += resource.get_urls()
        return urlpatterns

    urls = property(get_urls)

wm = WM()
