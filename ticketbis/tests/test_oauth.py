#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# (c) 2015 Ticketbis
import logging; log = logging.getLogger(__name__)

from . import BaseAuthenticationTestCase
import six
import ticketbis


class OAuthEndpointTestCase(BaseAuthenticationTestCase):
    def test_auth_url(self):
        url = self.api.oauth.auth_url()
        assert isinstance(url, six.string_types)

    def test_get_token(self):
        # Honestly, not much we can do to test here
        pass
