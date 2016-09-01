OAuth2 Consent App
====

This app serves the prototype authorization page
for Oregon State University's developer APIs
during the 3-legged OAuth2 flow.
It is meant to be used with the corresponding apigee proxy.

Installation
----

    % git clone https://github.com/osu-mist/oauth2-consent-app.git oauth2-consent-app
    % cd oauth2-consent-app
    % virtualenv .
    % bin/pip install -e .

### Dependencies

See [setup.py](setup.py#L11).

Testing
----

Install pytest, if you haven't yet.

    % bin/pip install pytest

Run the tests.

    % bin/pytest tests

Configuration
----

    SECRET_KEY

        This key protects the app's session cookies.
        You should set it to a suitably random string.

            python -c 'print repr(open("/dev/random").read(32))'

    OAUTH_URL

        The base URL of OAuth2 proxy where this app is served.
        Example: https://api.oregonstate.edu/v1/oauth2

    CAS_URL

        The base URL to a CAS login page.
        Example: https://login.oregonstate.edu/cas

Running
----

    % CONSENT_CONFIG=config.py bin/python -m consent

This runs the consent app in debug mode.
For deploying in production, use gunicorn or another WSGI server.

Docker
----

Build a docker image with

    # docker build --tag=consent .

Run the image with

    # docker run --port 5000:8000 --volume $PWD/config.py:/src/config.py:ro consent

where 5000 is the port you want to listen on
and $PWD/config.py is the (absolute) path to your config file.

TODO
----

- We should validate the list of scopes that the application is requesting
  and display pretty explanations to the user. (Apigee does filter out invalid
  scopes, but - the way things are set up right now - not until the user has
  already submitted the consent form.)

- Maybe redirect after the user logs in with CAS to get the ticket out of the url?

- Use the built-in `SERVER_NAME` and `APPLICATION_ROOT`
  config vars instead of `OAUTH_URL`.
