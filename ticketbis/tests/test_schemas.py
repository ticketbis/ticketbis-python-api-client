#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# (c) 2015 Ticketbis
import logging; log = logging.getLogger(__name__)

import os

from . import TEST_DATA_DIR, BaseAuthenticatedEndpointTestCase

class SchemasEndpointTestCase(BaseAuthenticatedEndpointTestCase):
    """
    General
    """
    def test_schema(self):
        response = self.api.schemas(self.default_schema_id)
        assert 'name' in response

    def test_schemas(self):
        response = self.api.schemas(params={'max': 2, 'offset': 0})
        assert 'name' in response[0]
        assert self.api.page_max == 2
        assert self.api.page_offset == 0

    def test_schemas_by_venue(self):
        response = self.api.venues.schemas(self.default_venue_id)
        assert 'name' in response[0]
