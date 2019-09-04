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


class SchemasEndpointTestCase(BaseAuthenticatedEndpointTestCase):
    def test_schema(self):
        response = self.api.schemas(self.default_schema_id)
        assert "name" in response

    def test_schemas(self):
        response = self.api.schemas(params={"max": 2, "offset": 0})
        assert "name" in response[0]
        assert self.api.page_max == 2
        assert self.api.page_offset == 0

    def test_schemas_by_venue(self):
        response = self.api.venues.schemas(self.default_venue_id)
        assert "name" in response[0]
