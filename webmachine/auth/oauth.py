# -*- coding: utf-8 -
#
# This file is part of dj-webmachine released under the MIT license. 
# See the NOTICE for more information.

from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.utils.importlib import import_module

try:
    from restkit.util import oauth2
except ImportError:
    raise ImportError("restkit packages is needed for auth.")

from webmachine.auth.base import Auth
from webmachine.util.const import TOKEN_REQUEST, TOKEN_ACCESS


def load_oauth_datastore():
    datastore = getattr(settings, 'OAUTH_DATASTORE', 
            'webmachine.auth.oauth_store.DataStore')
    i = datastore.rfind('.')
    module, clsname = datastore[:i], datastore[i+1:]
    try:
        mod = import_module(module)
    except ImportError:
        raise ImproperlyConfigured("oauth datastore module '%s' isn't valid" % module)

    try:
        cls = getattr(mod, clsname)
    except AttributeError:
        raise ImproperlyConfigured("oauth datastore '%s' doesn't exist in '%s' module" % (clsname, module))
    return cls


class OAuthServer(oauth2.Server):

    def __init__(self, datastore):
        self.datastore = datastore
        super(OAuthServer, self).__init__()

    def fetch_request_token(self, oauth_request):
        """Processes a request_token request and returns the
        request token on success.
        """
        try:
            # Get the request token for authorization.
            token = self._get_token(oauth_request, TOKEN_REQUEST)
        except oauth2.Error:
            # No token required for the initial token request.
            timestamp = self._get_timestamp(oauth_request)
            version = self._get_version(oauth_request)
            consumer = self._get_consumer(oauth_request)
            try:
                callback = self.get_callback(oauth_request)
            except oauth2.Error:
                callback = None # 1.0, no callback specified.

            #hack
            
            self._check_signature(oauth_request, consumer, None)
            # Fetch a new token.
            token = self.datastore.fetch_request_token(consumer,
                    callback, timestamp)
        return token

    def fetch_access_token(self, oauth_request):
        """Processes an access_token request and returns the
        access token on success.
        """
        timestamp = self._get_timestamp(oauth_request)
        version = self._get_version(oauth_request)
        consumer = self._get_consumer(oauth_request)
        try:
            verifier = self._get_verifier(oauth_request)
        except oauth2.Error:
            verifier = None
        # Get the request token.
        token = self._get_token(oauth_request, TOKEN_REQUEST)
        self._check_signature(oauth_request, consumer, token)
        new_token = self.datastore.fetch_access_token(consumer, token,
                verifier, timestamp)
        return new_token

    def verify_request(self, oauth_request):
        consumer = self._get_consumer(oauth_request)
        token = self._get_token(oauth_request, TOKEN_ACCESS)
        parameters = super(OAuthServer, self).verify_request(oauth_request,
                consumer, token)
        return consumer, token, parameters

    def authorize_token(self, token, user):
        """Authorize a request token."""
        return self.datastore.authorize_request_token(token, user)

    def get_callback(self, oauth_request):
        """Get the callback URL."""
        return oauth_request.get_parameter('oauth_callback')

    def _get_consumer(self, oauth_request):
        consumer_key = oauth_request.get_parameter('oauth_consumer_key')
        consumer = self.datastore.lookup_consumer(consumer_key)
        if not consumer:
            raise oauth2.Error('Invalid consumer.')
        return consumer

    def _get_token(self, oauth_request, token_type=TOKEN_ACCESS):
        """Try to find the token for the provided request token key."""
        token_field = oauth_request.get_parameter('oauth_token')
        token = self.datastore.lookup_token(token_type, token_field)
        if not token:
            raise oauth2.Error('Invalid %s token: %s' % (token_type, token_field))
        return token

    def _check_nonce(self, consumer, token, nonce):
        """Verify that the nonce is uniqueish."""
        nonce = self.datastore.lookup_nonce(consumer, token, nonce)
        if nonce:
            raise oauth2.Error('Nonce already used: %s' % str(nonce))

    def _get_timestamp(self, oauth_request):
        return int(oauth_request.get_parameter('oauth_timestamp'))

class Oauth(Auth):

    def __init__(self, realm="OAuth"):
        oauth_datastore = load_oauth_datastore()
        self.realm = realm
        self.oauth_server = OAuthServer(oauth_datastore())
        self.oauth_server.add_signature_method(oauth2.SignatureMethod_PLAINTEXT())
        self.oauth_server.add_signature_method(oauth2.SignatureMethod_HMAC_SHA1())

    def authorized(self, req, resp):
        params = {}
        headers = {}

        if req.method == "POST":
            params = req.REQUEST.items()

        if 'HTTP_AUTHORIZATION' in req.META:
            headers['Authorization'] = req.META.get('HTTP_AUTHORIZATION')


        oauth_request = oauth2.Request.from_request(req.method, 
            req.build_absolute_uri(), headers=headers,
            parameters=params,
            query_string=req.META.get('QUERY_STRING'))

        if not oauth_request:
            return 'OAuth realm="%s"' % self.realm

        try:
            consumer, token, params = self.oauth_server.verify_request(oauth_request)
        except oauth2.Error, err:
            resp.content = str(err)
            return 'OAuth realm="%s"' % self.realm 
       
        req.user = consumer.user
        return True
