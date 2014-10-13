from gaesessions import get_current_session
from google.appengine.api import urlfetch
import urllib
import random as rand
import base64
import hmac
import sha
import cgi
import clock
import logging
import json

TW_BASE_URL = 'https://api.twitter.com/'
REQUEST_TOKEN_URL = TW_BASE_URL + 'oauth/request_token'
ACCESS_TOKEN_URL = TW_BASE_URL + 'oauth/access_token'
SIGNIN_URL = TW_BASE_URL + 'oauth/authenticate?oauth_token=%s'
TIMELINE_URL = TW_BASE_URL + '1.1/statuses/user_timeline.json'

methods = {urlfetch.GET: 'GET', urlfetch.POST: 'POST'}
def nonce():
    return ''.join([str(rand.randint(1, 20)) for i in range(8)])
    
def _encode(str_):
    return urllib.quote(str_, safe='')
    
def _urlencode(dict_):
    return '&'.join("%s=%s" % (_encode(str(key)), _encode(str(dict_[key])))
                    for key in sorted(dict_.keys()))
    
class Twitter(object):
    def __init__(self, consumer_key, consumer_secret, callback_url, access_token = None,
                 token_secret = None):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.callback_url = callback_url
        self.token_secret = token_secret
        self.access_token = access_token
    
    def fetch_json(self, url, params=None, method=urlfetch.GET, headers = None):
        return json.loads(self.fetch(url, params, method, headers).content)
        
    def fetch(self, url, params=None, method=urlfetch.GET, headers = None):
        params = params or {}
        headers = self.headers(url, params, method, headers)
        #logging.info(url)
        #logging.info(urllib.urlencode(params))
        #logging.info(headers)
        if method!= urlfetch.GET:
            return urlfetch.fetch(
                url,urllib.urlencode(params),
                method, headers, deadline = 60)
        return urlfetch.fetch(url +  "?" + urllib.urlencode(params),
                              deadline = 60, 
                              headers = headers)
        
    def sign(self, url, method, params, headers):
        oauth_params = [(key, value) for key, value in headers.items()
                        if key.startswith("oauth_")]
        raw_string = '&'.join([_encode(methods[method]), _encode(url),
                              _encode(_urlencode(dict(params.items() +
                                                      oauth_params)))])
        key = "%s&%s" % (self.consumer_secret, self.token_secret or '')
#        logging.info(key)
#        logging.info(raw_string)
        return base64.b64encode(hmac.new(key, raw_string, sha).digest())

        
    def headers(self, url, params=None, method=urlfetch.GET, other_headers = None):
        oauth_headers = {'oauth_nonce': nonce(),
                         'oauth_callback': self.callback_url,
                         'oauth_signature_method': "HMAC-SHA1",
                         'oauth_timestamp': str(clock.timestamp(clock.now())), 
                         'oauth_consumer_key': self.consumer_key,
                         'oauth_version': '1.0'}
        if other_headers:
            oauth_headers.update(other_headers)
        if self.access_token:
            oauth_headers['oauth_token'] = self.access_token
        oauth_headers['oauth_signature'] = self.sign(url, method, params, oauth_headers)
        oauth_headers['realm'] = ''
        
        return {'Authorization':
                'OAuth ' + ', '.join('%s="%s"' % (key, _encode(value))
                                     for key, value in oauth_headers.items())}
        
    def log_user_in(self):
        response = self.fetch(REQUEST_TOKEN_URL)
        req_toks = dict(cgi.parse_qsl(response.content))
        get_current_session()['__tmp_twitter_tokens__'] = \
            (token, secret) = (req_toks['oauth_token'], req_toks['oauth_token_secret'])
        return SIGNIN_URL % token

    def fetch_access_token(self, verifier):
        (self.access_token,
         self.token_secret) = get_current_session()['__tmp_twitter_tokens__']
        response = self.fetch(ACCESS_TOKEN_URL, headers = {'oauth_verifier': verifier})
        toks = dict(cgi.parse_qsl(response.content))
        (self.access_token,
         self.token_secret) = toks['oauth_token'], toks['oauth_token_secret']
        
        return (self.access_token, self.token_secret)