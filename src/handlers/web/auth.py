import logging
import webapp2
import urllib2
import urllib
import json
import sys

from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
from google.appengine.ext import deferred
from google.appengine.api import users

from model.company import Company
from model.third_party_login_data import ThirdPartyLoginData
from model.third_party_profile_data import ThirdPartyProfileData
import github_config as github
import angellist_config as angellist
import linkedin_config as linkedin
import facebook_config as facebook
from model.third_party_user import ThirdPartyUser
from model.user import User
from networks import GITHUB, ANGELLIST, LINKEDIN, FACEBOOK
from handlers import RequestHandler
from gaesessions import get_current_session
from util.util import separator
from user_data.linkedin import pull_profile_data as linkedin_profile_data_pull
from user_data.angellist import pull_profile_data as angellist_profile_data_pull

networks = {
    GITHUB: github,
    LINKEDIN: linkedin,
    FACEBOOK: facebook,
    ANGELLIST: angellist
}

def _user_logged_in(handler):
    session = get_current_session()
    if session.is_active() and 'me_id' in session:
        if 'auth_only' in session:
            session.terminate()
            return False
        else:
            return True
    return False

def _user_authenticated(handler):
    session = get_current_session()
    if session.is_active() and \
        'me_id' in session and \
        'auth_only' in session and \
        session['auth_only'] is True:
        return True
    return False

def web_login_required(fn):
    def check_login(self, *args):
        if _user_logged_in(self):
            fn(self, *args)
        else:
            self.redirect('/member/missing?redirect_url=' + self.request.path + ('?' + self.request.query_string if self.request.query_string else ''))
    return check_login

def web_auth_required(fn):
    def check_auth(self, *args):
        if _user_authenticated(self):
            fn(self, *args)
        else:
            self.redirect('/member/not_authenticated?redirect_url=' + self.request.path + ('?' + self.request.query_string if self.request.query_string else ''))
    return check_auth

class Auth(object):
    def __init__(self, network, redirect_url):
        self.network = network
        self.config = networks[network].config
        self._auth_url = self.config['auth_url']
        self.token_url = self.config['token_url']
        self.client_id = self.config['client_id']
        self.client_secret = self.config['client_secret']
        self.redirect_url = redirect_url if redirect_url else self.config['redirect_url']
        self.scope = self.config['scope'] if 'scope' in self.config else ''
        self.company_param = 'company_id'
        self.separator = ' : '

    def get_auth_url(self, **kwargs):
        params = {  'client_id': self.client_id,
                    'redirect_uri': "%s?%s"%(self.redirect_url, urllib.urlencode(kwargs.items())) if kwargs else self.redirect_url,
                    'scope': self.scope
        }
        return "%s?%s"%(self._auth_url, urllib.urlencode(params))

    def is_user_created(self, req_handler):
        tp_id = req_handler['id']
        tpld = ThirdPartyLoginData.get_by_key_name(tp_id)
        logging.info(tp_id)
        if tpld:
            return True
        return False

    def fetch_and_save_user(self, req_handler):
        response = urlfetch.fetch(self.get_thirdparty_access_token_url(req_handler['code'])).content
        access_token = self.get_access_token(response)
        company_id = req_handler[self.company_param]
        session = get_current_session()
        self.save_user(access_token, company_id, session['me_email'])
        return '/member/expose_third_party?company_id=' + company_id

    def get_thirdparty_access_token_url(self, code):
        params = {'code': code, 'client_id': self.client_id, 'client_secret': self.client_secret}
        return "%s?%s"%(self.token_url, urllib.urlencode(params))

    def get_access_token(self, response):
        return response.split('&')[0].split('=')[1]

    def save_user(self, access_token, company_id, user_id):
        key_name = self.network + separator + str(company_id) + separator + str(user_id)
        tp_user = ThirdPartyUser(key_name=key_name, access_token=access_token)
        tp_user.put()
        return tp_user

    def set_session(self, req_handler, login_id):
        logging.info('Setting the login_id')
        req_handler.session['login_id'] = login_id

    @staticmethod
    def get_handler(network, redirect_url=None):
        if network == LINKEDIN:
            return LinkedinAuth(redirect_url=redirect_url)
        elif network == ANGELLIST:
            return AngellistAuth(redirect_url=redirect_url)
        elif network == GITHUB:
            return GithubAuth(redirect_url=redirect_url)

class GithubAuth(Auth):
    def __init__(self, redirect_url=None):
        Auth.__init__(self, GITHUB, redirect_url)

    def save_user(self, access_token, company_id, user_id):
        tp_user = Auth.save_user(self, access_token, company_id, user_id)
        response = json.loads(urlfetch.fetch(github.USER_URL%access_token).content)
        id, followers = response['login'], response['followers']
        tp_user.id = id
        tp_user.followers = followers
        tp_user.put()

class LinkedinAuth(Auth):
    def __init__(self, redirect_url=None):
        Auth.__init__(self, LINKEDIN, redirect_url)
        self.response_type = self.config['response_type']
        self.company_param = 'state'

    def fetch_and_save_user(self, req_handler):
        response = urlfetch.fetch(self.get_thirdparty_access_token_url(req_handler['code']), method=urlfetch.POST).content
        access_token = self.get_access_token(response)
        company_id = req_handler[self.company_param]
        session = get_current_session()
        self.save_user(access_token, company_id, session['me_email'])
        return '/member/expose_third_party?company_id=' + company_id

    def get_auth_url(self, **kwargs):
        auth_url = super(LinkedinAuth, self).get_auth_url()
        company_id = kwargs.get('company_id', None)
        user_id = kwargs.get('user_id', None)
        params = {
            'state': company_id,
            'response_type': self.response_type
        }
        return "%s&%s"%(auth_url, urllib.urlencode(params))

    def get_thirdparty_access_token_url(self, code):
        params = {'grant_type' : 'authorization_code',
              'code' : code,
              'redirect_uri' : self.redirect_url,
              'client_id' : self.client_id,
              'client_secret' : self.client_secret}
        return "%s?%s"%(self.token_url, urllib.urlencode(params))

    def get_access_token(self, response):
        return json.loads(response)['access_token']

    def save_third_party_profile_date(self, access_token, email):
        user = User.get_by_key_name(email)
        ThirdPartyProfileData(key_name=self.network, parent=user, access_token=access_token).put()

    def fetch_and_save_profile(self, req_handler):
        response = urlfetch.fetch(self.get_thirdparty_access_token_url(req_handler['code']), method=urlfetch.POST).content
        access_token = self.get_access_token(response)
        session = get_current_session()
        self.save_third_party_profile_date(access_token, session['me_email'])
        return '/member/profile'

class AngellistAuth(Auth):
    def __init__(self, redirect_url=None):
        Auth.__init__(self, ANGELLIST, redirect_url)
        self.company_param = 'state'

    def get_auth_url(self, **kwargs):
        company_id = kwargs.get('company_id', None)
        user_id = kwargs.get('user_id', None)
        params = {
            'client_id' : self.config['client_id'],
            'state': ANGELLIST + self.separator + company_id + self.separator + user_id,
            'network': ANGELLIST,
            'response_type': 'code'
        }
        return "%s?%s"%(self.config['auth_url'], urllib.urlencode(params))

    def fetch_and_save_user(self, req_handler):
        url = "%s?client_id=%s&client_secret=%s&code=%s&grant_type=authorization_code" % (self.token_url, self.client_id, self.client_secret, req_handler['code'])
        try:
            headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
            params = urllib.urlencode({})
            response = urllib2.urlopen(urllib2.Request(url, params, headers))
            json_data = json.loads(response.read())
            access_token = json_data['access_token']
        except:
            logging.info(sys.exc_info())
            access_token = ''
        network, company_id, user_id = req_handler[self.company_param].split(self.separator)
        self.save_user(access_token, company_id, user_id)
        return '/member/expose_third_party?company_id=' + company_id + '&user_id=' + user_id

def set_session(req_handler):
    logging.info('In set session')
    curr_session = get_current_session()
    if curr_session.is_active():
        logging.info('In terminate')
        curr_session.terminate()
    curr_session['me_id'] = req_handler['id']
    curr_session['me_access_token'] = req_handler['access_token']
    curr_session['me_name'] = req_handler['name']
    return curr_session

class ThirdPartyProfileHandler(RequestHandler):
    def get(self, network):
        handler = Auth.get_handler(network, redirect_url='http://minyattra.appspot.com/users/profile/' + network + '/update_success')
        self.redirect(handler.get_auth_url())

class ThirdPartyProfileSuccessHandler(RequestHandler):
    def get_profile_data_pull_handler(self, network):
        if network == LINKEDIN:
            return linkedin_profile_data_pull
        elif network == ANGELLIST:
            return angellist_profile_data_pull

    def get(self, network):
        handler = Auth.get_handler(network, redirect_url='http://minyattra.appspot.com/users/profile/' + network + '/update_success')
        redirect_url = handler.fetch_and_save_profile(self)
        session = get_current_session()
        user = User.get_by_key_name(session['me_email'])
        data_pull_handler = self.get_profile_data_pull_handler(network)
        third_party_profile_data = ThirdPartyProfileData.get_by_key_name(network, parent=user)
        data_pull_handler(third_party_profile_data)
        self.redirect(redirect_url)

class ThirdPartyDataHandler(RequestHandler):
    def get(self, network):
        company_id = self['company_id']
        user_id = self['user_id']
        handler = Auth.get_handler(network, redirect_url='http://minyattra.appspot.com/users/data/' + network + '/update_success')
        self.redirect(handler.get_auth_url(company_id=company_id, user_id=user_id))

class ThirdPartyDataSuccessHandler(RequestHandler):
    def authenticate_user(self):
        session = set_session(self)
        session['auth_only'] = True

    @web_login_required
    def get(self, network):
        handler = Auth.get_handler(network, redirect_url='http://minyattra.appspot.com/users/data/' + network + '/update_success')
        redirect_uri = handler.fetch_and_save_user(self)
        self.redirect(redirect_uri)

app = webapp2.WSGIApplication([ ('/users/data/([^/]+)/update', ThirdPartyDataHandler),
                                ('/users/data/([^/]+)/update_success', ThirdPartyDataSuccessHandler),
                                ('/users/profile/([^/]+)/update', ThirdPartyProfileHandler),
                                ('/users/profile/([^/]+)/update_success', ThirdPartyProfileSuccessHandler)
                                ])