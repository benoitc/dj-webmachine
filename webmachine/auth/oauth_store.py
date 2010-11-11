# -*- coding: utf-8 -
#
# This file is part of dj-webmachine released under the MIT license. 
# See the NOTICE for more information.

from django.contrib.auth.models import AnonymousUser

from webmachine.const import VERIFIER_SIZE, TOKEN_REQUEST, TOKEN_ACCESS
from webmachine.models import Nonce, Consumer, Token
from webmachine.util import generate_random

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

    def fetch_request_token(self, oauth_consumer, oauth_callback,
            oauth_timestamp):
        """-> OAuthToken."""
        raise NotImplementedError

    def fetch_access_token(self, oauth_consumer, oauth_token,
            oauth_verifier, oauth_timestamp):
        """-> OAuthToken."""
        raise NotImplementedError

    def authorize_request_token(self, oauth_token, user):
        """-> OAuthToken."""
        raise NotImplementedError



class DataStore(OAuthDataStore):

    def lookup_consumer(self, key):
        try:
            self.consumer = Consumer.objects.get(key=key)
        except Consumer.DoesNotExist:
            return None
        return self.consumer

    def lookup_token(self, token_type, key):
        try:
            self.request_token = Token.objects.get(
                    token_type=token_type, 
                    key=key
            )
        except Consumer.DoesNotExist:
            return None
        return self.request_token

    def lookup_nonce(self, consumer, token, nonce):
        if not token:
            return

        nonce, created = Nonce.objects.get_or_create(
                consumer_key=consumer.key,
                token_key=token.key,
                nonce=nonce
        )

        if created:
            return None
        return nonce

    def fetch_request_token(self, consumer, callback, timestamp):
        if consumer.key == self.consumer.key:
            request_token = Token.objects.create_token(
                    consumer=self.consumer,
                    token_type=TOKEN_REQUEST,
                    timestamp=timestamp
            )
                
            if callback:
                self.request_token.set_callback(callback)
            
            self.request_token = request_token
            return request_token
        return None

    def fetch_access_token(self, consumer, token, verifier, timestamp):
        if consumer.key == self.consumer.key \
        and token.key == self.request_token.key \
        and self.request_token.is_approved:
            if (self.request_token.callback_confirmed \
                    and verifier == self.request_token.verifier) \
                    or not self.request_token.callback_confirmed:

                self.access_token = Token.objects.create_token(
                    consumer=self.consumer,
                    token_type=TOKEN_ACCESS,
                    timestamp=timestamp,
                    user=self.request_token.user)
                return self.access_token
        return None

    def authorize_request_token(self, oauth_token, user):
        if oauth_token.key == self.request_token.key:
            # authorize the request token in the store
            self.request_token.is_approved = True
            if not isinstance(user, AnonymousUser):
                self.request_token.user = user
            self.request_token.verifier = generate_random(VERIFIER_SIZE)
            self.request_token.save()
            return self.request_token
        return None
