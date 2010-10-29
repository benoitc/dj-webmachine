# -*- coding: utf-8 -
#
# This file is part of dj-webmachine released under the MIT license. 
# See the NOTICE for more information.

import uuid

from django.contrib.auth.models import User
from django.db import models

KEY_SIZE = 32
SECRET_SIZE = 32 

class KeyManager(models.Manager):

    def generate_key_secret(self):
        key = uuid.uuid4().hex
        secret = User.objects.make_random_password(SECRET_SIZE)
        return key, secret

class ConsumerManager(KeyManager):

    def create_consumer(self, name=None, description=None, user=None):
        key, secret = self.generate_key_secret()
        consumer = self.create(
                key=key, 
                secret=secret,
                name=name or '',
                description=description or '', 
                user=user
        )
        return consumer


class TokenManager(KeyManager):

    def create_token(self, consumer, token_type, timestamp, user=None):
        key, secret = self.generate_key_secret()
        token = Token.objects.create(
                key=key, 
                secret=secret, 
                token_type=token_type,
                consumer=consumer,
                timestamp=timestamp,
                user=user)
        return token

