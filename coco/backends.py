"""Custom CAS authentication backend.

Validate a CAS ticket but translate the username to some other name
(pseudo) before proceeding with authentication.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import os

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.conf import settings

from django_cas_ng.signals import cas_user_authenticated
from django_cas_ng.utils import get_cas_client

User = get_user_model()

__all__ = ['CustomCASBackend']

logger = logging.getLogger(__name__)

TRANSLATION_FILE = os.path.join(os.path.dirname(__file__), "username_translations.csv")
USERNAME_TRANSLATION = {}
try:
    with open(TRANSLATION_FILE, 'r') as f:
        for l in f:
            source, dest = l.strip().split()
            USERNAME_TRANSLATION[source] = dest
    logger.debug("Username translation enabled (%d items)." % len(USERNAME_TRANSLATION))
except IOError:
    logger.debug("No username translation file. Translation disabled.")

class CustomCASBackend(ModelBackend):
    """Custom CAS authentication backend"""

    def authenticate(self, ticket, service, request):
        """Verifies CAS ticket and gets or creates User object"""
        client = get_cas_client(service_url=service)
        username, attributes, pgtiou = client.verify_ticket(ticket)
        if attributes:
            request.session['attributes'] = attributes
        if not username:
            return None

        username_case = settings.CAS_FORCE_CHANGE_USERNAME_CASE
        if username_case == 'lower':
            username = username.lower()
        elif username_case == 'upper':
            username = username.upper()

        # We have a valid username. Look for its translation if there is one.
        username = USERNAME_TRANSLATION.get(username, username)

        try:
            user = User.objects.get(**{User.USERNAME_FIELD: username})
            created = False
        except User.DoesNotExist:
            # check if we want to create new users, if we don't fail auth
            if not settings.CAS_CREATE_USER:
                return None
            # user will have an "unusable" password
            user = User.objects.create_user(username, '')
            user.save()
            created = True

        if pgtiou and settings.CAS_PROXY_CALLBACK:
            request.session['pgtiou'] = pgtiou

        # send the `cas_user_authenticated` signal
        cas_user_authenticated.send(
            sender=self,
            user=user,
            created=created,
            attributes=attributes,
            ticket=ticket,
            service=service,
        )
        return user

    def get_user(self, user_id):
        """Retrieve the user's entry in the User model if it exists"""

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
