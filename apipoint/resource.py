# -*- coding: utf-8 -
#
# This file is part of dj-apipoint released under the Apache 2 license. 
# See the NOTICE for more information.

import re
import types

from django.http import HttpResponse

from apipoint.acceptparse import get_accept_hdr, MIMEAccept, \
        MIMENilAccept, NoAccept
from apipoint.datetime_util import parse_date
from apipoint.decisions import b13, TRANSITIONS
from apipoint.etag import get_etag, AnyETag, NoETag
from apipoint.exc import HTTPException, HTTPInternalServerError
from apipoint.util import coerce_put_post, serialize_list

CHARSET_RE = re.compile(r';\s*charset=([^;]*)', re.I)


# FIXME: we should propbably wrap full HttpRequest object instead of
# adding properties to it in __call__ . Also datetime_utils has surely
# equivalent in Django. 
class Resource(object):
    base_url = None

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
        pass


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
            resp.status = state
        except HTTPException, e:
            # Error while processing request
            # Return HTTP response
            return e

        # set other headers 
        for attr_name in ('vary', 'etag', 'content_type', \
                'content_encoding', 'last_modified', 'expires'):
            
            if hasattr(resp, attr_name):
                header_name = attr_name.replace('_', '-').title()
                resp[header_name] = getattr(resp, attr_name)

        if resp.charset is not None:
            header = resp.get('Content-Type')
            if header is not None:
                match = CHARSET_RE.search(header)
                if match:
                    header = header[:match.start()] + header[match.end():]
                header += '; charset=%s' % charset
                resp['Content-Type'] = header

        return resp
