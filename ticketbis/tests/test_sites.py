#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# (c) 2015 Ticketbis
import logging; log = logging.getLogger(__name__)

import os

from . import TEST_DATA_DIR, BaseAuthenticatedEndpointTestCase

class SitesEndpointTestCase(BaseAuthenticatedEndpointTestCase):
    """
    General
    """
    def test_site(self):
        response = self.api.sites(self.default_site_id)
        assert 'name' in response

    def test_sites(self):
        response = self.api.sites(params={'max': 2, 'offset': 0})
        assert 'name' in response[0]
        assert self.api.page_max == 2
        assert self.api.page_offset == 0
