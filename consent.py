# encoding: utf-8
from __future__ import print_function
import json
import os
import urllib
import urlparse
import requests
import xml.etree.ElementTree as elementtree
from datetime import datetime

import flask
from flask_seasurf import SeaSurf

app = flask.Flask('consent')

# Configuration defaults
app.config['SECRET_KEY'] = None
app.config['OAUTH_URL'] = 'https://osu-test.apigee.net/oauth2'
app.config['CAS_URL'] = 'https://login.oregonstate.edu/cas-dev'

# make cookies more secure
# cookies with the secure flag are only sent over HTTPS
# cookies with the HttpOnly flag are not accessible with JavaScript
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['CSRF_COOKIE_SECURE'] = True
app.config['CSRF_COOKIE_HTTPONLY'] = True

# Load user config
if 'CONSENT_CONFIG' in os.environ:
    app.config.from_envvar('CONSENT_CONFIG')

csrf = SeaSurf(app)
request = flask.request
session = flask.session

@app.after_request
def set_x_frame_options(response):
    # https://tools.ietf.org/html/rfc6749#section-10.13
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options
    response.headers.set('X-Frame-Options', 'DENY')
    return response

@app.route('/authorize')
def index():
    if not request.args.get('redirect_uri', ''):
        return 'no redirect uri provided', 400

    query_params = urllib.urlencode([
        ('client_id', request.args['client_id']),
        ('redirect_uri', request.args['redirect_uri']),
        ('scope', request.args.get('scope', '')),
        ('state', request.args.get('state', '')),
    ])

    oauth_url = app.config['OAUTH_URL']
    cas_url = app.config['CAS_URL']
    service_url = append_query(oauth_url+"/authorize", query_params)
    consent_url = append_query(oauth_url+"/consent", query_params)

    if u'ticket' in request.args:
        # got cas; validate ticket
        try:
            user = validate_cas(cas_url, request.args[u'ticket'], service_url)
        except CASError as e:
            return u'login failed (%s)' % str(e), 403
        except Exception as e:
            return u'login failed', 403

        # save user
        session['user'] = user

        # TODO: redirect after successful login?

    elif u'user' not in session:
        # redirect to cas
        return flask.redirect(cas_url+"/login?service="+urllib.quote(service_url))

    # show consent page
    year = datetime.today().year
    return flask.render_template('consent.html.j2', consent_url=consent_url, year=year)


@app.route('/consent', methods=['POST'])
def consent():
    if not request.args.get('redirect_uri', ''):
        return 'no redirect uri provided', 400

    redirect_uri = request.args['redirect_uri']

    if u'user' not in session:
        return u'not logged in', 403

    yes = (request.form['consent'] == 'yes')
    if yes:
        # user consented!
        # tell apigee to generate an auth code

        payload = {
            'client_id': request.args['client_id'],
            'redirect_uri': request.args['redirect_uri'],
            'scope': request.args.get('scope', ''),
            'state': request.args.get('state', ''),
            'response_type': 'code',
            'username': session['user'],
        }

        headers = {
            'X-grant-authorization-code': 'true',
            'Content-Type': 'application/json',
        }

        return json.dumps(payload), headers
    else:
        # user didn't consent
        state = request.args.get('state', '')
        return redirect_error(redirect_uri, state, 'access_denied')

class CASError(Exception):
    def __init__(self, msg, code=''):
        self.msg = msg
        self.code = code
    def __str__(self):
        if self.code and self.msg:
            return str(self.msg) + " (" + str(self.code) + ")"
        if self.msg:
            return str(self.msg)
        return str(self.code)

def validate_cas(cas_url, ticket, service):
    r = requests.get(cas_url+'/serviceValidate', params={'ticket': ticket, 'service': service})
    if r.status_code != 200:
        raise CASError('invalid response')

    # note: processing xml from untrusted sources is unsafe
    # https://docs.python.org/2/library/xml.html#xml-vulnerabilities
    try:
        root = elementtree.fromstring(r.text)
    except elementtree.ParseError:
        raise CASError('invalid response')

    ns = '{http://www.yale.edu/tp/cas}'
    if root.tag != ns+'serviceResponse':
        raise CASError('invalid response')

    authenticationFailure = root.find(ns+'authenticationFailure')
    authenticationSuccess = root.find(ns+'authenticationSuccess')

    if authenticationFailure is not None:
        raise CASError(authenticationFailure.text.strip(), authenticationFailure.get('code'))

    if authenticationSuccess is not None:
        user = authenticationSuccess.find(ns+'user')
        return user.text

    raise CASError('invalid response')

def redirect_error(url, state, error_code):
    return flask.redirect(append_query(url, urllib.urlencode([
        ('error', error_code),
        ('state', state),
    ])))

def append_query(url, query):
    url = urlparse.urlsplit(url)
    if url.query:
        query = url.query + '&' + query
    return urlparse.urlunsplit([url.scheme, url.netloc, url.path, query, url.fragment])

if __name__ == '__main__':
    app.run(port=5000, debug=True)
