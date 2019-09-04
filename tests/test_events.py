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
# limitations under the License

from . import BaseAuthenticatedEndpointTestCase


class EventsEndpointTestCase(BaseAuthenticatedEndpointTestCase):
    def test_events(self):
        response = self.api.events(params={"max": 2, "offset": 0})
        assert "id" in response[0]
        assert self.api.page_max == 2
        assert self.api.page_offset == 0

        response = self.api.events(response[0]["id"])
        assert "name" in response

    def test_events_by_category(self):
        response = self.api.categories.events(
            self.default_category_id, params={"max": 2, "offset": 0}
        )
        assert "name" in response[0]

    def test_event_pagination(self):
        response = self.api.events(auto_pagination=True, params={"max": 1})
        r = next(response)
        r = next(response)
        assert "name" in r
