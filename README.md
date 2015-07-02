# Ticketbis

Python wrapper for the [Ticketbis API](http://api.ticketbis.com).

NOTE: This document is a *work in progress*.

Features:

* Python 2+3 compatibility
* Site auto-discovery
* Pagination delegated to the API client
* OAuth2
* Automatic retries

Dependencies:

* requests

## Installation

    pip install ticketbis

or

    easy_install ticketbis

Depending upon your system and virtualenv settings, these may require sudo permissions.

[PyPi page](https://pypi.python.org/pypi/ticketbis)

## Usage

### Authentication

#### Authorization code

```python
# Construct the client object
client = ticketbis.Ticketbis(
    client_id='YOUR_CLIENT_ID', 
    client_secret='YOUR_CLIENT_SECRET', 
    redirect_uri='http://yoururl.example.com')

# Build the authorization url for your app
auth_uri = client.oauth.auth_url()
```

Redirect your user to the address *auth_uri* and let them authorize your app. They will then be redirected to your *redirect_uri*, with a query paramater of code=XX_CODE_RETURNED_IN_REDIRECT_XX. In your webserver, parse out the *code* value, and use it to call client.oauth.get_token()

```python
# Interrogate ticketbis' servers to get the user's access_token
access_token = client.oauth.get_token('XX_CODE_RETURNED_IN_REDIRECT_XX')

# Apply the returned access token to the client
client.set_access_token(access_token)

# Get sites
sites = client.sites()
```

#### Client credentials

```python
# Construct the client object
client = ticketbis.Ticketbis(
    client_id='YOUR_CLIENT_ID', 
    client_secret='YOUR_CLIENT_SECRET', 
    grant_type=ticketbis.CLIENT_CRED_GRANT_TYPE)

# Interrogate ticketbis' servers to get the client's access_token (no code required)
access_token = client.oauth.get_token()

# Apply the returned access token to the client
client.set_access_token(access_token)

# Get sites
sites = client.sites()
```
    
### Instantiating a client
#### Userless Access

```python
client = ticketbis.Ticketbis(
    client_id='YOUR_CLIENT_ID', 
    client_secret='YOUR_CLIENT_SECRET')
```

#### Authenticated User Access

```python
client = ticketbis.Ticketbis(access_token='USER_ACCESS_TOKEN')
```

#### Specific API version

```python
client = ticketbis.Ticketbis(
    client_id='YOUR_CLIENT_ID', 
    client_secret='YOUR_CLIENT_SECRET', 
    version=2)
```

or

```python
client = ticketbis.Ticketbis(access_token='USER_ACCESS_TOKEN', version=2)
```

#### Resolving Site
Since Ticketbis is a multi-site platform, a `site` or `lang` is required. If you are connecting to a specific site, it is recommended to use the `site` parameter:

```python
client = ticketbis.Ticketbis(
    client_id='YOUR_CLIENT_ID', 
    client_secret='YOUR_CLIENT_SECRET', 
    site='ticketbisES')
```
Ticketbis can auto-discover the site based on the `lang` parameter (i.e. user's locale):

```python
client = ticketbis.Ticketbis(
    client_id='YOUR_CLIENT_ID', 
    client_secret='YOUR_CLIENT_SECRET', 
    lang='en-gb')
```

A few Ticketbis sites are listed below:

| name              | site                       | lang  |
| ----------------- | -------------------------- | ----- |
| ticketbisES       | www.ticketbis.com          | es-es |
| ticketbisIT       | www.ticketbis.it           | it-it |
| ticketbisGB       | www.ticketbis.net          | en-gb |
| ticketbisMX       | www.ticketbis.com.mx       | es-mx |
| ticketbisAR       | www.ticketbis.com/ar       | es-ar |
| ticketbisBR       | www.ticketbis.com.br       | pt-br |
| ticketbisPT       | www.ticketbis.com.pt       | pt-pt |
| ticketbisDE       | www.ticketbis.com/de-de    | de-de |
| ticketbisRU       | www.ticketbis.ru           | ru-ru |
| ticketbisCL       | www.ticketbis.cl           | es-cl |
| ticketbisCO       | www.ticketbis.com.co       | es-co |
| ticketbisFR       | www.ticketbisfr.com        | fr-fr |
| ticketbisJP       | www.ticketbis.com/jp       | ja-jp |
| ticketbisTW       | www.ticketbis.com/tw       | zh-tw |
| ticketbisKR       | www.ticketbis.co.kr        | ko-kr |
| ticketbisUS       | www.ticketbis.com/en       | en-us |

A complete list can be found requesting site's API endpont.

### Examples

#### Sites

```python
sites = client.sites()
```

#### Events for a specific category

```python
events = client.categories.events(category_id=2)
```

#### Events for a specific category delegating pagination to the API client

```python
events = client.categories.events(2, auto_pagination=True)
```

### Testing
In order to run the tests:
* Copy `ticketbis/tests/_creds.example.py` to `ticketbis/tests/_creds.py`
* Fill in your personal credentials to run the tests (`_creds.py` is in .gitignore)
* Run `nosetests`

## License
MIT License. See LICENSE
Copyright (c) 2015 Ticketbis
