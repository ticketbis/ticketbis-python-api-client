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


class SitesEndpointTestCase(BaseAuthenticatedEndpointTestCase):
    """Test endpoint for retrieving sites."""

    def test_site(self):
        """Return a single site."""
        response = self.api.sites(self.default_site_id)
        assert "name" in response

    def test_sites(self):
        """Return multiple sites using pagination."""
        response = self.api.sites(params={"max": 2, "offset": 0})
        assert "name" in response[0]
        assert self.api.page_max == 2
        assert self.api.page_offset == 0
