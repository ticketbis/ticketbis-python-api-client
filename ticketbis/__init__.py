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
    # Enables debugging at httplib level (requests->urllib3->httplib)
    # The only thing missing will be the response.body which is not logged.
    import httplib
    httplib.HTTPConnection.debuglevel = 1

    # You must initialize logging, otherwise you'll not see debug output.
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


# Default API version.
API_VERSION = 1

# Library versioning matches supported ticketbis API version
__version__ = '0.3.1'
__author__ = u'Jose Gargallo'

API_ENDPOINT = 'https://api.ticketbis.com/'
AUTH_ENDPOINT = 'oauth/authorize/'
TOKEN_ENDPOINT = 'oauth/token/'

# Number of times to retry http requests
NUM_REQUEST_RETRIES = 1

# Max number of sub-requests per multi request
MAX_MULTI_REQUESTS = 5

# Change this if your Python distribution has issues with Ticketbis's SSL cert
VERIFY_SSL = True

# Grant types supported
AUTH_CODE_GRANT_TYPE = 'authorization_code'
CLIENT_CRED_GRANT_TYPE = 'client_credentials'


# Exceptions
class TicketbisException(Exception): pass
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
    """Ticketbis API wrapper"""

    def __init__(self, client_id=None, client_secret=None, access_token=None,
            redirect_uri=None, version=None, site=None, lang='en-gb',
            grant_type=AUTH_CODE_GRANT_TYPE, api_endpoint=API_ENDPOINT, auth=None):
        """Sets up the api object"""
        self.oauth = self.OAuth(api_endpoint, client_id, client_secret,
                redirect_uri, grant_type)
        # Set up endpoints
        self.base_requester = self.Requester(api_endpoint, client_id, client_secret,
                access_token, version, site, lang, auth)

        # Dynamically enable endpoints
        self._attach_endpoints()

        # resolves site
        if not site and access_token:
            # forces API to return site according to lang
            # (gets site from response header)
            self.sites(params={'max': 1})

    def _attach_endpoints(self):
        """Dynamically attach endpoint callables to this client"""
        for name, endpoint in inspect.getmembers(self):
            if inspect.isclass(endpoint) and issubclass(endpoint,
                    self._Endpoint) and (endpoint is not self._Endpoint):
                endpoint_instance = endpoint(self.base_requester)
                setattr(self, endpoint_instance.endpoint, endpoint_instance)

    def set_access_token(self, access_token):
        """Update the access token to use"""
        self.base_requester.set_token(access_token)

    @property
    def rate_limit(self):
        """Returns the maximum rate limit for the last API call"""
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
    def site(self):
        """Returns site name"""
        return self.base_requester.site


    @property
    def rate_remaining(self):
        """
        Returns the remaining rate limit for the last API call
        i.e. X-RateLimit-Remaining
        """
        return self.base_requester.rate_remaining

    class OAuth(object):
        """Handles OAuth authentication procedures and helps retrieve tokens"""
        def __init__(self, api_endpoint, client_id, client_secret, redirect_uri,
                grant_type):
            self.api_endpoint = api_endpoint
            self.client_id = client_id
            self.client_secret = client_secret
            self.redirect_uri = redirect_uri
            self.grant_type = grant_type

        def auth_url(self):
            """Gets the url a user needs to access to give up a user token"""
            params = {
                'client_id': self.client_id,
                'response_type': u'code',
                'redirect_uri': self.redirect_uri,
            }
            return '{API_ENDPOINT}{AUTH_ENDPOINT}?{params}'.format(
                API_ENDPOINT=self.api_endpoint,
                AUTH_ENDPOINT=AUTH_ENDPOINT,
                params=parse.urlencode(params))

        def get_token(self, code=None, scope='read write'):
            """Gets the auth token from a user's response"""
            params = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': self.grant_type,
            }

            if self.grant_type == AUTH_CODE_GRANT_TYPE:
                params['redirect_uri'] = self.redirect_uri
                if not code:
                    log.error(u'Code not provided')
                    return None
                else:
                    params['code'] = six.u(code)
            elif self.grant_type == CLIENT_CRED_GRANT_TYPE:
                params['scope'] = scope


            # Get the response from the token uri and attempt to parse
            token_endpoint = '{0}{1}'.format(self.api_endpoint, TOKEN_ENDPOINT)
            res = _post(token_endpoint, data=params)
            return res['data']['access_token']

    class Requester(object):
        """Api requesting object"""
        def __init__(self, api_endpoint, client_id=None, client_secret=None,
                access_token=None, version=None, site=None, lang=None, auth=None):
            """Sets up the api object"""
            self.client_id = client_id
            self.client_secret = client_secret
            self.set_token(access_token)
            self.version = version or API_VERSION
            self.site = site
            self.lang = lang
            self.multi_requests = list()
            self.rate_limit = None
            self.rate_remaining = None
            self.rate_remaining = None
            self.api_endpoint = api_endpoint
            self.auth = auth

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
            url = self._get_url(path)

            result = _get(url, headers=headers, params=params, auth=self.auth)
            self._set_header_properties(result)

            return result['data']

        def GET_PAGINATED(self, path, params={}, **kwargs):
            """GET request that returns data iterating over pagination"""
            params = params.copy()

            headers = self._create_headers()
            params = self._enrich_params(params)
            url = self._get_url(path)

            pending_pages = True
            while pending_pages:
                result = _get(url, headers=headers, params=params, auth=self.auth)
                self._set_header_properties(result)
                pending_pages = \
                    self.page_offset + len(result['data']) < self.total_count
                params['offset'] = self.page_offset + self.page_max
                for r in result['data']:
                    yield r

        def _set_header_properties(self, result):
            self.site = result['headers']['X-ticketbis-site']

            self.rate_limit = result['headers'].get('X-RateLimit-Limit', None)
            self.rate_remaining = result['headers'].get('X-RateLimit-Remaining', None)

            if 'X-ticketbis-totalCount' in result['headers']:
                self.total_count = \
                    int(result['headers']['X-ticketbis-totalCount'])
                self.page_offset = \
                    int(result['headers']['X-ticketbis-pageOffset'])
                self.page_max = \
                    int(result['headers']['X-ticketbis-pageMaxSize'])
            else:
                self.total_count = None
                self.page_offset = None
                self.page_max = None

        def add_multi_request(self, path, params={}):
            """Add multi request to list and return number of requests added"""
            url = path
            if params:
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
            url = self._get_url(path)
            result = _post(url, headers=headers, data=json.dumps(data), files=files, auth=self.auth)
            self.rate_limit = result['headers']['X-RateLimit-Limit']
            self.rate_remaining = result['headers']['X-RateLimit-Remaining']
            return result['data']

        def PUT(self, path, data={}, files=None):
            """PUT request that returns processed data"""
            if data is not None:
                data = data.copy()
            if files is not None:
                files = files.copy()
            headers = self._create_headers()
            data = self._enrich_params(data)
            url = self._get_url(path)
            result = _put(url, headers=headers, data=json.dumps(data), files=files, auth=self.auth)
            self.rate_limit = result['headers']['X-RateLimit-Limit']
            self.rate_remaining = result['headers']['X-RateLimit-Remaining']
            return result['data']

        def _get_url(self, path):
            return '{API_ENDPOINT}{path}'.format(
                API_ENDPOINT=self.api_endpoint,
                path=path
            )

        def _enrich_params(self, params):
            """Enrich the params dict"""
            if self.userless:
                params['client_id'] = self.client_id
                params['client_secret'] = self.client_secret
            return params

        def _create_headers(self):
            """Get the headers we need"""
            api_v = 'application/vnd.ticketbis.v{0}+json'.format(self.version)
            headers = {
                'Accept': '{0}, application/json'.format(api_v),
                'Content-Type': 'application/json',
            }

            if not self.userless:
                headers['Authorization'] = 'Bearer {0}'.format(self.oauth_token)
            if self.site:
                headers['X-ticketbis-site'] = self.site
            elif self.lang:
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

        def create(self, params={}):
            return self.POST('', params)

        def update(self, params={}):
            return self.PUT('{0}'.format(params['id']), params)

        def GET(self, path=None, auto_pagination=False, *args, **kwargs):
            """Use the requester to get the data"""
            if not auto_pagination:
                return self.requester.GET(self._expanded_path(path),
                        *args, **kwargs)
            else:
                return self.requester.GET_PAGINATED(self._expanded_path(path),
                    *args, **kwargs)

        def POST(self, path=None, *args, **kwargs):
            """Use the requester to post the data"""
            return self.requester.POST(self._expanded_path(path),
                    *args, **kwargs)

        def PUT(self, path=None, *args, **kwargs):
            """Use the requester to put the data"""
            return self.requester.PUT(self._expanded_path(path),
                    *args, **kwargs)

    class Events(_Endpoint):
        endpoint = 'events'

        def __call__(self, event_id=u'', auto_pagination=False,
                params={}, multi=False):
            return self.GET('{0}'.format(event_id), auto_pagination,
                   params=params, multi=multi)

        def section_groups(self, event_id, auto_pagination=False,
                params={}, multi=False):
            return self.GET('{0}/section_groups'.format(event_id), auto_pagination,
                   params=params, multi=multi)

    class Categories(_Endpoint):
        endpoint = 'categories'

        def __call__(self, category_id=u'', auto_pagination=False,
                params={}, multi=False):
            return self.GET('{0}'.format(category_id), auto_pagination,
                   params=params, multi=multi)

        def events(self, category_id, auto_pagination=False,
                params={}, multi=False):
            return self.GET('{0}/events'.format(category_id), auto_pagination,
                   params=params, multi=multi)

    class Sites(_Endpoint):
        endpoint = 'sites'

        def __call__(self, site_id=u'', auto_pagination=False,
                params={}, multi=False):
            return self.GET('{0}'.format(site_id), auto_pagination,
                   params=params, multi=multi)

    class Venues(_Endpoint):
        endpoint = 'venues'

        def __call__(self, venue_id=u'', auto_pagination=False,
                params={}, multi=False):
            return self.GET('{0}'.format(venue_id), auto_pagination,
                   params=params, multi=multi)

        def schemas(self, venue_id, auto_pagination=False,
                params={}, multi=False):
            return self.GET('{0}/schemas'.format(venue_id), auto_pagination,
                   params=params, multi=multi)

    class Schemas(_Endpoint):
        endpoint = 'schemas'

        def __call__(self, schema_id=u'', auto_pagination=False,
                params={}, multi=False):
            return self.GET('{0}'.format(schema_id), auto_pagination,
                   params=params, multi=multi)

    class SectionGroups(_Endpoint):
        endpoint = 'section_groups'

        def __call__(self, schema_id=u'', auto_pagination=False,
                params={}, multi=False):
            return self.GET('{0}'.format(schema_id), auto_pagination,
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
            Code processing this sequence must check the yields for their type.
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
            return int(math.ceil(
                len(self.requester.multi_requests) / float(MAX_MULTI_REQUESTS)))

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
def _get(url, headers={}, params=None, auth=None):
    """Tries to GET data from an endpoint using retries"""
    param_string = _ticketbis_urlencode(params)
    for i in xrange(NUM_REQUEST_RETRIES):
        try:
            try:
                response = requests.get(url, headers=headers,
                        params=param_string, verify=VERIFY_SSL, auth=auth)
                return _process_response(response)
            except requests.exceptions.RequestException as e:
                _log_and_raise_exception('Error connecting with ticketbis API',
                        e)
        except TicketbisException as e:
            # Some errors don't bear repeating
            if e.__class__ in [InvalidAuth, ParamError, EndpointError,
                    NotAuthorized, Deprecated]: raise
            # If we've reached our last try, re-raise
            if ((i + 1) == NUM_REQUEST_RETRIES): raise
        time.sleep(1)

def _post(url, headers={}, data=None, files=None, auth=None):
    """Tries to POST data to an endpoint"""
    try:
        response = requests.post(url, headers=headers, data=data, files=files,
                verify=VERIFY_SSL, auth=auth)
        return _process_response(response)
    except requests.exceptions.RequestException as e:
        _log_and_raise_exception('Error connecting with ticketbis API', e)

def _put(url, headers={}, data=None, files=None, auth=None):
    """Tries to PUT data to an endpoint"""
    try:
        response = requests.put(url, headers=headers, data=data, files=files,
                verify=VERIFY_SSL, auth=auth)
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
    if response.status_code in (200, 201):
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
        _log_and_raise_exception('Invalid format, missing meta property. data',
                data)

def _as_utf8(s):
    try:
        return str(s)
    except UnicodeEncodeError:
        return unicode(s).encode('utf8')

def _ticketbis_urlencode(query, doseq=0, safe_chars="&/,+"):
    # Courtesy of github.com/iambibhas
    if hasattr(query,"items"):
        query = query.items()
    else:
        try:
            if len(query) and not isinstance(query[0], tuple):
                raise TypeError
        except TypeError:
            ty,va,tb = sys.exc_info()
            raise TypeError("not valid non-string sequence").with_traceback(tb)

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
