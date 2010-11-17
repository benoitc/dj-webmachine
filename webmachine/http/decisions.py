# -*- coding: utf-8 -
#
# This file is part of dj-webmachine released under the MIT license. 
# See the NOTICE for more information.

import datetime

from webmachine.util.datetime_util import UTC
import webmachine.exc

def b03(res, req, resp):
    "Options?"
    if req.method == 'OPTIONS':
        for (header, value) in res.options(req, resp):
            resp[header] = value
        return True
    return False

def b04(res, req, resp):
    "Request entity too large?"
    return not res.valid_entity_length(req, resp)

def b05(res, req, resp):
    "Unknown Content-Type?"
    return not res.known_content_type(req, resp)

def b06(res, req, resp):
    "Unknown or unsupported Content-* header?"
    return not res.valid_content_headers(req, resp)

def b07(res, req, resp):
    "Forbidden?"
    return res.forbidden(req, resp)

def b08(res, req, resp):
    "Authorized?"
    auth = res.is_authorized(req, resp)
    if auth is True:
        return True
    elif isinstance(auth, basestring):
        resp["WWW-Authenticate"] = auth
    return False

def b09(res, req, resp):
    "Malformed?"
    return res.malformed_request(req, resp)

def b10(res, req, resp):
    "Is method allowed?"
    if req.method in res.allowed_methods(req, resp):
        return True
    return False 

def b11(res, req, resp):
    "URI too long?"
    return res.uri_too_long(req, resp)

def b12(res, req, resp):
    "Known method?"
    return req.method in res.known_methods(req, resp)

def b13(res, req, resp):
    "Service available?"
    return res.ping(req, resp) and res.service_available(req, resp)

def c03(res, req, resp):
    "Accept exists?"
    return "HTTP_ACCEPT" in req.META

def c04(res, req, resp):
    "Acceptable media type available?"
    ctypes = [ctype for (ctype, func) in res.content_types_provided(req, resp)]
    ctype = req.accept.best_match(ctypes)
    if ctype is None:
        return False
    resp.content_type = ctype
    return True

def d04(res, req, resp):
    "Accept-Language exists?"
    return "HTTP_ACCEPT_LANGUAGE" in req.META

def d05(res, req, resp):
    "Accept-Language available?"
    langs = res.languages_provided(req, resp)
    if langs is not None:
        lang = req.accept_language.best_match(langs)
        if lang is None:
            return False
        resp.content_language = lang
    return True
    
def e05(res, req, resp):
    "Accept-Charset exists?"
    return "HTTP_ACCEPT_CHARSET" in req.META

def e06(res, req, resp):
    "Acceptable charset available?"
    charsets = res.charsets_provided(req, resp)
    if charsets is not None:
        charset = req.accept_charset.best_match(charsets)
        if charset is None:
            return False
        resp._charset = charset
    return True

def f06(res, req, resp):
    "Accept-Encoding exists?"
    return "HTTP_ACCEPT_ENCODING" in req.META

def f07(res, req, resp):
    "Acceptable encoding available?"
    encodings = res.encodings_provided(req, resp)
    if encodings is not None:
        encodings = [enc for (enc, func) in encodings]
        enc = req.accept_encoding.best_match(encodings)
        if enc is None:
            return False
        resp.content_encoding = enc
    return True

def g07(res, req, resp):
    "Resource exists?"

    # Set variances now that conneg is done
    hdr = []
    if len(res.content_types_provided(req, resp) or []) > 1:
        hdr.append("Accept")
    if len(res.charsets_provided(req, resp) or []) > 1:
        hdr.append("Accept-Charset")
    if len(res.encodings_provided(req, resp) or []) > 1:
        hdr.append("Accept-Encoding")
    if len(res.languages_provided(req, resp) or []) > 1:
        hdr.append("Accept-Language")
    hdr.extend(res.variances(req, resp))
    resp.vary = hdr

    return res.resource_exists(req, resp)

def g08(res, req, resp):
    "If-Match exists?"
    return "HTTP_IF_MATCH" in req.META

def g09(res, req, resp):
    "If-Match: * exists?"
    return '*' in req.if_match

def g11(res, req, resp):
    "Etag in If-Match?"
    return res.generate_etag(req, resp) in req.if_match

def h07(res, req, resp):
    "If-Match: * exists?"
    # Need to recheck that if-match was an actual header
    # because WebOb is says that '*' will match no header.
    return 'HTTP_IF_MATCH' in req.META and '*' in req.if_match

def h10(res, req, resp):
    "If-Unmodified-Since exists?"
    return "HTTP_IF_MODIFIED_SINCE" in req.META

def h11(res, req, resp):
    "If-Unmodified-Since is a valid date?"
    return req.if_unmodified_since is not None

def h12(res, req, resp):
    "Last-Modified > If-Unmodified-Since?"
    resp.last_modified = res.last_modified(req, resp)
    return resp.last_modified > req.if_unmodified_since

def i04(res, req, resp):
    "Apply to a different URI?"
    uri = res.moved_permanently(req, resp)
    if not uri:
        return False
    resp.location = uri
    return True

def i07(res, req, resp):
    "PUT?"
    return req.method == "PUT"

def i12(res, req, resp):
    "If-None-Match exists?"
    return "HTTP_IF_NONE_MATCH" in req.META
    
def i13(res, req, resp):
    "If-None-Match: * exists?"
    return '*' in req.if_none_match
    
def j18(res, req, resp):
    "GET/HEAD?"
    return req.method in ["GET", "HEAD"]

def k05(res, req, resp):
    "Resource moved permanently?"
    uri = res.moved_permanently(req, resp)
    if not uri:
        return False
    resp.location = uri
    return True

def k07(res, req, resp):
    "Resource previously existed?"
    return res.previously_existed(req, resp)

def k13(res, req, resp):
    "Etag in If-None-Match?"
    resp.etag = res.generate_etag(req, resp)
    return resp.etag in req.if_none_match

def l05(res, req, resp):
    "Resource moved temporarily?"
    uri = res.moved_temporarily(req, resp)
    if not uri:
        return False
    resp.location = uri
    return True

def l07(res, req, resp):
    "POST?"
    return req.method == "POST"

def l13(res, req, resp):
    "If-Modified-Since exists?"
    return "HTTP_IF_MODIFIED_SINCE" in req.META

def l14(res, req, resp):
    "If-Modified-Since is a valid date?"
    return req.if_modified_since is not None

def l15(res, req, resp):
    "If-Modified-Since > Now?"
    return req.if_modified_since > datetime.datetime.now(UTC)

def l17(res, req, resp):
    "Last-Modified > If-Modified-Since?"
    resp.last_modified = res.last_modified(req, resp)
    return resp.last_modified > req.if_modified_since

def m05(res, req, resp):
    "POST?"
    return req.method == "POST"

def m07(res, req, resp):
    "Server permits POST to missing resource?"
    return res.allow_missing_post(req, resp)

def m16(res, req, resp):
    "DELETE?"
    return req.method == "DELETE"

def m20(res, req, resp):
    """Delete enacted immediayly?
    Also where DELETE is forced."""
    return res.delete_resource(req, resp)

def m20b(res, req, resp):
    """ Delete completed """
    return res.delete_completed(req, resp)

def n05(res, req, resp):
    "Server permits POST to missing resource?"
    return res.allow_missing_post(req, resp)

def n11(res, req, resp):
    "Redirect?"
    if res.post_is_create(req, resp):
        handle_request_body(res, req, resp)
    else:
        if not res.process_post(req, resp):
            raise webmachine.exc.HTTPInternalServerError("Failed to process POST.")
        return False
    resp.location = res.created_location(req, resp)
    if not resp.location:
        return False     
    return True


def n16(res, req, resp):
    "POST?"
    return req.method == "POST"

def o14(res, req, resp):
    "Is conflict?"
    if not res.is_conflict(req, resp):
        handle_response_body(res, req, resp)
        return False
    return True

def o16(res, req, resp):
    "PUT?"
    return req.method == "PUT"

def o18(res, req, resp):
    "Multiple representations? (Build GET/HEAD body)"
    if req.method not in ["GET", "HEAD"]:
        return res.multiple_choices(req, resp)

    handle_response_body(res, req, resp)
    return res.multiple_choices(req, resp)

def o20(res, req, resp):
    "Response includes entity?"
    return bool(resp._container)

def p03(res, req, resp):
    "Conflict?"
    if res.is_conflict(req, resp):
        return True

    handle_request_body(res, req, resp)
    return False

def p11(res, req, resp):
    "New resource?"
    if not resp.location:
        return False
    return True

def first_match(func, req, resp, expect):
    for (key, value) in func(req, resp):
        if key == expect:
            return value
    return None

def handle_request_body(res, req, resp):
    ctype = req.content_type or "application/octet-stream"
    mtype = ctype.split(";", 1)[0]

    func = first_match(res.content_types_accepted, req, resp, mtype)
    if func is None:
        raise webmachine.exc.HTTPUnsupportedMediaType()

    return func(req, resp)

def handle_response_body(res, req, resp):
    resp.etag = res.generate_etag(req, resp)
    resp.last_modified = res.last_modified(req, resp)
    resp.expires = res.expires(req, resp)
    
    # Generate the body
    func = first_match(res.content_types_provided, req, resp, resp.content_type)
    if func is None:
        raise webmachine.exc.HTTPInternalServerError()
   
    body = func(req, resp)

    # If we're using a charset, make sure to use unicode_body.    
    if resp.charset:
        resp.body = unicode(body)
    else:
        resp.body = body

    # Handle our content encoding.
    encoding = resp.content_encoding
    if encoding:
        func = first_match(res.encodings_provided, req, resp, encoding)
        if func is None:
            raise webmachine.exc.HTTPInternalServerError()
        resp.body = func(resp.body)
        resp['Content-Encoding'] = encoding

    if not isinstance(resp.body, basestring) and hasattr(resp.body, '__iter__'):
        resp._container = resp.body
        resp._is_string = False
    else:
        resp._container = [resp.body]
        
        resp._is_string = True


TRANSITIONS = {
    b03: (200, c03), # Options?
    b04: (413, b03), # Request entity too large?
    b05: (415, b04), # Unknown Content-Type?
    b06: (501, b05), # Unknown or unsupported Content-* header?
    b07: (403, b06), # Forbidden?
    b08: (b07, 401), # Authorized?
    b09: (400, b08), # Malformed?
    b10: (b09, 405), # Is method allowed?
    b11: (414, b10), # URI too long?
    b12: (b11, 501), # Known method?
    b13: (b12, 503), # Service available?
    c03: (c04, d04), # Accept exists?
    c04: (d04, 406), # Acceptable media type available?
    d04: (d05, e05), # Accept-Language exists?
    d05: (e05, 406), # Accept-Language available?
    e05: (e06, f06), # Accept-Charset exists?
    e06: (f06, 406), # Acceptable charset available?
    f06: (f07, g07), # Accept-Encoding exists?
    f07: (g07, 406), # Acceptable encoding available?
    g07: (g08, h07), # Resource exists?
    g08: (g09, h10), # If-Match exists?
    g09: (h10, g11), # If-Match: * exists?
    g11: (h10, 412), # Etag in If-Match?
    h07: (412, i07), # If-Match: * exists?
    h10: (h11, i12), # If-Unmodified-Since exists?
    h11: (h12, i12), # If-Unmodified-Since is valid date?
    h12: (412, i12), # Last-Modified > If-Unmodified-Since?
    i04: (301, p03), # Apply to a different URI?
    i07: (i04, k07), # PUT?
    i12: (i13, l13), # If-None-Match exists?
    i13: (j18, k13), # If-None-Match: * exists?
    j18: (304, 412), # GET/HEAD?
    k05: (301, l05), # Resource moved permanently?
    k07: (k05, l07), # Resource previously existed?
    k13: (j18, l13), # Etag in If-None-Match?
    l05: (307, m05), # Resource moved temporarily?
    l07: (m07, 404), # POST?
    l13: (l14, m16), # If-Modified-Since exists?
    l14: (l15, m16), # If-Modified-Since is valid date?
    l15: (m16, l17), # If-Modified-Since > Now?
    l17: (m16, 304), # Last-Modified > If-Modified-Since?
    m05: (n05, 410), # POST?
    m07: (n11, 404), # Server permits POST to missing resource?
    m16: (m20, n16), # DELETE?
    m20: (m20b, 500), # DELETE enacted immediately?
    m20b: (o20, 202), # Delete completeed?
    m20: (o20, 202), # Delete enacted?
    n05: (n11, 410), # Server permits POST to missing resource?
    n11: (303, p11), # Redirect?
    n16: (n11, o16), # POST?
    o14: (409, p11), # Conflict?
    o16: (o14, o18), # PUT?
    o18: (300, 200), # Multiple representations?
    o20: (o18, 204), # Response includes entity?
    p03: (409, p11), # Conflict?
    p11: (201, o20)  # New resource?
}
