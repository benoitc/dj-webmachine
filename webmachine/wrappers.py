# -*- coding: utf-8 -
#
# This file is part of dj-webmachine released under the MIT license. 
# See the NOTICE for more information.
import re

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from webob import Request
from webob.descriptors import *
from webob.datetime_utils import *
from webob.headers import ResponseHeaders


_PARAM_RE = re.compile(r'([a-z0-9]+)=(?:"([^"]*)"|([a-z0-9_.-]*))', re.I)
_OK_PARAM_RE = re.compile(r'^[a-z0-9_.-]+$', re.I)

class WMRequest(WSGIRequest, Request):

    environ = None
    path = None
    method = None
    META = None

    def __init__(self, environ, *args, **kwargs):
        Request.__init__(self, environ)
        WSGIRequest.__init__(self, environ)

        # add path args args to the request
        self.url_args = args or []
        self.url_kwargs = kwargs or {}

    webob_POST = Request.POST
    webob_WGET = Request.GET

    @property
    def str_POST(self):

        clength = self.environ.get('CONTENT_LENGTH')
        try:
            return super(WMRequest, self).str_POST
        finally:
            self.environ['CONTENT_LENGTH'] = clength
            self._seek_input()

    def _load_post_and_files(self):
        try:
            return WSGIRequest._load_post_and_files(self)
        finally:
            # "Resetting" the input so WebOb will read it:
            self._seek_input()
    
    def _seek_input(self):
        if "wsgi.input" in self.environ:
            try:
                self.environ['wsgi.input'].seek(0)
            except AttributeError:
                pass

class WMResponse(HttpResponse):
    """ Add some properties to HttpResponse """

    status_code = 200

    default_content_type = 'text/html'
    default_charset = 'UTF-8'
    unicode_errors = 'strict'
    default_conditional_response = False

    def __init__(self, content='', mimetype=None, status=None,
            content_type=None, request=None):
        if isinstance(status, basestring):
            (status_code, status_reason) = status.split(" ", 1)
            status_code = int(status_code)
            self.status_reason = status_reason or None
        else:
            status_code = status
            self.status_reason = None

        self.request = request
        self._headerlist = []

        HttpResponse.__init__(self, content=content,
                status=status_code, content_type=content_type)

        

    def _headerlist__get(self):
        """
        The list of response headers
        """
        return self._headers.values()

    def _headerlist__set(self, value):
        self._headers = {}
        if not isinstance(value, list):
            if hasattr(value, 'items'):
                value = value.items()
            value = list(value)
        
        headers = ResponseHeaders.view_list(self.headerlist)
        for hname in headers.keys():
            self._headers[hname.lower()] = (hname, headers[hname])
        self._headerlist = value


    def _headerlist__del(self):
        self.headerlist = []
        self._headers = {}

    headerlist = property(_headerlist__get, _headerlist__set, _headerlist__del, doc=_headerlist__get.__doc__)

    def __setitem__(self, header, value):
        header, value = self._convert_to_ascii(header, value)
        self._headers[header.lower()] = (header, value)

    def __delitem__(self, header):
        try:
            del self._headers[header.lower()]
        except KeyError:
            return

    def __getitem__(self, header):
        return self._headers[header.lower()][1]

    allow = list_header('Allow', '14.7')
    ## FIXME: I realize response.vary += 'something' won't work.  It should.
    ## Maybe for all listy headers.
    vary = list_header('Vary', '14.44')

    content_length = converter(
        header_getter('Content-Length', '14.17'),
        parse_int, serialize_int, 'int')

    content_encoding = header_getter('Content-Encoding', '14.11')
    content_language = list_header('Content-Language', '14.12')
    content_location = header_getter('Content-Location', '14.14')
    content_md5 = header_getter('Content-MD5', '14.14')
    # FIXME: a special ContentDisposition type would be nice
    content_disposition = header_getter('Content-Disposition', '19.5.1')

    accept_ranges = header_getter('Accept-Ranges', '14.5')
    content_range = converter(
        header_getter('Content-Range', '14.16'),
        parse_content_range, serialize_content_range, 'ContentRange object')

    date = date_header('Date', '14.18')
    expires = date_header('Expires', '14.21')
    last_modified = date_header('Last-Modified', '14.29')

    etag = converter(
        header_getter('ETag', '14.19'),
        parse_etag_response, serialize_etag_response, 'Entity tag')

    location = header_getter('Location', '14.30')
    pragma = header_getter('Pragma', '14.32')
    age = converter(
        header_getter('Age', '14.6'),
        parse_int_safe, serialize_int, 'int')

    retry_after = converter(
        header_getter('Retry-After', '14.37'),
        parse_date_delta, serialize_date_delta, 'HTTP date or delta seconds')

    server = header_getter('Server', '14.38')

    def _convert_to_ascii(self, header, value):
        def convert(s):
            try:
                return s.decode('ascii')
            except AttributeError:
                return s
        return convert(header), convert(value)

    #
    # charset
    #

    def _charset__get(self):
        """
        Get/set the charset (in the Content-Type)
        """
        header = self._headers.get('content-type')
        if not header:
            return None
        match = CHARSET_RE.search(header[1])
        if match:
            return match.group(1)
        return None

    def _charset__set(self, charset):
        if charset is None:
            del self.charset
            return
        try:
            hname, header = self._headers.pop('content-type')
        except KeyError:
            raise AttributeError(
                    "You cannot set the charset when no content-type is defined")
            match = CHARSET_RE.search(header)
        if match:
            header = header[:match.start()] + header[match.end():]
        header += '; charset=%s' % charset
        self._headers['content-type'] = hname, header

    def _charset__del(self):
        try:
            hname, header = self._headers.pop('content-type')
        except KeyError:
            # Don't need to remove anything
            return
        match = CHARSET_RE.search(header)
        if match:
            header = header[:match.start()] + header[match.end():]
        self[hname] = header

    charset = property(_charset__get, _charset__set, _charset__del, doc=_charset__get.__doc__)


    #
    # content_type
    #

    def _content_type__get(self):
        """
        Get/set the Content-Type header (or None), *without* the
        charset or any parameters.

        If you include parameters (or ``;`` at all) when setting the
        content_type, any existing parameters will be deleted;
        otherwise they will be preserved.
        """
        header = self._headers.get('content-type')

        if not header:
            return None
        return header[1].split(';', 1)[0]

    def _content_type__set(self, value):
        if ';' not in value:
            if 'content-type' in self._headers:
                header = self._headers.get('content-type')
                if ';' in header[1]:
                    params = header[1].split(';', 1)[1]
                    value += ';' + params
        self['Content-Type'] = value

    def _content_type__del(self):
        try:
            del self._headers['content-type']
        except KeyError:
            pass

    content_type = property(_content_type__get, _content_type__set,
            _content_type__del, doc=_content_type__get.__doc__)


    #
    # content_type_params
    #

    def _content_type_params__get(self):
        """
        A dictionary of all the parameters in the content type.

        (This is not a view, set to change, modifications of the dict would not be
        applied otherwise)
        """
        if not 'content-type' in self._headers:
            return {}

        params = self._headers.get('content-type')
        if ';' not in params[1]:
            return {}
        params = params[1].split(';', 1)[1]
        result = {}
        for match in _PARAM_RE.finditer(params):
            result[match.group(1)] = match.group(2) or match.group(3) or ''
        return result

    def _content_type_params__set(self, value_dict):
        if not value_dict:
            del self.content_type_params
            return
        params = []
        for k, v in sorted(value_dict.items()):
            if not _OK_PARAM_RE.search(v):
                ## FIXME: I'm not sure what to do with "'s in the parameter value
                ## I think it might be simply illegal
                v = '"%s"' % v.replace('"', '\\"')
            params.append('; %s=%s' % (k, v))
        ct = self._headers.pop('content-type')
        if not ct:
            ct = ''
        else:
            ct = ct[1].split(';', 1)[0]
        ct += ''.join(params)
        self._headers['content-type'] = 'Content-Type', ct

    def _content_type_params__del(self, value):
        try:
            header = self._headers['content-type']
        except KeyError:
            return

        self._headers['content-type'] = header[0], header[1].split(';', 1)[0]

    content_type_params = property(
            _content_type_params__get,
            _content_type_params__set,
            _content_type_params__del,
            doc=_content_type_params__get.__doc__
            )

