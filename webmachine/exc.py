# -*- coding: utf-8 -
#
# This file is part of dj-webmachine released under the MIT. 
# See the NOTICE for more information.


from django.http import HttpResponse
from django import template


class HTTPException(Exception):

    def __init__(self, message, resp):
        Exception.__init__(self, message)
        self.__dict__['response'] = resp

    def __call__(self):
        return self.response

class DjangoHttpException(HttpResponse, HTTPException):
    status_code = 200
    title = None
    explanation = ''
    body_template = """\
{{explanation|safe}}<br><br>
{{detail|safe}}
{{comment|safe}}"""

    ## Set this to True for responses that should have no request body
    empty_body = False

    def __init__(self, detail=None, body_template=None, comment=None, **kw):
        HttpResponse.__init__(
                self,
                status = '%s %s' % (self.code, self.title), 
                **kw)
        Exception.__init__(self, detail)


        if comment is not None:
            self.comment = comment

        if body_template is not None:
            self.body_template = body_template
        if isinstance(self.explanation, (list, tuple)):
            self.explanation = "<p>%s</p>" % "<br>".join(self.explanation)


        if not self.empty_body:
            t = template.Template(self.body_template)
            c = template.Context(dict(
                detail=detail,
                explanation=self.explanation,
                comment=comment))

            self._container = [t.render(c)]
        else:
            self._container = ['']
        self._is_string = True




class HTTPOk(DjangoHttpException):
    """ return response with Status 200 """
    title = "OK"

class HTTPError(DjangoHttpException):
    code = 400

############################################################
## 2xx success
############################################################

class HTTPCreated(HTTPOk):
    code = 201
    title = 'Created'

class HTTPAccepted(HTTPOk):
    code = 202
    title = 'Accepted'
    explanation = 'The request is accepted for processing.'

class HTTPNonAuthoritativeInformation(HTTPOk):
    code = 203
    title = 'Non-Authoritative Information'

class HTTPNoContent(HTTPOk):
    code = 204
    title = 'No Content'
    empty_body = True

class HTTPResetContent(HTTPOk):
    code = 205
    title = 'Reset Content'
    empty_body = True

class HTTPPartialContent(HTTPOk):
    code = 206
    title = 'Partial Content'

############################################################
## 4xx client error
############################################################

class HTTPClientError(HTTPError):
    """
    base class for the 400's, where the client is in error

    This is an error condition in which the client is presumed to be
    in-error.  This is an expected problem, and thus is not considered
    a bug.  A server-side traceback is not warranted.  Unless specialized,
    this is a '400 Bad Request'
    """
    code = 400
    title = 'Bad Request'
    explanation = ('The server could not comply with the request since\r\n'
                   'it is either malformed or otherwise incorrect.\r\n')

class HTTPBadRequest(HTTPClientError):
    pass

class HTTPUnauthorized(HTTPClientError):
    code = 401
    title = 'Unauthorized'
    explanation = (
        'This server could not verify that you are authorized to\r\n'
        'access the document you requested.  Either you supplied the\r\n'
        'wrong credentials (e.g., bad password), or your browser\r\n'
        'does not understand how to supply the credentials required.\r\n')

class HTTPPaymentRequired(HTTPClientError):
    code = 402
    title = 'Payment Required'
    explanation = ('Access was denied for financial reasons.')

class HTTPForbidden(HTTPClientError):
    code = 403
    title = 'Forbidden'
    explanation = ('Access was denied to this resource.')

class HTTPNotFound(HTTPClientError):
    code = 404
    title = 'Not Found'
    explanation = ('The resource could not be found.')

class HTTPMethodNotAllowed(HTTPClientError):
    code = 405
    title = 'Method Not Allowed'
    
class HTTPNotAcceptable(HTTPClientError):
    code = 406
    title = 'Not Acceptable'


class HTTPProxyAuthenticationRequired(HTTPClientError):
    code = 407
    title = 'Proxy Authentication Required'
    explanation = ('Authentication with a local proxy is needed.')

class HTTPRequestTimeout(HTTPClientError):
    code = 408
    title = 'Request Timeout'
    explanation = ('The server has waited too long for the request to '
                   'be sent by the client.')

class HTTPConflict(HTTPClientError):
    code = 409
    title = 'Conflict'
    explanation = ('There was a conflict when trying to complete '
                   'your request.')

class HTTPGone(HTTPClientError):
    code = 410
    title = 'Gone'
    explanation = ('This resource is no longer available.  No forwarding '
                   'address is given.')

class HTTPLengthRequired(HTTPClientError):
    code = 411
    title = 'Length Required'
    explanation = ('Content-Length header required.')

class HTTPPreconditionFailed(HTTPClientError):
    code = 412
    title = 'Precondition Failed'
    explanation = ('Request precondition failed.')

class HTTPRequestEntityTooLarge(HTTPClientError):
    code = 413
    title = 'Request Entity Too Large'
    explanation = ('The body of your request was too large for this server.')

class HTTPRequestURITooLong(HTTPClientError):
    code = 414
    title = 'Request-URI Too Long'
    explanation = ('The request URI was too long for this server.')

class HTTPUnsupportedMediaType(HTTPClientError):
    code = 415
    title = 'Unsupported Media Type'


class HTTPRequestRangeNotSatisfiable(HTTPClientError):
    code = 416
    title = 'Request Range Not Satisfiable'
    explanation = ('The Range requested is not available.')

class HTTPExpectationFailed(HTTPClientError):
    code = 417
    title = 'Expectation Failed'
    explanation = ('Expectation failed.')

class HTTPUnprocessableEntity(HTTPClientError):
    ## Note: from WebDAV
    code = 422
    title = 'Unprocessable Entity'
    explanation = 'Unable to process the contained instructions'

class HTTPLocked(HTTPClientError):
    ## Note: from WebDAV
    code = 423
    title = 'Locked'
    explanation = ('The resource is locked')

class HTTPFailedDependency(HTTPClientError):
    ## Note: from WebDAV
    code = 424
    title = 'Failed Dependency'
    explanation = ('The method could not be performed because the requested '
                   'action dependended on another action and that action failed')

############################################################
## 5xx Server Error
############################################################


class HTTPServerError(HTTPError):
    """
    base class for the 500's, where the server is in-error

    This is an error condition in which the server is presumed to be
    in-error.  This is usually unexpected, and thus requires a traceback;
    ideally, opening a support ticket for the customer. Unless specialized,
    this is a '500 Internal Server Error'
    """
    code = 500
    title = 'Internal Server Error'
    explanation = (
      'The server has either erred or is incapable of performing\r\n'
      'the requested operation.\r\n')

class HTTPInternalServerError(HTTPServerError):
    pass

class HTTPNotImplemented(HTTPServerError):
    code = 501
    title = 'Not Implemented'


class HTTPBadGateway(HTTPServerError):
    code = 502
    title = 'Bad Gateway'
    explanation = ('Bad gateway.')

class HTTPServiceUnavailable(HTTPServerError):
    code = 503
    title = 'Service Unavailable'
    explanation = ('The server is currently unavailable. '
                   'Please try again at a later time.')

class HTTPGatewayTimeout(HTTPServerError):
    code = 504
    title = 'Gateway Timeout'
    explanation = ('The gateway has timed out.')

class HTTPVersionNotSupported(HTTPServerError):
    code = 505
    title = 'HTTP Version Not Supported'
    explanation = ('The HTTP version is not supported.')

class HTTPInsufficientStorage(HTTPServerError):
    code = 507
    title = 'Insufficient Storage'
    explanation = ('There was not enough space to save the resource')

