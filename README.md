OAuth2 Consent App
====

This app serves the prototype authorization page
for Oregon State University's developer APIs
during the 3-legged OAuth2 flow.
It is meant to be used with the corresponding [apigee proxy][].

[apigee proxy]:

Installation
----

    % git clone https://github.com/osu-mist/oauth2-consent-app.git oauth2-consent-app
    % cd oauth2-consent-app
    % virtualenv .
    % bin/pip install -e .

Configuration
----

    SECRET_KEY

        This key protects the app's session cookies.
        You should set it to a suitably random string.

            python -c 'print repr(open("/dev/random").read(32))'

    OAUTH_URL

        The base URL of OAuth2 proxy where this app is served.

    CAS_URL

        The base URL to OSU's CAS login page.
        You probably want to stick with the default unless you're testing.

Running
----

    % CONSENT_CONFIG=config.py bin/python -m consent

This runs the consent app in debug mode.
For deploying in production, use gunicorn or another WSGI server.
