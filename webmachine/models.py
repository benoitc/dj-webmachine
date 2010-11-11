# -*- coding: utf-8 -
#
# This file is part of dj-webmachine released under the MIT license. 
# See the NOTICE for more information.

import time
import urllib
import urlparse

from django.contrib.auth.models import User
from django.db import models

from webmachine.const import KEY_SIZE, SECRET_SIZE, VERIFIER_SIZE, \
TOKEN_TYPES, PENDING, CONSUMER_STATES

from webmachine.managers import ConsumerManager, TokenManager

def generate_random(length=SECRET_SIZE):
    return User.objects.make_random_password(length=length)

class Nonce(models.Model):
    token_key = models.CharField(max_length=KEY_SIZE)
    consumer_key = models.CharField(max_length=KEY_SIZE)
    key = models.CharField(max_length=255)

class Consumer(models.Model):
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=KEY_SIZE)
    secret = models.CharField(max_length=SECRET_SIZE)
    description = models.TextField()
    user = models.ForeignKey(User, null=True, blank=True,
            related_name="consumers_user")
    status = models.SmallIntegerField(choices=CONSUMER_STATES, 
            default=PENDING)

    objects = ConsumerManager()

    def __str__(self):
        data = {'oauth_consumer_key': self.key,
            'oauth_consumer_secret': self.secret}

        return urllib.urlencode(data)

class Token(models.Model):
    key = models.CharField(max_length=KEY_SIZE)
    secret = models.CharField(max_length=SECRET_SIZE)
    token_type = models.SmallIntegerField(choices=TOKEN_TYPES)
    callback = models.CharField(max_length=2048) #URL
    callback_confirmed = models.BooleanField(default=False)
    verifier = models.CharField(max_length=VERIFIER_SIZE)
    consumer = models.ForeignKey(Consumer,
            related_name="tokens_consumer")
    timestamp = models.IntegerField(default=time.time())
    user = models.ForeignKey(User, null=True, blank=True, 
            related_name="tokens_user")
    is_approved = models.BooleanField(default=False)
    
    objects = TokenManager()

    def set_callback(self, callback):
        self.callback = callback
        self.callback_confirmed = True
        self.save()

    def set_verifier(self, verifier=None):
        if verifier is not None:
            self.verifier = verifier
        else:
            self.verifier = generate_random(VERIFIER_SIZE)
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


    def to_string(self, only_key=False):
        token_dict = {
                'oauth_token': self.key, 
                'oauth_token_secret': self.secret,
                'oauth_callback_confirmed': self.callback_confirmed and 'true' or 'error',
        }

        if self.verifier:
            token_dict.update({ 'oauth_verifier': self.verifier })

        if only_key:
            del token_dict['oauth_token_secret']
            del token_dict['oauth_callback_confirmed']

        return urllib.urlencode(token_dict)
