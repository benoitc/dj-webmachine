# -*- coding: utf-8 -
#
# This file is part of dj-webmachine released under the MIT license. 
# See the NOTICE for more information.

"""
Minimal API building
++++++++++++++++++++

Combinating the power of Django and the :ref:`resources <resources>` it's relatively easy to buid an api. The process is also eased using the WM object. dj-webmachine offer a way to create automatically resources by using the ``route`` decorator.

Using this decorator, our helloworld example can be rewritten like that:

.. code-block:: python


    from webmachine.ap import wm

    import json
    @wm.route(r"^$")
    def hello(req, resp):
        return "<html><p>hello world!</p></html>"


    @wm.route(r"^$", provided=[("application/json", json.dumps)])
    def hello_json(req, resp):
        return {"ok": True, "message": "hellow world"}

and the urls.py:

.. code-block:: python

    from django.conf.urls.defaults import *

    import webmachine

    webmachine.autodiscover()

    urlpatterns = patterns('',
        (r'^', include(webmachine.wm.urls))
    )

The autodiscover will detect all resources modules and add then to the
url dispatching. The route decorator works a little like the one in
bottle_ or for that matter flask_ (though bottle was the first). 

This decorator works differently though. It creates full
:class:`webmachine.resource.Resource` instancse registered in the wm
object. So we are abble to provide all the features available in a
resource:

 - settings which content is accepted, provided
 - assiciate serializers to the content types
 - throttling
 - authorization
"""

from webmachine.resource.base import Resource, RESOURCE_METHODS

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

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

def build_ctypes(ctypes,method):
    for ctype in ctypes:
        if isinstance(ctype, tuple):
            cb = serializer_cb(ctype[1], method) 
            yield ctype[0], cb
        else:
            yield ctype, lambda v: v


class RouteResource(Resource):

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
        self.provided = list(build_ctypes(provided, "serialize"))

        # build content accepted list
        accepted = validate_ctype(kwargs.get('accepted')) or []
        self.accepted = list(build_ctypes(accepted, "unserialize"))
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
        for m in methods:
            self.methods[m.upper()] = fun

        # we probably should merge here
        provided = validate_ctype(kwargs.get('provided'))
        if provided is not None:
            provided = list(build_ctypes(provided, "serialize"))
            self.provided.extend(provided)
        
        accepted = validate_ctype(kwargs.get('accepted'))
        if accepted is not None:
            accepted = list(build_ctypes(accepted, "unserialize"))
            self.accepted.extend(accepted)


    def wrap(self, f, cb=None):
        def _wrapped(req, resp):
            if cb is not None:
                return cb(f(req, resp))
            return f(req, resp)
        return _wrapped

    def first_match(self, media, expect):
        for key, value in media:
            if key == expect:
                return value
        return None

    def accept_body(self, req, resp):
        ctype = req.content_type or "application/octet-stream"
        mtype = ctype.split(";", 1)[0]
        funload = self.first_match(self.accepted, mtype)
        if funload is None:
            raise webmachine.exc.HTTPUnsupportedMediaType()
        req._raw_post_data = funload(req.raw_post_data)
        if isinstance(req._raw_post_data, basestring):
            req._stream = StringIO(req._raw_post_data)

        fun = self.methods[req.method]
        body = fun(req, resp)
        if isinstance(body, tuple):
            resp._container, resp.location = body
        else:
           resp._container = body

        return self.return_body(req, resp)

    def return_body(self, req, resp):
        fundump = self.first_match(self.provided, resp.content_type)
        if fundump is None:
            raise webmachine.exc.HTTPInternalServerError()
        resp._container = fundump(resp._container)
        if not isinstance(resp._container, basestring):
            resp._is_tring = False
        else:
            resp._container = [resp._container]
            resp._is_string = True
        return resp._container


    #### resources methods

    def allowed_methods(self, req, resp):
        return self.methods.keys()

    def format_suffix_accepted(self, req, resp):
        if 'formats' in self.kwargs:
            return self.kwargs['formats']
        return []

    def content_types_accepted(self, req, resp):
        if not self.accepted:
            return None
        return [(c, self.accept_body) for c, f in self.accepted]
        
    def content_types_provided(self, req, resp):
        fun = self.methods[req.method]
        if not self.provided:
            return [("text/html", self.wrap(fun))]

        return [(c, self.wrap(fun, f)) for c, f in self.provided]

    def delete_resource(self, req, resp):
        fun = self.methods['DELETE']
        ret = fun(req, resp)
        if isinstance(ret, basestring) or hasattr(ret, '__iter__'):
            resp._container = ret
            self.return_body(req, resp)
            return True
        return False

    def post_is_create(self, req, resp):
        if req.method == 'POST':
            return True
        return False

    def created_location(self, req, resp):
        return resp.location

    def process_post(self, res, resp):
        return self.accept_body(req, resp)

    def multiple_choices(self, req, resp):
        return False

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
        this function to return response.

        **Parameters**

        :attr pattern: regular expression, like the one you give in
        your urls.py

        :attr methods: methods accepted on this function

        :attr provides: list of provided contents tpes and associated
        serializers::

            [(MediaType, Handler)]


        :attr accepted: list of content you accept in POST/PUT with
        associated deserializers::

            [(MediaType, Handler)]


        A serializer can be a simple callable taking a value or a class:

        .. code-block:: python

            class Myserializer(object):

                def unserialize(self, value):
                    # ... do something to value
                    return value

                def serialize(self, value):
                    # ... do something to value
                    return value


        :attr formats: return a list of format with their associated 
        contenttype::

            [(Suffix, MediaType)]

        :attr kwargs: any named parameter coresponding to a
        :ref:`resource method <resource>`. Each value is a callable
        taking a request and a response as arguments:

        .. code-block:: python

            def f(req, resp):
                pass

        """
        def _decorated(func):
            self.add_route(pattern, func, **kwargs)
            return func
        return _decorated

    def _wrap_urls(self, f, pattern):
        from django.conf.urls.defaults import patterns, url, include
        def _wrapped(*args):
            return patterns('', 
                    url(pattern, include(f(*args)))
            )
        return _wrapped

    def add_resource(self, klass, pattern=None):
        """add one :ref:`Resource class<resource>` to the routing.
        
        :attr klass: class inheriting from :class:webmachine.Resource
        :attr pattern: regexp.

        """
        res = klass()
        if not pattern:
            if hasattr(res._meta, "resource_path"):
                kname = res._meta.resource_path
            else:
                kname = klass.__name__.lower()

            pattern = r'^%s/' % res._meta.app_label
            if kname:
                pattern = r'%s/' % kname
        res.get_urls = self._wrap_urls(res.get_urls, pattern)
        self.resources[pattern] = res

    def add_resources(self, *klasses):
        """ allows you to add multiple Resource classes to the WM instance. You
        can also pass a pattern by using a tupple instead of simply
        provided the Resource class. Ex::

            (MyResource, r"^some/path$")
        """
        for klass in klasses:
            if isinstance(klass, tuple):
                klass, pattern = klass
            else:
                pattern = None
            self.add_resource(klass, pattern=pattern)

    def add_route(self, pattern, func, **kwargs):
        if pattern in self.resources:
            res = self.resources[pattern]
            res.update(func, **kwargs)
        else:
            res = RouteResource(pattern, func, **kwargs)
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
