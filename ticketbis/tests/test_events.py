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
        response = self.api.events(self.default_eventid)
        #response = self.api.events()
        assert 'name' in response

#    def test_leaderboard(self):
#        response = self.api.users.leaderboard()
#        assert 'leaderboard' in response
#
#    def test_search_twitter(self):
#        response = self.api.users.search(params={'twitter': u'mLewisLogic'})
#        assert 'results' in response
#
#    """
#    Aspects
#    """
#    def test_badges(self):
#        response = self.api.users.badges()
#        assert 'sets' in response
#        assert 'badges' in response
#
#    """
#    Actions
#    """
#    def test_update_name(self):
#        # Change my name to Miguel
#        response = self.api.users.update(params={'firstName': 'Miguel'})
#        assert 'user' in response
#        assert response['user']['firstName'] == 'Miguel'
#        # Change it back
#        response = self.api.users.update(params={'firstName': 'Mike'})
#        assert 'user' in response
#        assert response['user']['firstName'] == 'Mike'
