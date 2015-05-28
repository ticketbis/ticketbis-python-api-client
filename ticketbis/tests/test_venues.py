#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# (c) 2015 Ticketbis
import logging; log = logging.getLogger(__name__)

import os

from . import TEST_DATA_DIR, BaseAuthenticatedEndpointTestCase

class VenuesEndpointTestCase(BaseAuthenticatedEndpointTestCase):
    """
    General
    """
    def test_venue(self):
        response = self.api.venues(self.default_venue_id)
        assert 'name' in response

    def test_venues(self):
        response = self.api.venues(params={'max': 2, 'offset': 0})
        assert 'name' in response[0]
        assert self.api.page_max == 2
        assert self.api.page_offset == 0
    
    #def test_venues_update(self):
    #    response = self.api.venues.update({
    #        'id': '1',
    #        'name': 'San mames API TEST 222222',
    #        'city': 'Bilbao API TEST22222',
    #        'address': 'Address API TEST2222',
    #        'country': 'ES',
    #    })
    #    assert 'city' in response
