from __future__ import absolute_import

import logging
import datetime

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from .sessiongateway import SessionGateway

logger = logging.getLogger(__name__)
gate = SessionGateway()

@receiver(user_logged_in)
def sig_user_logged_in(sender, user, request, **kwargs):
    gate.store_session({
        'cookie': request.session.session_key,
        'username': user.username,
        'userid': user.id,
        'login_date': datetime.datetime.now().isoformat(),
        })
    logger.debug("user logged in: %s at %s" % (user, request.META.get('REMOTE_ADDR')))

@receiver(user_logged_out)
def sig_user_logged_out(sender, user, request, **kwargs):
    gate.delete_session(request.session.session_key)
    logger.debug("user logged out: %s at %s" % (user, request.META.get('REMOTE_ADDR')))
