# -*- coding: utf-8 -
#
# This file is part of dj-webmachine released under the MIT license. 
# See the NOTICE for more information.

import random
import urllib
import urlparse
import uuid

from django.contrib.auth.models import User
from django.db import models

from webmachine.util import keygen

KEY_SIZE = 32
SECRET_SIZE = 256
VERIFIER_SIZE = 16
TOKEN_TYPES = ('access', 'request')

def generate_nonce(length=8):
    """Generate pseudorandom number."""
    return ''.join([str(random.randint(0, 9)) for i in range(length)])

def generate_verifier(length=8):
    """Generate pseudorandom number."""
    return ''.join([str(random.randint(0, 9)) for i in range(length)])


def create_consumer(user=None):
    key = uuid.UUID4().hex
    secret = keygen(SECRET_SIZE)
    consumer = Consumer.objects.create(key=key, secret=secret, user=user)
    return consumer

def create_token():
    key = uuid.UUID4().hex
    secret = keygen(SECRET_SIZE)
    token = Token.objects.create(key=key, secret=secret)
    return token

class Nonce(models.models):
    token_key = models.CharField(max_length=KEY_SIZE)
    consumer_key = models.CharField(max_length=KEY_SIZE)
    key = models.CharField(max_length=255)

class Consumer(models.Model):

    key = models.CharField(max_length=KEY_SIZE)
    secret = models.CharField(max_length=SECRET_SIZE)
    user = models.ForeignKey(User, null=True, blank=True)

    def __str__(self):
        data = {'oauth_consumer_key': self.key,
            'oauth_consumer_secret': self.secret}

        return urllib.urlencode(data)

class Token(models.Models):

    key = models.CharField(max_length=KEY_SIZE)
    secret = models.CharField(max_length=SECRET_SIZE)
    callback = models.CharField(max_length=2048) #URL
    callback_confirmed = models.BooleanField(default=False)
    verifier = models.CharField(max_length=VERIFIER_SIZE)

    def set_callback(self, callback):
        self.callback = callback
        self.callback_confirmed = True
        self.save()

    def set_verifier(self, verifier=None):
        if verifier is not None:
            self.verifier = verifier
        else:
            self.verifier = generate_verifier()
        self.save()

    def get_callback_url(self):
        if self.callback and self.verifier:
            # Append the oauth_verifier.
            parts = urlparse.urlparse(self.callback)
            scheme, netloc, path, params, query, fragment = parts[:6]
            if query:
                query = '%s&oauth_verifier=%s' % (query, self.verifier)
            else:
                query = 'oauth_verifier=%s' % self.verifier
            return urlparse.urlunparse((scheme, netloc, path, params,
                query, fragment))
        return self.callback
