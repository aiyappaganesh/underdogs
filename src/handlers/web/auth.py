import logging
import webapp2
import urllib2
import urllib
import json

from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
from google.appengine.ext import deferred
from google.appengine.api import users

from model.company import Company
import github_config as github
import angellist_config as angellist
import linkedin_config as linkedin
import facebook_config as facebook
from model.third_party_user import ThirdPartyUser
from model.user import User
from networks import GITHUB, ANGELLIST, LINKEDIN, FACEBOOK
from handlers import RequestHandler

networks = {
    GITHUB: github,
    LINKEDIN: linkedin,
    FACEBOOK: facebook,
    ANGELLIST: angellist
}

def _user_logged_in(handler):
    logging.info(handler.session['login_id'])
    if not 'login_id' in handler.session:
        handler.redirect('/member/login?' + urllib.urlencode({'redirect_url': handler.request.url}))
        logging.info('returning false one')
        return False
    user = User.all().filter('login_id =', handler.session['login_id']).get()
    if not user:
        logging.info('returning false two')
        return False
    logging.info('returning true')
    return True

def login_required(fn):
    def check_login(self, *args):
        if _user_logged_in(self):
            fn(self, *args)
    return check_login

class Auth(object):
    def __init__(self, network):
        self.config = networks[network].config
        self._auth_url = self.config['auth_url']
        self.token_url = self.config['token_url']
        self.client_id = self.config['client_id']
        self.client_secret = self.config['client_secret']
        self.redirect_url = self.config['redirect_url']
        self.scope = self.config['scope'] if 'scope' in self.config else ''
        self.company_param = 'company_id'
        self.separator = ' : '

    def get_auth_url(self, **kwargs):
        params = {  'client_id': self.client_id,
                    'redirect_uri': "%s?%s"%(self.redirect_url, urllib.urlencode(kwargs.items())) if kwargs else self.redirect_url,
                    'scope': self.scope
        }
        return "%s?%s"%(self._auth_url, urllib.urlencode(params))

    def fetch_and_save_user(self, req_handler):
        response = urlfetch.fetch(self.get_thirdparty_access_token_url(req_handler['code'])).content
        access_token = self.get_access_token(response)
        company_id, user_id = req_handler[self.company_param].split(self.separator)
        self.save_user(access_token, company_id, user_id)
        return '/member/expose_third_party?company_id=' + company_id + '&user_id=' + user_id

    def get_thirdparty_access_token_url(self, code):
        params = {'code': code, 'client_id': self.client_id, 'client_secret': self.client_secret}
        return "%s?%s"%(self.token_url, urllib.urlencode(params))

    def get_access_token(self, response):
        return response.split('&')[0].split('=')[1]

    def save_user(self, access_token, company_id, user_id):
        pass

    def set_session(self, req_handler, login_id):
        logging.info('Setting the login_id')
        req_handler.session['login_id'] = login_id

    @staticmethod
    def get_handler_obj(req_handler):
        company_id = req_handler['company_id']
        network = req_handler['network']
        if network and network == 'facebook':
            return FacebookAuth()
        elif ANGELLIST in req_handler[AngellistAuth().company_param]:
            return AngellistAuth()
        elif company_id and len(company_id) > 0:
            return GithubAuth()
        else:
            return LinkedinAuth()


class GithubAuth(Auth):
    def __init__(self):
        Auth.__init__(self, GITHUB)

    def save_user(self, access_token, company_id, user_id):
        company = Company.get_by_id(int(company_id))
        user = User.get_by_key_name(user_id, parent=company)
        response = json.loads(urlfetch.fetch(github.USER_URL%access_token).content)
        id, followers = response['login'], response['followers']
        ThirdPartyUser(key_name=GITHUB, parent=user, access_token=access_token, id=id, followers=followers).put()

class FacebookAuth(Auth):
    def __init__(self):
        Auth.__init__(self, FACEBOOK)

    def fetch_and_save_user(self, req_handler):
        create_user = req_handler['create_user']
        access_token = req_handler['access_token']
        login_id = req_handler['id']
        redirect_url = req_handler['redirect_url']
        user = User().all().filter('login_id =', login_id).get()
        name = req_handler['name']
        if create_user == 'false':
            if not user:
                return '/member/missing?user_id=' + login_id + '&name=' + name + '&access_token=' + req_handler['access_token']
            else:
                if redirect_url:
                    return str(redirect_url)
                else:
                    return '/member/dashboard?member_id=' + login_id
        else:
            company_id = req_handler['company_id']
            if not user:
                c = Company.get_by_id(int(company_id))
                User(key_name=login_id, parent=c, login_id=login_id, name=name).put()
            return '/member/expose_third_party?company_id=' + company_id + '&user_id=' + login_id

class LinkedinAuth(Auth):
    def __init__(self):
        Auth.__init__(self, LINKEDIN)
        self.response_type = self.config['response_type']
        self.company_param = 'state'

    def fetch_and_save_user(self, req_handler):
        response = urlfetch.fetch(self.get_thirdparty_access_token_url(req_handler['code']), method=urlfetch.POST).content
        access_token = self.get_access_token(response)
        company_id, user_id = req_handler[self.company_param].split(self.separator)
        self.save_user(access_token, company_id, user_id)
        return '/member/expose_third_party?company_id=' + company_id + '&user_id=' + user_id

    def get_auth_url(self, **kwargs):
        auth_url = super(LinkedinAuth, self).get_auth_url()
        company_id = kwargs['company_id']
        user_id = kwargs['user_id']
        params = {
            'state': company_id + self.separator + user_id,
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

    def save_user(self, access_token, company_id, user_id):
        company = Company.get_by_id(int(company_id))
        user = User.get_by_key_name(user_id, parent=company)
        ThirdPartyUser(key_name=LINKEDIN, parent=user, access_token=access_token).put()

class AngellistAuth(Auth):
    def __init__(self):
        Auth.__init__(self, ANGELLIST)
        self.company_param = 'state'

    def get_auth_url(self, **kwargs):
        company_id = kwargs['company_id']
        user_id = kwargs['user_id']
        params = {
            'client_id' : self.config['client_id'],
            'state': ANGELLIST + self.separator + company_id + self.separator + user_id,
            'network': ANGELLIST,
            'response_type': 'code'
        }
        return "%s?%s"%(self.config['auth_url'], urllib.urlencode(params))

    def fetch_and_save_user(self, req_handler):
        response = urlfetch.fetch(self.get_thirdparty_access_token_url(req_handler['code']), method=urlfetch.POST).content
        logging.info(response)
        access_token = self.get_access_token(response)
        network_name, company_id, user_id = req_handler[self.company_param].split(self.separator)
        self.save_user(access_token, company_id, user_id)
        return '/member/expose_third_party?company_id=' + company_id + '&user_id=' + user_id

    def get_thirdparty_access_token_url(self, code):
        params = {'code' : code,
              'grant_type' : 'authorization_code',
              'client_id' : self.client_id,
              'client_secret' : self.client_secret}
        return "%s?%s"%(self.token_url, urllib.urlencode(params))

    def save_user(self, access_token, company_id, user_id):
        company = Company.get_by_id(int(company_id))
        user = User.get_by_key_name(user_id, parent=company)
        ThirdPartyUser(key_name=ANGELLIST, parent=user, access_token=access_token).put()

class ThirdPartyRequestHandler(RequestHandler):
    def get(self):
        handler = Auth.get_handler_obj(self)
        redirect_uri = handler.fetch_and_save_user(self)
        self.redirect(redirect_uri)

app = webapp2.WSGIApplication([ ('/users/github/callback', ThirdPartyRequestHandler),
                                ('/users/facebook/callback', ThirdPartyRequestHandler),
                                ('/users/angellist/callback', ThirdPartyRequestHandler),
                                ('/users/handle_linkedin_auth', ThirdPartyRequestHandler)])