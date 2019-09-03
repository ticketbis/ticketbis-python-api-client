# -*- coding: utf-8 -*-
#
# Copyright (c) 2015-2019 Ticketbis
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from . import BaseAuthenticatedEndpointTestCase


class VenuesEndpointTestCase(BaseAuthenticatedEndpointTestCase):
    """Test endpoint for managing venues."""

    def test_venue(self):
        """Return a single venue."""
        response = self.api.venues(self.default_venue_id)
        assert "name" in response

    def test_venues(self):
        """Return multiple venues using pagination."""
        response = self.api.venues(params={"max": 2, "offset": 0})
        assert "name" in response[0]
        assert self.api.page_max == 2
        assert self.api.page_offset == 0

    # def test_venues_update(self):
    #    response = self.api.venues.update({
    #        'id': '1',
    #        'name': 'San mames API TEST 222222',
    #        'city': 'Bilbao API TEST22222',
    #        'address': 'Address API TEST2222',
    #        'country': 'ES',
    #    })
    #    assert 'city' in response
