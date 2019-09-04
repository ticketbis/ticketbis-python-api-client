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

import os

import betamax
from betamax.fixtures import unittest
from betamax_serializers import pretty_json

import ticketbis

if (
    "CLIENT_ID" in os.environ
    and "CLIENT_SECRET" in os.environ
    and "ACCESS_TOKEN" in os.environ
    and "API_ENDPOINT" in os.environ
):
    CLIENT_ID = os.environ["CLIENT_ID"]
    CLIENT_SECRET = os.environ["CLIENT_SECRET"]
    ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
    API_ENDPOINT = os.environ["API_ENDPOINT"]
else:
    try:
        from ticketbis.tests._creds import (
            CLIENT_ID,
            CLIENT_SECRET,
            ACCESS_TOKEN,
            API_ENDPOINT,
        )
    except ImportError:
        API_ENDPOINT = "https://buscaticket.com.qa2.sh-env.net/api/"
        CLIENT_ID = "api"
        CLIENT_SECRET = "deadbeef"
        ACCESS_TOKEN = "deadbeef=="


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "testdata")

betamax.Betamax.register_serializer(pretty_json.PrettyJSONSerializer)

with betamax.Betamax.configure() as config:
    config.cassette_library_dir = os.path.join(os.path.dirname(__file__), "cassettes")
    config.default_cassette_options["serialize_with"] = "prettyjson"

    config.define_cassette_placeholder("<AUTH_TOKEN>", ACCESS_TOKEN)


class BaseEndpointTestCase(unittest.BetamaxTestCase):
    default_site_name = "ticketbisES"
    default_category_id = u"2"
    default_site_id = u"1"
    default_venue_id = u"1"
    default_schema_id = u"1"

    def setUp(self):
        super(BaseEndpointTestCase, self).setUp()
        self.session.headers.pop("Accept-Encoding", None)


class BaseAuthenticationTestCase(BaseEndpointTestCase):
    def setUp(self):
        super(BaseAuthenticationTestCase, self).setUp()
        self.api = ticketbis.Ticketbis(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri="http://ticketbis.com",
            site=self.default_site_name,
            api_endpoint=API_ENDPOINT,
            session=self.session,
        )


class BaseAuthenticatedEndpointTestCase(BaseEndpointTestCase):
    def setUp(self):
        super(BaseAuthenticatedEndpointTestCase, self).setUp()
        self.api = ticketbis.Ticketbis(
            access_token=ACCESS_TOKEN,
            site=self.default_site_name,
            api_endpoint=API_ENDPOINT,
            session=self.session,
        )


class BaseUserlessEndpointTestCase(BaseEndpointTestCase):
    def setUp(self):
        super(BaseUserlessEndpointTestCase, self).setUp()
        self.api = ticketbis.Ticketbis(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            site=self.default_site_name,
            api_endpoint=API_ENDPOINT,
            session=self.session,
        )


class MultilangEndpointTestCase(BaseEndpointTestCase):
    def setUp(self):
        super(MultilangEndpointTestCase, self).setUp()
        self.apis = []
        for lang in ("es", "fr", "de", "it", "ja", "th", "ko", "ru", "pt", "id"):
            self.apis.append(
                ticketbis.Ticketbis(
                    client_id=CLIENT_ID,
                    client_secret=CLIENT_SECRET,
                    lang=lang,
                    api_endpoint=API_ENDPOINT,
                    session=self.session,
                )
            )
