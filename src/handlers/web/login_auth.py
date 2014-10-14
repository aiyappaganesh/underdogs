import webapp2
import logging
import json

from handlers.web import WebRequestHandler
from networks import LINKEDIN, FACEBOOK, TWITTER
from facebook_config import config as fb_config
from twitter_config import config as tw_config
from linkedin_config import config as li_config
from google.appengine.api import urlfetch
from gaesessions import get_current_session
from twitter import Twitter
from model.third_party_login_data import ThirdPartyLoginData
from model.user import User

class LoginAuth():
    def __init__(self):
        self.config = None

    @staticmethod
    def get_handler_obj(network):
        if network == FACEBOOK:
            return FacebookAuth()
        elif network == TWITTER:
            return TwitterAuth()
        elif network == LINKEDIN:
            return LinkedinAuth()
        return None

    def get_login_dialog_redirect_url(self):
        return self.config['login_auth_dialog']

class FacebookAuth(LoginAuth):
    def __init__(self):
        LoginAuth.__init__(self)
        self.config = fb_config

    def parse_at(self, response):
        at = response.split('&')[0]
        return at.split('=')[1]

    def get_login_dialog_redirect_url(self):
        url = self.config['login_auth_dialog']
        return url%(self.config['client_id'], 'http://minyattra.appspot.com/users/login_success?network=' + FACEBOOK)

    def exchange_accesstoken(self, req_handler):
        at = None
        if not req_handler['error']:
            at_url = self.config['accesstoken_url']%(self.config['client_id'], req_handler.request.url, self.config['client_secret'], req_handler['code'])
            response = urlfetch.fetch(at_url).content
            at = self.parse_at(response)
        return at

    def verify_at(self, at):
        app_at_url = 'https://graph.facebook.com/oauth/access_token?client_id=%s&client_secret=%s&grant_type=client_credentials'
        response = urlfetch.fetch(app_at_url%(self.config['client_id'], self.config['client_secret'])).content
        app_at = response.split('=')[1]
        debug_url = 'https://graph.facebook.com/debug_token?input_token=%s&access_token=%s'
        response = json.loads(urlfetch.fetch(debug_url%(at, app_at)).content)
        return response['data']['user_id']

class TwitterAuth(LoginAuth):
    def __init__(self):
        LoginAuth.__init__(self)
        self.config = tw_config

    def get_login_dialog_redirect_url(self):
        tw = Twitter(self.config['consumer_key'],
                     self.config['consumer_secret'],
                     'http://minyattra.appspot.com/users/login_success?network=' + TWITTER)
        return tw.log_user_in()

    def exchange_accesstoken(self, req_handler):
        tw = Twitter(self.config['consumer_key'],
                     self.config['consumer_secret'],
                     'http://minyattra.appspot.com/users/login_success?network=' + TWITTER)
        at, ts = tw.fetch_access_token(req_handler['oauth_verifier'])
        get_current_session()['__tmp_twitter_tokens__'] = (at, ts)
        return at

    def verify_at(self, at):
        temp_at, ts = get_current_session()['__tmp_twitter_tokens__']
        tw = Twitter(self.config['consumer_key'],
                     self.config['consumer_secret'],
                     '',
                     access_token = at,
                     token_secret = ts)
        response = tw.fetch_json('https://api.twitter.com/1.1/account/verify_credentials.json',
                  {'include_entities': 'false'})
        return response['id']

class LinkedinAuth(LoginAuth):
    def __init__(self):
        LoginAuth.__init__(self)
        self.config = li_config

    def get_login_dialog_redirect_url(self):
        url = 'https://www.linkedin.com/uas/oauth2/authorization?response_type=code&client_id=%s&state=STATE&redirect_uri=%s'
        return url%(self.config['client_id'], 'http://minyattra.appspot.com/users/login_success?network='+ LINKEDIN)

    def exchange_accesstoken(self, req_handler):
        url = 'https://www.linkedin.com/uas/oauth2/accessToken?grant_type=authorization_code&code=%s&redirect_uri=%s&client_id=%s&client_secret=%s'
        url = url%(req_handler['code'], 'http://minyattra.appspot.com/users/login_success?network='+ LINKEDIN, self.config['client_id'], self.config['client_secret'])
        response = json.loads(urlfetch.fetch(url, method=urlfetch.POST).content)
        return response['access_token']

    def verify_at(self, at):
        url = 'https://api.linkedin.com/v1/people/~:(id,picture-url)?scope=r_basicprofile&format=json&oauth2_access_token=' + at
        content = urlfetch.fetch(url).content
        response = json.loads(content)
        return response['id']

class ThirdPartyLoginHandler(WebRequestHandler):
    def get_network_name(self):
        return self.request.path.split('/')[2]

    def get(self):
        network = self.get_network_name()
        handler = LoginAuth.get_handler_obj(network)
        self.redirect(handler.get_login_dialog_redirect_url())

class ThirdPartyLoginSuccessHandler(WebRequestHandler):
    def authenticate_user(self, user_id):
        curr_session = get_current_session()
        if curr_session.is_active():
            curr_session.terminate()
        curr_session['me_id'] = user_id
        curr_session['auth_only'] = True

    def login_user(self, user_id):
        curr_session = get_current_session()
        if curr_session.is_active():
            curr_session.terminate()
        tpld = ThirdPartyLoginData.get_by_key_name(str(user_id))
        user = User.get_by_key_name(tpld.parent_id)
        curr_session['me_id'] = user_id
        curr_session['me_email'] = tpld.parent_id
        curr_session['me_name'] = user.name

    def is_user_created(self, user_id):
        tpld = ThirdPartyLoginData.get_by_key_name(str(user_id))
        if tpld:
            return True
        return False

    def get(self):
        handler = LoginAuth.get_handler_obj(self['network'])
        at = handler.exchange_accesstoken(self)
        user_id = handler.verify_at(at)
        if self.is_user_created(user_id):
            self.login_user(user_id)
            self.redirect('/')
        else:
            self.authenticate_user(user_id)
            self.redirect('/member/signup?network=' + self['network'])

handlers = []
for network in [FACEBOOK, TWITTER, LINKEDIN]:
    handlers.append(('/users/' + network + '/login_callback', ThirdPartyLoginHandler))
handlers.append(('/users/login_success', ThirdPartyLoginSuccessHandler))

app = webapp2.WSGIApplication(handlers)