import requests
import pytest

def test_append_query():
    from consent import append_query
    assert append_query('http://oregonstate.edu', 'error=access_denied') == 'http://oregonstate.edu?error=access_denied'
    assert append_query('https://oregonstate.edu/?this=that', 'error=access_denied') == 'https://oregonstate.edu/?this=that&error=access_denied'
    assert append_query('https://oregonstate.edu/#footer', 'error=access_denied') == 'https://oregonstate.edu/?error=access_denied#footer'

    assert append_query('https://oregonstate.edu/path/?a=1&b=2', 'c=3&d=4') == 'https://oregonstate.edu/path/?a=1&b=2&c=3&d=4'

def test_redirect_error():
    from consent import redirect_error
    r = redirect_error('http://oregonstate.edu', '!@#$%^&*', 'access_denied')
    url = r.headers['location']
    assert url == 'http://oregonstate.edu?error=access_denied&state=%21%40%23%24%25%5E%26%2A'

def test_validate_redirect_uri():
    from consent import validate_redirect_uri
    validate_redirect_uri('https://oregonstate.edu')
    validate_redirect_uri('https://oregonstate.edu:80')
    validate_redirect_uri('https://oregonstate.edu/path')
    validate_redirect_uri('https://oregonstate.edu?foo=bar')
    validate_redirect_uri('https://oregonstate.edu?error=error')
    validate_redirect_uri('http://127.0.0.1/')
    validate_redirect_uri('http://127.0.0.1:5000/')

def test_invalid_redirect_uri():
    from consent import validate_redirect_uri
    from werkzeug.exceptions import BadRequest
    with pytest.raises(BadRequest):
        validate_redirect_uri('http://oregonstate.edu') # not https

    with pytest.raises(BadRequest):
        validate_redirect_uri('index.html') # no scheme

    with pytest.raises(BadRequest):
        validate_redirect_uri('https://oregonstate.edu/#blah') # has fragment

    with pytest.raises(BadRequest):
        validate_redirect_uri('https://') # no host

    with pytest.raises(BadRequest):
        validate_redirect_uri('https://:') # no host

    with pytest.raises(BadRequest):
        validate_redirect_uri('') # empty string

    with pytest.raises(BadRequest):
        validate_redirect_uri('http://localhost')

    with pytest.raises(BadRequest):
        # don't confuse userinfo with a host name
        validate_redirect_uri('http://127.0.0.1:x@evil.com')
