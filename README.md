# Ticketbis

Python wrapper for the [Ticketbis API](http://developer.ticketbis.com/docs/).

Features:

* Python 2+3 compatibility
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

    # Construct the client object
    client = ticketbis.Ticketbis(client_id='YOUR_CLIENT_ID', client_secret='YOUR_CLIENT_SECRET', redirect_uri='http://fondu.com/oauth/authorize')

    # Build the authorization url for your app
    auth_uri = client.oauth.auth_url()

Redirect your user to the address *auth_uri* and let them authorize your app. They will then be redirected to your *redirect_uri*, with a query paramater of code=XX_CODE_RETURNED_IN_REDIRECT_XX. In your webserver, parse out the *code* value, and use it to call client.oauth.get_token()

    # Interrogate ticketbis' servers to get the user's access_token
    access_token = client.oauth.get_token('XX_CODE_RETURNED_IN_REDIRECT_XX')

    # Apply the returned access token to the client
    client.set_access_token(access_token)

    # Get the user's data
    user = client.users()

### Instantiating a client
#### [Userless Access](https://developer.ticketbis.com/overview/auth)
    client = ticketbis.Ticketbis(client_id='YOUR_CLIENT_ID', client_secret='YOUR_CLIENT_SECRET')

#### [Authenticated User Access](https://developer.ticketbis.com/overview/auth) (when you already have a user's access_token)
    client = ticketbis.Ticketbis(access_token='USER_ACCESS_TOKEN')


#### [Specifing a specific API version](https://developer.ticketbis.com/overview/versioning)
    client = ticketbis.Ticketbis(client_id='YOUR_CLIENT_ID', client_secret='YOUR_CLIENT_SECRET', version='20111215')
or

    client = ticketbis.Ticketbis(access_token='USER_ACCESS_TOKEN', version='20111215')


### Examples

#### Venues
##### [Get details about a venue](https://developer.ticketbis.com/docs/venues/venues)
    client.venues('40a55d80f964a52020f31ee3')

### Testing
In order to run the tests:
* Copy `ticketbis/tests/_creds.example.py` to `ticketbis/tests/_creds.py`
* Fill in your personal credentials to run the tests (`_creds.py` is in .gitignore)
* Run `nosetests`

## License
MIT License. See LICENSE
Copyright (c) 2015 Ticketbis
