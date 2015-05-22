#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# (c) 2015 Ticketbis
import logging; log = logging.getLogger(__name__)

# Try to load JSON libraries in this order:
# ujson -> simplejson -> json
try:
    import ujson as json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        import json

import inspect
import math
import time
import sys

# 3rd party libraries that might not be present during initial install
#  but we need to import for the version #
try:
    import requests

    from six.moves.urllib import parse
    from six.moves import xrange
    import six

    # Monkey patch to requests' json using ujson when available;
    # Otherwise it wouldn't affect anything
    requests.models.json = json
except ImportError:
    pass


# Helpful for debugging what goes in and out
NETWORK_DEBUG = False
if NETWORK_DEBUG:
    # These two lines enable debugging at httplib level (requests->urllib3->httplib)
    # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
    # The only thing missing will be the response.body which is not logged.
    import httplib
    httplib.HTTPConnection.debuglevel = 1
    # You must initialize logging, otherwise you'll not see debug output.
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


# Default API version. Move this forward as the library is maintained and kept current
API_VERSION_YEAR  = '2015'
API_VERSION_MONTH = '06'
API_VERSION_DAY   = '01'
API_VERSION = 1

# Library versioning matches supported ticketbis API version
__version__ = '1!{year}.{month}.{day}'.format(year=API_VERSION_YEAR, month=API_VERSION_MONTH, day=API_VERSION_DAY)
__author__ = u'Jose Gargallo'

AUTH_ENDPOINT = 'http://api.ticketbis.com.local:8000/oauth/authorize'
TOKEN_ENDPOINT = 'http://api.ticketbis.com.local:8000/oauth/token'
API_ENDPOINT = 'http://api.ticketbis.com.local:8000/'

# Number of times to retry http requests
NUM_REQUEST_RETRIES = 1

# Max number of sub-requests per multi request
MAX_MULTI_REQUESTS = 5

# Change this if your Python distribution has issues with Ticketbis's SSL cert
VERIFY_SSL = True


# Generic ticketbis exception
class TicketbisException(Exception): pass
# Specific exceptions
class InvalidAuth(TicketbisException): pass
class ParamError(TicketbisException): pass
class EndpointError(TicketbisException): pass
class NotAuthorized(TicketbisException): pass
class RateLimitExceeded(TicketbisException): pass
class Deprecated(TicketbisException): pass
class ServerError(TicketbisException): pass
class FailedGeocode(TicketbisException): pass
class Other(TicketbisException): pass

error_types = {
    'invalid_auth': InvalidAuth,
    'param_error': ParamError,
    'endpoint_error': EndpointError,
    'not_authorized': NotAuthorized,
    'rate_limit_exceeded': RateLimitExceeded,
    'deprecated': Deprecated,
    'server_error': ServerError,
    'failed_geocode': FailedGeocode,
    'other': Other,
}



class Ticketbis(object):
    """Ticketbis V1 API wrapper"""

    def __init__(self, client_id=None, client_secret=None, access_token=None, redirect_uri=None, version=None, lang=None):
        """Sets up the api object"""
        # Set up OAuth
        self.oauth = self.OAuth(client_id, client_secret, redirect_uri)
        # Set up endpoints
        self.base_requester = self.Requester(client_id, client_secret, access_token, version, lang)
        # Dynamically enable endpoints
        self._attach_endpoints()

    def _attach_endpoints(self):
        """Dynamically attach endpoint callables to this client"""
        for name, endpoint in inspect.getmembers(self):
            if inspect.isclass(endpoint) and issubclass(endpoint, self._Endpoint) and (endpoint is not self._Endpoint):
                endpoint_instance = endpoint(self.base_requester)
                setattr(self, endpoint_instance.endpoint, endpoint_instance)

    def set_access_token(self, access_token):
        """Update the access token to use"""
        self.base_requester.set_token(access_token)

    @property
    def rate_limit(self):
        """Returns the maximum rate limit for the last API call i.e. X-RateLimit-Limit"""
        return self.base_requester.rate_limit

    @property
    def total_count(self):
        """Returns the total count of items when listing"""
        return self.base_requester.total_count

    @property
    def page_offset(self):
        """Returns current offset when listing"""
        return self.base_requester.page_offset

    @property
    def page_max(self):
        """Returns the max items per page when listing"""
        return self.base_requester.page_max


    @property
    def rate_remaining(self):
        """Returns the remaining rate limit for the last API call i.e. X-RateLimit-Remaining"""
        return self.base_requester.rate_remaining

    class OAuth(object):
        """Handles OAuth authentication procedures and helps retrieve tokens"""
        def __init__(self, client_id, client_secret, redirect_uri):
            self.client_id = client_id
            self.client_secret = client_secret
            self.redirect_uri = redirect_uri

        def auth_url(self):
            """Gets the url a user needs to access to give up a user token"""
            params = {
                'client_id': self.client_id,
                'response_type': u'code',
                'redirect_uri': self.redirect_uri,
            }
            return '{AUTH_ENDPOINT}?{params}'.format(
                AUTH_ENDPOINT=AUTH_ENDPOINT,
                params=parse.urlencode(params))

        def get_token(self, code):
            """Gets the auth token from a user's response"""
            if not code:
                log.error(u'Code not provided')
                return None
            params = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': u'authorization_code',
                'redirect_uri': self.redirect_uri,
                'code': six.u(code),
            }
            # Get the response from the token uri and attempt to parse
            return _get(TOKEN_ENDPOINT, params=params)['data']['access_token']


    class Requester(object):
        """Api requesting object"""
        def __init__(self, client_id=None, client_secret=None, access_token=None, version=None, lang=None):
            """Sets up the api object"""
            self.client_id = client_id
            self.client_secret = client_secret
            self.set_token(access_token)
            self.version = version or API_VERSION
            self.lang = lang
            self.multi_requests = list()
            self.rate_limit = None
            self.rate_remaining = None
            self.rate_remaining = None

            """ pagination """
            self.total_count = None
            self.page_offset = None
            self.page_max = None

        def set_token(self, access_token):
            """Set the OAuth token for this requester"""
            self.oauth_token = access_token
            self.userless = not bool(access_token) # Userless if no access_token

        def GET(self, path, params={}, **kwargs):
            """GET request that returns processed data"""
            params = params.copy()
            # Short-circuit multi requests
            if kwargs.get('multi') is True:
                return self.add_multi_request(path, params)
            # Continue processing normal requests
            headers = self._create_headers()
            params = self._enrich_params(params)
            url = '{API_ENDPOINT}{path}'.format(
                API_ENDPOINT=API_ENDPOINT,
                path=path
            )

            result = _get(url, headers=headers, params=params)
            self._set_header_properties(result)

            return result['data']

        def GET_PAGINATED(self, path, params={}, **kwargs):
            """GET request that returns processed data iterating over pagination"""
            params = params.copy()

            headers = self._create_headers()
            params = self._enrich_params(params)
            url = '{API_ENDPOINT}{path}'.format(
                API_ENDPOINT=API_ENDPOINT,
                path=path
            )

            pending_pages = True
            while pending_pages:
                result = _get(url, headers=headers, params=params)
                self._set_header_properties(result)
                pending_pages = self.page_offset + len(result['data']) < self.total_count
                params['offset'] = self.page_offset + self.page_max
                for r in result['data']:
                    yield r

        def _set_header_properties(self, result):
            self.rate_limit = result['headers']['X-RateLimit-Limit']
            self.rate_remaining = result['headers']['X-RateLimit-Remaining']
            if 'X-ticketbis-totalCount' in result['headers']:
                self.total_count = int(result['headers']['X-ticketbis-totalCount'])
                self.page_offset = int(result['headers']['X-ticketbis-pageOffset'])
                self.page_max = int(result['headers']['X-ticketbis-pageMaxSize'])
            else:
                self.total_count = None
                self.page_offset = None
                self.page_max = None

        def add_multi_request(self, path, params={}):
            """Add multi request to list and return the number of requests added"""
            url = path
            if params:
                # First convert the params into a query string then quote the whole string
                # so it will fit into the multi request query -as a value for the requests= query param-
                url += '?{0}'.format(parse.quote_plus(parse.urlencode(params)))
            self.multi_requests.append(url)
            return len(self.multi_requests)

        def POST(self, path, data={}, files=None):
            """POST request that returns processed data"""
            if data is not None:
                data = data.copy()
            if files is not None:
                files = files.copy()
            headers = self._create_headers()
            data = self._enrich_params(data)
            url = '{API_ENDPOINT}{path}'.format(
                API_ENDPOINT=API_ENDPOINT,
                path=path
            )
            result = _post(url, headers=headers, data=data, files=files)
            self.rate_limit = result['headers']['X-RateLimit-Limit']
            self.rate_remaining = result['headers']['X-RateLimit-Remaining']
            return result['data']

        def _enrich_params(self, params):
            """Enrich the params dict"""
            if self.userless:
                params['client_id'] = self.client_id
                params['client_secret'] = self.client_secret
            return params

        def _create_headers(self):
            """Get the headers we need"""
            headers = {
                'Accept': 'application/vnd.ticketbis.v{0}+json, application/json'.format(self.version)
            }

            if not self.userless:
                headers['Authorization'] = 'Bearer {0}'.format(self.oauth_token)
            # If we specified a specific language, use that
            if self.lang:
                headers['Accept-Language'] = self.lang
            return headers


    class _Endpoint(object):
        """Generic endpoint class"""
        def __init__(self, requester):
            """Stores the request function for retrieving data"""
            self.requester = requester

        def _expanded_path(self, path=None):
            """Gets the expanded path, given this endpoint"""
            return '{expanded_path}'.format(
                expanded_path='/'.join(p for p in (self.endpoint, path) if p)
            )

        def GET(self, path=None, auto_pagination=False, *args, **kwargs):
            """Use the requester to get the data"""
            if not auto_pagination:
                return self.requester.GET(self._expanded_path(path), *args, **kwargs)
            else:
                return self.requester.GET_PAGINATED(self._expanded_path(path), 
                    *args, **kwargs)

        def POST(self, path=None, *args, **kwargs):
            """Use the requester to post the data"""
            return self.requester.POST(self._expanded_path(path), *args, **kwargs)


    class Events(_Endpoint):
        endpoint = 'events'

        def __call__(self, event_id=u'', auto_pagination=False, params={}, multi=False):
            return self.GET('{0}'.format(event_id), auto_pagination, 
                   params=params, multi=multi)

    class Categories(_Endpoint):
        endpoint = 'categories'

        def __call__(self, category_id=u'', auto_pagination=False, params={}, multi=False):
            return self.GET('{0}'.format(category_id), auto_pagination,
                   params=params, multi=multi)

        def events(self, category_id, auto_pagination=False, params={}, multi=False):
            return self.GET('{0}/events'.format(category_id), auto_pagination, 
                   params=params, multi=multi)

    class Multi(_Endpoint):
        """Multi request endpoint handler"""
        endpoint = 'multi'

        def __len__(self):
          return len(self.requester.multi_requests)

        def __call__(self):
            """
            Generator to process the current queue of multi's

            note: This generator will yield both data and TicketbisException's
            The code processing this sequence must check the yields for their type.
            The exceptions should be handled by the calling code, or raised.
            """
            while self.requester.multi_requests:
                # Pull n requests from the multi-request queue
                requests = self.requester.multi_requests[:MAX_MULTI_REQUESTS]
                del(self.requester.multi_requests[:MAX_MULTI_REQUESTS])
                # Process the 4sq multi request
                params = {
                    'requests': ','.join(requests),
                }
                responses = self.GET(params=params)['responses']
                # ... and yield out each individual response
                for response in responses:
                    # Make sure the response was valid
                    try:
                        _raise_error_from_response(response)
                        yield response['response']
                    except TicketbisException as e:
                        yield e

        @property
        def num_required_api_calls(self):
            """Returns the expected number of API calls to process"""
            return int(math.ceil(len(self.requester.multi_requests) / float(MAX_MULTI_REQUESTS)))

def _log_and_raise_exception(msg, data, cls=TicketbisException):
  """Calls log.error() then raises an exception of class cls"""
  data = u'{0}'.format(data)
  # We put data as a argument for log.error() so error tracking systems such
  # as Sentry will properly group errors together by msg only
  log.error(u'{0}: %s'.format(msg), data)
  raise cls(u'{0}: {1}'.format(msg, data))

"""
Network helper functions
"""
def _get(url, headers={}, params=None):
    """Tries to GET data from an endpoint using retries"""
    param_string = _ticketbis_urlencode(params)
    for i in xrange(NUM_REQUEST_RETRIES):
        try:
            try:
                response = requests.get(url, headers=headers, params=param_string, verify=VERIFY_SSL)
                return _process_response(response)
            except requests.exceptions.RequestException as e:
                _log_and_raise_exception('Error connecting with ticketbis API', e)
        except TicketbisException as e:
            # Some errors don't bear repeating
            if e.__class__ in [InvalidAuth, ParamError, EndpointError, NotAuthorized, Deprecated]: raise
            # If we've reached our last try, re-raise
            if ((i + 1) == NUM_REQUEST_RETRIES): raise
        time.sleep(1)

def _post(url, headers={}, data=None, files=None):
    """Tries to POST data to an endpoint"""
    try:
        response = requests.post(url, headers=headers, data=data, files=files, verify=VERIFY_SSL)
        return _process_response(response)
    except requests.exceptions.RequestException as e:
        _log_and_raise_exception('Error connecting with ticketbis API', e)

def _process_response(response):
    """Make the request and handle exception processing"""
    # Read the response as JSON
    try:
        data = response.json()
    except ValueError:
        _log_and_raise_exception('Invalid response', response.text)

    # Default case, Got proper response
    if response.status_code == 200:
        return { 'headers': response.headers, 'data': data }
    return _raise_error_from_response(data)

def _raise_error_from_response(data):
    """Processes the response data"""
    # Check the meta-data for why this request failed
    meta = data.get('meta')
    if meta:
        # Account for ticketbis conflicts
        # see: https://developer.ticketbis.com/overview/responses
        if meta.get('code') in (200, 409): return data
        exc = error_types.get(meta.get('errorType'))
        if exc:
            raise exc(meta.get('errorDetail'))
        else:
            _log_and_raise_exception('Unknown error. meta', meta)
    else:
        _log_and_raise_exception('Response format invalid, missing meta property. data', data)

def _as_utf8(s):
    try:
        return str(s)
    except UnicodeEncodeError:
        return unicode(s).encode('utf8')

def _ticketbis_urlencode(query, doseq=0, safe_chars="&/,+"):
    """Gnarly hack because ticketbis doesn't properly handle standard url encoding"""
    # Original doc: http://docs.python.org/2/library/urllib.html#urllib.urlencode
    # Works the same way as urllib.urlencode except two differences -
    # 1. it uses `quote()` instead of `quote_plus()`
    # 2. it takes an extra parameter called `safe_chars` which is a string
    #    having the characters which should not be encoded.
    #
    # Courtesy of github.com/iambibhas
    if hasattr(query,"items"):
        # mapping objects
        query = query.items()
    else:
        # it's a bother at times that strings and string-like objects are
        # sequences...
        try:
            # non-sequence items should not work with len()
            # non-empty strings will fail this
            if len(query) and not isinstance(query[0], tuple):
                raise TypeError
            # zero-length sequences of all types will get here and succeed,
            # but that's a minor nit - since the original implementation
            # allowed empty dicts that type of behavior probably should be
            # preserved for consistency
        except TypeError:
            ty,va,tb = sys.exc_info()
            raise TypeError("not a valid non-string sequence or mapping object").with_traceback(tb)

    l = []
    if not doseq:
        # preserve old behavior
        for k, v in query:
            k = parse.quote(_as_utf8(k), safe=safe_chars)
            v = parse.quote(_as_utf8(v), safe=safe_chars)
            l.append(k + '=' + v)
    else:
        for k, v in query:
            k = parse.quote(_as_utf8(k), safe=safe_chars)
            if isinstance(v, six.string_types):
                v = parse.quote(_as_utf8(v), safe=safe_chars)
                l.append(k + '=' + v)
            else:
                try:
                    # is this a sufficient test for sequence-ness?
                    len(v)
                except TypeError:
                    # not a sequence
                    v = parse.quote(_as_utf8(v), safe=safe_chars)
                    l.append(k + '=' + v)
                else:
                    # loop over the sequence
                    for elt in v:
                        l.append(k + '=' + parse.quote(_as_utf8(elt)))
    return '&'.join(l)
