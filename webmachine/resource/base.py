# -*- coding: utf-8 -
#
# This file is part of dj-webmachine released under the MIT license. 
# See the NOTICE for more information.

import re
import sys
import types

from django.db.models.options import get_verbose_name
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
from webmachine.resource.decisions import b13, TRANSITIONS



CHARSET_RE = re.compile(r';\s*charset=([^;]*)', re.I)


DEFAULT_NAMES = ('verbose_name', 'app_label')

class Options(object):
    """ class based on django.db.models.options. We only keep
    useful bits."""
    
    def __init__(self, meta, app_label=None):
        self.module_name, self.verbose_name = None, None
        self.verbose_name_plural = None
        self.object_name, self.app_label = None, app_label
        self.meta = meta
    
    def contribute_to_class(self, cls, name):
        cls._meta = self

        # First, construct the default values for these options.
        self.object_name = cls.__name__
        self.module_name = self.object_name.lower()
        self.verbose_name = get_verbose_name(self.object_name)

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
        setattr(new_class, '_meta',  Options(meta, app_label=app_label))

        return new_class
    

# FIXME: we should propbably wrap full HttpRequest object instead of
# adding properties to it in __call__ . Also datetime_utils has surely
# equivalent in Django. 
class Resource(object):
    __metaclass__ = ResourceMeta

    base_url = None
    csrf_exempt = True

    def allowed_methods(self, req, resp):
        return ["GET", "HEAD"]

    def allow_missing_post(self, req, resp):
        return False

    def auth_required(self, req, resp):
        return True
    
    def charsets_provided(self, req, resp):
        """\
        return [("iso-8859-1", lambda x: x)]
        
        Returning None prevents the character set negotiation
        logic.
        """
        return None

    def content_types_accepted(self, req, resp):
        return None

    def content_types_provided(self, req, resp):
        return [
            ("text/html", self.to_html)
        ]

    def created_location(self, req, resp):
        return None

    def delete_completed(self, req, resp):
        return True
    
    def delete_resource(self, req, resp):
        return False

    def encodings_provided(self, req, resp):
        """\
        return [("identity", lambda x: x)]

        Returning None prevents the encoding negotiation logic.
        """
        return None

    def expires(self, req, resp):
        return None
    
    def finish_request(self, req, resp):
        return True

    def forbidden(self, req, resp):
        return False
    
    def generate_etag(self, req, resp):
        return None

    def is_authorized(self, req, resp):
        return True
    
    def is_conflict(self, req, resp):
        return False

    def known_content_type(self, req, resp):
        return True

    def known_methods(self, req, resp):
        return set([
            "GET", "HEAD", "POST", "PUT", "DELETE",
            "TRACE", "CONNECT", "OPTIONS"
        ])

    def languages_provided(self, req, resp):
        """\
        return ["en", "es", "en-gb"]
        
        returning None short circuits the language negotiation
        """
        return None

    def last_modified(self, req, resp):
        return None

    def malformed_request(self, req, resp):
        return False

    def moved_permanently(self, req, resp):
        return False
    
    def moved_temporarily(self, req, resp):
        return False
    
    def multiple_choices(self, req, resp):
        return False

    def options(self, req, resp):
        return []

    def ping(self, req, resp):
        return True
    
    def post_is_create(self, req, resp):
        return False
    
    def previously_existed(self, req, resp):
        return False

    def process_post(self, req, resp):
        return False

    def resource_exists(self, req, resp):
        return True
    
    def service_available(self, req, resp):
        return True

    def uri_too_long(self, req, resp):
        return False
    
    def valid_content_headers(self, req, resp):
        return True
    
    def valid_entity_length(self, req, resp):
        return True

    def variances(self, req, resp):
        return []

    ###################
    # PRIVATE METHODS #
    ###################

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url
        urlpatterns = patterns('', 
            url(r'^$', self, name="%s_index" % self.__class__.__name__),
        )
        return urlpatterns

    def __call__(self, req, *args, **kwargs):
        """ Process request and return the response """

        # add path args to the request
        setattr(req, "url_args", args or [])
        setattr(req, "url_kwargs", kwargs or [])


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

        # start to build response
        resp = HttpResponse()
        
        # add missing features we need in response
        resp.content_encoding = None
        resp.content_type = None 
        resp.vary = []
        resp.charset = None
        resp.etag = None
        resp.last_modified = None
        resp.expires = None

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

        return resp

