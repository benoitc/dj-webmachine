# -*- coding: utf-8 -
#
# This file is part of dj-webmachine released under the MIT license. 
# See the NOTICE for more information.


"""
all dj-webmachine resources should inherit from the Resource object:

.. code-block:: python

    from webmachine import Resource

    class MyResource(Resource):
        pass 


All Resource methods are of the signature:

.. code-block:: python

    def f(self, req, resp):
        return result

``req`` is a :class:`django.http.HttpRequest` instance, and ``resp`` a
:class:`django.http.HttpResource` instance. This instances have been
:ref:`improved to support more HTTP semantics <http>`. At any time you
can manipulate this object to return the response you want or pass
values to other methods.

There are over 30 Resource methods you can define, but any of them can 
be omitted as they have reasonable defaults.
"""

import re
import sys
import types

from django.http import HttpResponse
from django.utils.translation import activate, deactivate_all, get_language, \
string_concat
from django.utils.encoding import smart_str, force_unicode


from webmachine.acceptparse import get_accept_hdr, MIMEAccept, \
        MIMENilAccept, NoAccept
from webmachine.etag import get_etag, AnyETag, NoETag
from webmachine.exc import HTTPException, HTTPInternalServerError
from webmachine.util import coerce_put_post, serialize_list
from webmachine.util.datetime_util import parse_date
from webmachine.decisions import b13, TRANSITIONS, first_match


CHARSET_RE = re.compile(r';\s*charset=([^;]*)', re.I)
get_verbose_name = lambda class_name: re.sub('(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))', ' \\1', class_name).lower().strip()

DEFAULT_NAMES = ('verbose_name', 'app_label', 'resource_prefix')

class Options(object):
    """ class based on django.db.models.options. We only keep
    useful bits."""
    
    def __init__(self, meta, app_label=None):
        self.module_name, self.verbose_name = None, None
        self.verbose_name_plural = None
        self.resource_prefix = None
        self.object_name, self.app_label = None, app_label
        self.meta = meta
    
    def contribute_to_class(self, cls, name):
        cls._meta = self

        # First, construct the default values for these options.
        self.object_name = cls.__name__
        self.module_name = self.object_name.lower()
        self.verbose_name = get_verbose_name(self.object_name)
        self.resource_prefix = self.module_name
        # Next, apply any overridden values from 'class Meta'.
        if self.meta:
            meta_attrs = self.meta.__dict__.copy()
            for name in self.meta.__dict__:
                # Ignore any private attributes that Django doesn't care about.
                # NOTE: We can't modify a dictionary's contents while looping
                # over it, so we loop over the *original* dictionary instead.
                if name.startswith('_'):
                    del meta_attrs[name]
            for attr_name in DEFAULT_NAMES:
                if attr_name in meta_attrs:
                    setattr(self, attr_name, meta_attrs.pop(attr_name))
                elif hasattr(self.meta, attr_name):
                    setattr(self, attr_name, getattr(self.meta, attr_name))

            # verbose_name_plural is a special case because it uses a 's'
            # by default.
            setattr(self, 'verbose_name_plural', meta_attrs.pop('verbose_name_plural', 
                string_concat(self.verbose_name, 's')))

            # Any leftover attributes must be invalid.
            if meta_attrs != {}:
                raise TypeError("'class Meta' got invalid attribute(s): %s" % ','.join(meta_attrs.keys()))
        else:
            self.verbose_name_plural = string_concat(self.verbose_name, 's')
        del self.meta
        
    def __str__(self):
        return "%s.%s" % (smart_str(self.app_label), smart_str(self.module_name))

    def verbose_name_raw(self):
        """
        There are a few places where the untranslated verbose name is needed
        (so that we get the same value regardless of currently active
        locale).
        """
        lang = get_language()
        deactivate_all()
        raw = force_unicode(self.verbose_name)
        activate(lang)
        return raw
    verbose_name_raw = property(verbose_name_raw)


class ResourceMeta(type):
    def __new__(cls, name, bases, attrs):
        super_new = super(ResourceMeta, cls).__new__
        parents = [b for b in bases if isinstance(b, ResourceMeta)]
        if not parents:
            return super_new(cls, name, bases, attrs)
            
        new_class = super_new(cls, name, bases, attrs)

        attr_meta = attrs.pop('Meta', None)
        if not attr_meta:
            meta = getattr(new_class, 'Meta', None)
        else:
            meta = attr_meta
        
        if getattr(meta, 'app_label', None) is None:
            document_module = sys.modules[new_class.__module__]
            app_label = document_module.__name__.split('.')[-2]
        else:
            app_label = getattr(meta, 'app_label')

        
        new_class.add_to_class('_meta',  Options(meta, app_label=app_label))
        return new_class
    
    def add_to_class(cls, name, value):
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


RESOURCE_METHODS = ["allowed_methods", "allow_missing_post",
"auth_required", "charsets_provided", "content_types_accepted",
"content_types_provided", "created_location", "delete_completed",
"delete_resource", "encodings_provided", "expires", "finish_request",
"forbidden", "format_suffix_accepted", "generate_etag", "is_authorized",
"is_conflict", "known_content_type", "known_methods",
"languages_provided", "last_modified", "malformed_request",
"moved_permanently", "moved_temporarily", "multiple_choices", "options",
"ping", "post_is_create", "previously_existed", "process_post",
"resource_exists", "service_available", "uri_too_long",
"valid_content_headers", "valid_entity_length", "variances"]


# FIXME: we should propbably wrap full HttpRequest object instead of
# adding properties to it in __call__ . Also datetime_utils has surely
# equivalent in Django. 
class Resource(object):
    __metaclass__ = ResourceMeta

    base_url = None
    csrf_exempt = True
    format_sufx_param = "FORMAT_SUFX"


    def allowed_methods(self, req, resp):
        """
        If a Method not in this list is requested, then a 
        405 Method Not Allowed will be sent. Note that 
        these are all-caps and are string. 

        :return: [Method] 
        """
        return ["GET", "HEAD"]

    def allow_missing_post(self, req, resp):
        """
        If the resource accepts POST requests to nonexistent resources, 
        then this should return True.

        :return: True or False
        """
        return False

    def auth_required(self, req, resp):
        """
        :return: True or False
        """
        return True
    
    def charsets_provided(self, req, resp):
        """
        If this is anything other than None, it must be a list of pairs 
        where each pair is of the form Charset, Converter where Charset
        is a string naming a charset and Converter is a callable function 
        in the resource which will be called on the produced body in a GET
        and ensure that it is in Charset.

        Ex:
            return [("iso-8859-1", lambda x: x)]
        
        Returning None prevents the character set negotiation
        logic.

        :return: [(Charset, Handler)]
        """
        return None

    def content_types_accepted(self, req, resp):
        """
        This is used similarly to content_types_provided, 
        except that it is for incoming resource representations
        -- for example, PUT requests.

        :return: [(MediaType, Handler)] or None
        """
        return None

    def content_types_provided(self, req, resp):
        """
        This should return a list of pairs where each pair is of the form 
        (Mediatype, Handler) where Mediatype is a string of content-type 
        format and the Handler is an callable function which can provide
        a resource representation in that media type. Content negotiation 
        is driven by this return value. For example, if a client request
        includes an Accept header with a value that does not appear as a 
        first element in any of the return tuples, then a 406 Not Acceptable 
        will be sent.

        :return: [(MediaType, Handler)] or None
        """
        return [
            ("text/html", self.to_html)
        ]

    def created_location(self, req, resp):
        """
        :return: Path or None
        """
        return None

    def delete_completed(self, req, resp):
        """
        This is only called after a successful delete_resource 
        call, and should return false if the deletion was accepted
        but cannot yet be guaranteed to have finished.

        :return: True or False
        """
        return True
    
    def delete_resource(self, req, resp):
        """
        This is called when a DELETE request should be enacted, 
        and should return true if the deletion succeeded.

        :return: True or False
        """
        return False

    def encodings_provided(self, req, resp):
        """\
        This must be a list of pairs where in each pair Encoding 
        is a string naming a valid content encoding and Encoder
        is a callable function in the resource which will be 
        called on the produced body in a GET and ensure that it
        is so encoded. One useful setting is to have the function
        check on method, and on GET requests return [("identity", lambda x: x)] 
        as this is all that is needed to support identity encoding.

            return [("identity", lambda x: x)]

        Returning None prevents the encoding negotiation logic.

        :return: [(Encoding, Encoder)]
        """
        return None

    def expires(self, req, resp):
        """
        :return: Nonr or Date string
        """
        return None
    
    def finish_request(self, req, resp):
        """
        This function, if exported, is called just before the final 
        response is constructed and sent. The Result is ignored, so
        any effect of this function must be by returning a modified 
        request.

        :return: True or False
        """
        return True

    def forbidden(self, req, resp):
        """
        :return: True or False
        """
        return False

    def format_suffix_accepted(self, req, resp):
        """
        Allows you to force the accepted format depending on path
        suffix.

        Ex:  return [("json", "application/json")]
        will allows to force `Accept` header to `application/json` on
        url `/some/url.json` 

        :return: [(Suffix, MediaType)] or None
        """
        return []
    
    def generate_etag(self, req, resp):
        """
        If this returns a value, it will be used as the value of the ETag 
        header and for comparison in conditional requests.

        :return: Str or None
        """
        return None

    def is_authorized(self, req, resp):
        """
        If this returns anything other than true, the response will 
        be 401 Unauthorized. The AuthHead return value will be used 
        as the value in the WWW-Authenticate header.

        :return: True or False
        """
        return True
    
    def is_conflict(self, req, resp):
        """
        If this returns true, the client will receive a 409 Conflict.

        :return: True or False
        """
        return False

    def known_content_type(self, req, resp):
        """
        :return: True or False
        """
        return True

    def known_methods(self, req, resp):
        """
        :return: set([Method])
        """
        return set([
            "GET", "HEAD", "POST", "PUT", "DELETE",
            "TRACE", "CONNECT", "OPTIONS"
        ])

    def languages_provided(self, req, resp):
        """\
        return ["en", "es", "en-gb"]
        
        returning None short circuits the language negotiation

        :return: [Language]
        """
        return None

    def last_modified(self, req, resp):
        """
        :return: DateString or None
        """
        return None

    def malformed_request(self, req, resp):
        """
        :return: True or False
        """
        return False

    def moved_permanently(self, req, resp):
        """
        :return: True Or False
        """
        return False
    
    def moved_temporarily(self, req, resp):
        """
        :return: True or False
        """
        return False
    
    def multiple_choices(self, req, resp):
        """
        If this returns true, then it is assumed that multiple 
        representations of the response are possible and a single
        one cannot be automatically chosen, so a 300 Multiple Choices
        will be sent instead of a 200.

        :return: True or False
        """
        return False

    def options(self, req, resp):
        """
        If the OPTIONS method is supported and is used, the return 
        value of this function is expected to be a list of pairs 
        representing header names and values that should appear 
        in the response.

        :return: [(HeaderName, Value)]
        """
        return []

    def ping(self, req, resp):
        """
        :return: True or False
        """
        return True
    
    def post_is_create(self, req, resp):
        """
        If POST requests should be treated as a request to put content
        into a (potentially new) resource as opposed to being a generic 
        submission for processing, then this function should return true. 
        If it does return true, then create_path will be called and the 
        rest of the request will be treated much like a PUT to the Path 
        entry returned by that call.

        :return: True or False
        """
        return False
    
    def previously_existed(self, req, resp):
        """
        :return: True or False
        """
        return False

    def process_post(self, req, resp):
        """
        If post_is_create returns false, then this will be called to process
        any POST requests. If it succeeds, it should return True.

        :return: True or False
        """
        return False

    def resource_exists(self, req, resp):
        """
        Returning non-true values will result in 404 Not Found.

        :return: True or False
        """
        return True
    
    def service_available(self, req, resp):
        """
        :return: True or False
        """
        return True

    def uri_too_long(self, req, resp):
        """
        :return: True or False
        """
        return False
    
    def valid_content_headers(self, req, resp):
        """
        :return: True or False
        """
        return True
    
    def valid_entity_length(self, req, resp):
        """
        :return: True or False
        """
        return True

    def variances(self, req, resp):
        """
        If this function is implemented, it should return a list 
        of strings with header names that should be included in 
        a given response's Vary header. The standard conneg headers
        (Accept, Accept-Encoding, Accept-Charset, Accept-Language)
        do not need to be specified here as Webmachine will add the
        correct elements of those automatically depending on resource
        behavior.

        :return: True or False
        """
        return []


    def get_urls(self):
        """
        method used to register utls in django urls routing.

        :return: urlpattern
        """
        from django.conf.urls.defaults import patterns, url
        urlpatterns = patterns('',
            url(r'^\.(?P<%s>\w*)$' % self.format_sufx_param, self, 
                name="%s_index_fmt" % self.__class__.__name__), 
            url(r'^$', self, name="%s_index" % self.__class__.__name__),
            
            
        )
        return urlpatterns


    ###################
    # PRIVATE METHODS #
    ###################

    def _process(self, req, *args, **kwargs):
        """ Process request and return the response """

        # initialize response object
        resp = HttpResponse()

        # add path args args to the request
        setattr(req, "url_args", args or [])
        setattr(req, "url_kwargs", kwargs or {})

        # force format depending on suffix ?
        if self.format_sufx_param in kwargs:
            fmt =kwargs.get(self.format_sufx_param)
            fmt_sufx = first_match(self.format_suffix_accepted, req,
                    resp, fmt)
            if fmt_sufx is not None:
                req.META['HTTP_ACCEPT'] = fmt_sufx
            else:
                resp.status_code = 406 
                resp._container = ["format %s not accepted" % fmt] 
                return resp

        # django isn't restful
        req.method = req.method.upper()
        if req.method == "PUT":
            coerce_put_post(req)

        # add content_type to the request
        req_ctype = req.META.get('CONTENT_TYPE', '').split(';', 1)[0]
        setattr(req, "content_type", req_ctype)

        # accept properties
        req.accept = get_accept_hdr(req, 'HTTP_ACCEPT', MIMEAccept, MIMENilAccept, 
                'MIME Accept')
        req.accept_charset = get_accept_hdr(req, 'HTTP_ACCEPT_CHARSET')
        req.accept_encoding = get_accept_hdr(req, 'HTTP_ACCEPT_ENCODING', 
                NilClass=NoAccept)
        req.accept_language = get_accept_hdr(req, 'HTTP_ACCEPT_LANGUAGE')

        # cache properties
        req.if_match = get_etag(req, 'HTTP_IF_MATCH', AnyETag)
        req.if_none_match = get_etag(req, 'HTTP_IF_NONE_MATCH', NoETag)
        req.date = parse_date(req.META.get('HTTP_DATE'))
        req.if_modified_since = parse_date(req.META.get('HTTP_IF_MODIFIED_SINCE'))
        req.if_unmodified_since = parse_date(req.META.get('HTTP_IF_UNMODIFIED_SINCE'))
        req.pragma = req.META.get('pragma')

                
        # add missing features we need in response
        resp.content_encoding = None
        resp.content_type = None 
        resp.vary = []
        resp.charset = None
        resp.etag = None
        resp.last_modified = None
        resp.expires = None
        resp.location = None

        ctypes = [ct for (ct, func) in (self.content_types_provided(req, resp) or [])]
        if len(ctypes):
            resp.content_type = ctypes[0]

        try:
            state = b13
            while not isinstance(state, int):
                if state(self, req, resp):
                    state = TRANSITIONS[state][0]
                else:
                    state = TRANSITIONS[state][1]
                if not isinstance(state, (int, types.FunctionType)):
                    raise HTTPInternalServerError("Invalid state: %r" % state)

            resp.status_code = state
        except HTTPException, e:
            # Error while processing request
            # Return HTTP response
            return e

        # set other headers 
        for attr_name in ('vary', 'etag', 'content_type', \
                'content_encoding', 'last_modified', 'expires'):
           
            val = serialize_list(getattr(resp, attr_name))
            if val and val is not None:
                header_name = attr_name.replace('_', '-').title()
                resp[header_name] = val 

        if resp.charset is not None:
            header = resp.get('Content-Type')
            if header is not None:
                match = CHARSET_RE.search(header)
                if match:
                    header = header[:match.start()] + header[match.end():]
                header += '; charset=%s' % resp.charset
                resp['Content-Type'] = header

        if resp.location is not None:
            resp['Location'] = resp.location

        return resp

    def __call__(self, request, *args, **kwargs):
        return self._process(request, *args, **kwargs)
