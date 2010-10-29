# -*- coding: utf-8 -
#
# This file is part of dj-webmachine released under the MIT license. 
# See the NOTICE for more information.

from django.utils.translation import ugettext_lazy as _

VERIFIER_SIZE = 16
KEY_SIZE = 32
SECRET_SIZE = 32 

# token types
TOKEN_REQUEST  = 2
TOKEN_ACCESS = 1

TOKEN_TYPES = (
    (TOKEN_ACCESS, _("Access")),
    (TOKEN_REQUEST, _("Request"))
)

# consumer states
PENDING = 1
ACCEPTED = 2
CANCELED = 3
REJECTED = 4

CONSUMER_STATES = (
    (PENDING,  _('Pending')),
    (ACCEPTED, _('Accepted')),
    (CANCELED, _('Canceled')),
    (REJECTED, _('Rejected')),
)
