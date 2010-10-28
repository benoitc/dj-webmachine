# -*- coding: utf-8 -
#
# This file is part of dj-webmachine released under the MIT license. 
# See the NOTICE for more information.

from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.utils.importlib import import_module

try:
    from restkit.utils import oauth2
except ImportError:
    try:
        import oauth2
    except ImportError:
        raise ImportError("oauth2 module is needed. Install restkit or"
        " python-oauth2.")

from webmachine.auth.base import Auth

def load_oauth_datastore(self):
    datastore = getattr(settings, 'OAUTH_DATASTORE', 
            'webmachine.auth.oauth_store.DataStore')
    i = datastore.rfind('.')
    module, clsname = datastore[:i], datastore[i+1:]
    try:
        mod = import_module(module)
    except ImportError:
        raise ImproperlyConfigured("oauth datastore module '%s' "
            "isn't valid" % module)

    try:
        cls = getattr(mod, clsname)
    except AttributeError:
        raise ImproperlyConfigured("oauth datastore '%s' doesn't exist"
                " in '%s' module" % (clsname, module))
    return cls


class OAuthServer(oauth2.Server):

    def __init__(self, datastore):
        self.datastore = datastore
        super(OAuthServer, self).__init__()
    
    def verify_request(self, oauth_request):
        consumer = self._get_consumer(oauth_request)
        token = self._get_token(oauth_request, 'access')
        parameters = super(OAuthServer, self).verify_request(oauth_request,
                consumer, token)
        return consumer, token, parameters

    def _get_consumer(self, oauth_request):
        consumer_key = oauth_request.get_parameter('oauth_consumer_key')
        consumer = self.datastore.lookup_consumer(consumer_key)
        if not consumer:
            raise oauth2.Error('Invalid consumer.')
        return consumer

    def _get_token(self, oauth_request, token_type='access'):
        """Try to find the token for the provided request token key."""
        token_field = oauth_request.get_parameter('oauth_token')
        token = self.datastore.lookup_token(token_type, token_field)
        if not token:
            raise oauth2.Error('Invalid %s token: %s' % (token_type, token_field))
        return token


class Oauth(Auth):

    def __init__(self, realm="OAuth"):
        oauth_datastore = load_oauth_datastore()
        self.realm = realm
        self.oauth_server = OAuthServer(oauth_datastore())
        self.oauth_server.add_signature_method(oauth2.OAuthSignatureMethod_PLAINTEXT())
        self.oauth_server.add_signature_method(oauth2.OAuthSignatureMethod_HMAC_SHA1())

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
            return False

        try:
            consumer, token, params = self.oauth_server.verify_request(oauth_request)
        except oauth2.Error, err:
            resp.content = str(err)
            return 'OAuth realm="%s"' % self.realm 
       
        req.user = consumer.user
        return True
