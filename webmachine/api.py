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

from webmachine.resource import Resource

class QA(object):
    """ object used to document query args and validate them """

    def __init__(self, name, default=None, validator=None, 
            required=False, null=True, doc=""):
        self.name = name
        self.default = default
        self.validator = validator
        self.required = required
        self.null = null
        self.doc = ""

    def validate(self, req, resp, value):
        if not self.validator:
            return True
        return self.validator(req, resp, value)

    def is_required(self, req, resp):
        return self.required

    def get_default(self, req, resp):
        return self.default

def qa(name, default=None, validator=None, required=False, null=True,
        doc=""):
    """ shortcut to create a QA instance """
    return QA(name, default=default, validator=validatir
            required=required, null=null, doc=doc)


class WMUrl(object):
    """ object used to document url used """

    def __init__(self, regexp, doc=""):
        self.regexp = regexp
        doc = doc

def wmurl(regexp, doc=""):
    """ shortcut to create an Url instance """
    return WUrl(regexp, doc=doc)


class ApiDescriptor(object):

    allowed_method = ["GET", "HEAD"]
    urls = None
    query_args = None
    throttle = None
    serializers = []

    def unserialize(self, req, resp):
        if req.method != "DELETE":
            funname = "handle_%s" % req.method.lower()
            if hasattr(self, funname):
                body = getattr(self, funname)(req, resp)
            else:
                return False
        else:
            body = resp._container
        
        serializer = get_serializer(resp.content_type)
        return serializer.serialize(body, req, resp)
    
    def serialize(self, req, resp):
        ctype = req.content_type or "application/octet-stream"
        mtype = ctype.split(";", 1)[0]

        serializer = get_serializer(mtype)
        req.decoded_data = serializer.unserialize(req, resp)
        


class ApiResource(Resource):

    def __init__(self, descriptor):
        self.descriptor = descriptor

    def allowed_methods(self, req, resp):
        if hasattr(self.descriptor, "filter_methods"):
            fun = getattr(self.descriptor, "filter_methods")
            return fun(req.method, req, resp)

        return self.descriptor.allowed_methods

    def malformed_request(self, req, resp):
        query_args = self.descriptor.query_args
        if not query_args:
            return False
        args_to_validate = []
        if "default" in query_args:
            args_to_validate.extend(query_args["defaul"])
        if req.method in query_args:
            args_to_validate.extend(query_args[req.method])

        final_query_args = {}
        for arg in args_to_validate:
            if arg.name in req.REQUEST:
                value = req.REQUEST[arg.name]
                if not arg.validate(value, req, resp):
                    return True
                final_query_args[arg.name] = value
            elif arg.is_required(req, resp):
                return True
            else:
                default = arg.get_default(req, resp)
                if default is not None:
                    final_query_args[arg.name] = default
        req.query_args = final_query_args
        return False

    def content_types_accepted(self, req, resp):
        ctypes = self.descriptor.content_types_accepted
        if not ctypes:
            return []
        
        fun = getattr(self.descriptor, "unserialize")
        return [(ctype, fun) for ctype in ctypes]


    def content_types_provided(self, req, resp):
        ctypes = self.descriptor.content_types_provided
        if not ctypes:
            return []

        fun = getattr(self.descriptor, "serialize")
        return [(ctype, fun) for ctype in ctypes]
    

    def delete_resource(self, req, resp):
        result = self.descriptor.delete(req, resp)
        if result == False or result == None:
            return False
        resp._container = result
        return True

    def resource_exists(self, req, resp):
        if hasattr(self.descriptor, "resource_exists"):
            fun = getattr(self.descriptor, "resource_exists")
            return fun(req, resp)
        return True

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url, include
        urls = []
        for url in self.descriptor.urls:
            urls.append(url(url.pattern, self))
        return patterns('', *urls)

def register_api(*api_desccriptors, site=None, version='1.0'):
    api_descriptors = api_descriptors or []
    resources = [ApiResource(api_descriptor) for api_descriptor in \
            api_descriptors]
    if site = None:
        from webmachine.sites import site

    site.register(resources)
