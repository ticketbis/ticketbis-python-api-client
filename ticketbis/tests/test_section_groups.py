#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# (c) 2015 Ticketbis
import logging; log = logging.getLogger(__name__)

import os

from . import TEST_DATA_DIR, BaseAuthenticatedEndpointTestCase

class SectionGroupsEndpointTestCase(BaseAuthenticatedEndpointTestCase):
    """
    General
    """

    def test_section_groups_by_event(self):
        response = self.api.events(params={'max': 1, 'offset': 0})
        assert 'id' in response[0]
        response = self.api.events.section_groups(response[0]['id'])
        assert 'name' in response[0]
