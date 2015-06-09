#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# (c) 2015 Ticketbis

import os
import unittest

import ticketbis

if 'CLIENT_ID' in os.environ and 'CLIENT_SECRET' in os.environ \
        and 'ACCESS_TOKEN' in os.environ and 'API_ENDPOINT' in os.environ:
    CLIENT_ID = os.environ['CLIENT_ID']
    CLIENT_SECRET = os.environ['CLIENT_SECRET']
    ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
    API_ENDPOINT = os.environ['API_ENDPOINT']
else:
    try:
        from ticketbis.tests._creds import *
    except ImportError:
        print("Please create a creds.py file in this package, based upon creds.example.py")


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'testdata')


class BaseEndpointTestCase(unittest.TestCase):
    default_site_name = 'ticketbisES'
    default_category_id = u'2'
    default_site_id = u'1'
    default_venue_id = u'1'
    default_schema_id = u'1'

class BaseAuthenticationTestCase(BaseEndpointTestCase):
    def setUp(self):
        self.api = ticketbis.Ticketbis(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri='http://ticketbis.com',
            site=self.default_site_name,
            api_endpoint=API_ENDPOINT
        )

class BaseAuthenticatedEndpointTestCase(BaseEndpointTestCase):
    def setUp(self):
        self.api = ticketbis.Ticketbis(
#            client_id=CLIENT_ID,
#            client_secret=CLIENT_SECRET,
            access_token=ACCESS_TOKEN,
            site=self.default_site_name,
            api_endpoint=API_ENDPOINT
        )

class BaseUserlessEndpointTestCase(BaseEndpointTestCase):
    def setUp(self):
        self.api = ticketbis.Ticketbis(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            site=self.default_site_name,
            api_endpoint=API_ENDPOINT
        )

class MultilangEndpointTestCase(BaseEndpointTestCase):
    def setUp(self):
        self.apis = []
        for lang in ('es', 'fr', 'de', 'it', 'ja', 'th', 'ko', 'ru', 'pt', 'id'):
            self.apis.append(
                ticketbis.Ticketbis(
                    client_id=CLIENT_ID,
                    client_secret=CLIENT_SECRET,
                    lang=lang,
                    api_endpoint=API_ENDPOINT
                )
            )
