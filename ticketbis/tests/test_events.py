#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# (c) 2015 Ticketbis
import logging; log = logging.getLogger(__name__)

import os

from . import TEST_DATA_DIR, BaseAuthenticatedEndpointTestCase

class EventsEndpointTestCase(BaseAuthenticatedEndpointTestCase):
    """
    General
    """
    def test_event(self):
        response = self.api.events(self.default_event_id)
        assert 'name' in response

    def test_events(self):
        response = self.api.events(params={'max': 2, 'offset': 0})
        assert 'name' in response[0]
        assert self.api.page_max == 2
        assert self.api.page_offset == 0

    def test_events_by_category(self):
        response = self.api.categories.events(self.default_category_id, 
                params={'max': 2, 'offset': 0})
        assert 'name' in response[0]
