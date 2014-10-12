import webapp2
import logging
import json

from handlers.web import WebRequestHandler
from networks import LINKEDIN, FACEBOOK, TWITTER
from facebook_config import config as fb_config
from google.appengine.api import urlfetch
from gaesessions import get_current_session

class LoginAuth():
    def __init__(self):
        self.config = None

    @staticmethod
    def get_handler_obj(network):
        if network == FACEBOOK:
            return FacebookAuth()
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

class ThirdPartyLoginHandler(WebRequestHandler):
    def get_network_name(self):
        return self.request.path.split('/')[2]

    def get(self):
        network = self.get_network_name()
        handler = LoginAuth.get_handler_obj(network)
        logging.info(handler.get_login_dialog_redirect_url())
        self.redirect(handler.get_login_dialog_redirect_url())

class ThirdPartyLoginSuccessHandler(WebRequestHandler):
    def authenticate_user(self, user_id):
        curr_session = get_current_session()
        if curr_session.is_active():
            curr_session.terminate()
        curr_session['me_id'] = user_id
        curr_session['auth_only'] = True

    def get(self):
        handler = LoginAuth.get_handler_obj(self['network'])
        at = handler.exchange_accesstoken(self)
        user_id = handler.verify_at(at)
        self.authenticate_user(user_id)
        self.redirect('/member/signup?network=' + self['network'])

handlers = []
for network in [FACEBOOK, LINKEDIN, TWITTER]:
    handlers.append(('/users/' + network + '/login_callback', ThirdPartyLoginHandler))
handlers.append(('/users/login_success', ThirdPartyLoginSuccessHandler))

app = webapp2.WSGIApplication(handlers)