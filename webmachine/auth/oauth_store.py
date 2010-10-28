# -*- coding: utf-8 -
#
# This file is part of dj-webmachine released under the MIT license. 
# See the NOTICE for more information.

from webmachine.models import Nonce, Consumer, Token, \
create_consumer, create_token
from webmachine.util import keygen

class OAuthDataStore(object):
    """A database abstraction used to lookup consumers and tokens."""

    def lookup_consumer(self, key):
        """-> OAuthConsumer."""
        raise NotImplementedError

    def lookup_token(self, token_type, key):
        """-> OAuthToken."""
        raise NotImplementedError

    def lookup_nonce(self, oauth_consumer, oauth_token, nonce):
        """-> OAuthToken."""
        raise NotImplementedError

    def fetch_request_token(self, oauth_consumer, oauth_callback):
        """-> OAuthToken."""
        raise NotImplementedError

    def fetch_access_token(self, oauth_consumer, oauth_token, oauth_verifier):
        """-> OAuthToken."""
        raise NotImplementedError

    def authorize_request_token(self, oauth_token, user):
        """-> OAuthToken."""
        raise NotImplementedError



class DataStore(OAuthDataStore):

    def lookup_consumer(self, key):
        return Consumer.objects.get(key=key)

    def lookup_token(self, token_type, key):
        return Token.objects.get(token_type, key)


