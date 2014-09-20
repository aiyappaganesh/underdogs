import logging
import webapp2
import urllib2
import urllib
import json

from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
from google.appengine.ext import deferred
from google.appengine.api import users

import github_config as github
import dribbble_config as dribbble
import linkedin_config as linkedin
from model.third_party_user import ThirdPartyUser
from model.user import User
from networks import GITHUB, DRIBBBLE, LINKEDIN

def get_github_auth_url():
	params = {'client_id': github.CLIENT_ID, 'redirect_uri': github.REDIRECT_URL, 'scope': github.SCOPE}
	return "%s?%s"%(github.AUTH_URL, urllib.urlencode(params))

def get_github_access_token_url(code):
	params = {'code': code, 'client_id': github.CLIENT_ID, 'client_secret': github.CLIENT_SECRET}
	return "%s?%s"%(github.ACCESS_TOKEN_URL, urllib.urlencode(params))

def get_dribbble_auth_url():
	params = {'client_id': dribbble.CLIENT_ID, 'redirect_uri': dribbble.REDIRECT_URL, 'scope': dribbble.SCOPE}
	return "%s?%s"%(dribbble.AUTH_URL, urllib.urlencode(params))

def get_linkedin_auth_url():
    params = {'response_type' : linkedin.RESPONSE_TYPE,
              'client_id' : linkedin.CLIENT_ID,
              'scope' : linkedin.SCOPE,
              'state' : linkedin.STATE,
              'redirect_uri' : linkedin.REDIRECT_URI}
    return "%s?%s"%(linkedin.AUTHORIZATION_URL, urllib.urlencode(params))

def get_linkedin_access_token_url(code):
    params = {'grant_type' : 'authorization_code',
              'code' : code,
              'redirect_uri' : linkedin.REDIRECT_URI,
              'client_id' : linkedin.CLIENT_ID,
              'client_secret' : linkedin.CLIENT_SECRET}
    return "%s?%s"%(linkedin.ACCESS_TOKEN_URL, urllib.urlencode(params))

def fetch_and_save_github_user(access_token):
	email = users.get_current_user().email()
	user = User.get_by_key_name(email)
	response = json.loads(urlfetch.fetch(github.USER_URL%access_token).content)
	id, followers = response['login'], response['followers']
	ThirdPartyUser(key_name=GITHUB, parent=user, access_token=access_token, id=id, followers=followers).put()

def fetch_and_save_dribbble_user(access_token):
	email = users.get_current_user().email()
	user = User.get_by_key_name(email)
	ThirdPartyUser(key_name=DRIBBBLE, parent=user, access_token=access_token).put()

def fetch_and_save_linkedin_user(access_token):
	email = users.get_current_user().email()
	user = User.get_by_key_name(email)
	ThirdPartyUser(key_name=LINKEDIN, parent=user, access_token=access_token).put()

class GitHubAuthHandler(webapp2.RequestHandler):
	def get(self):
		template_values = {'github_auth_url' : get_github_auth_url()}
		index_path = 'templates/users/login.html'
		self.response.out.write(template.render(index_path, template_values))

class GitHubCallbackHandler(webapp2.RequestHandler):
	def get(self):
		code = self.request.get('code')
		response = urlfetch.fetch(get_github_access_token_url(code)).content
		access_token = response.split('&')[0].split('=')[1]
		fetch_and_save_github_user(access_token)

class LinkedInAuthHandler(webapp2.RequestHandler):
    def get(self):
        response = urlfetch.fetch(get_linkedin_auth_url()).content

class LinkedInCallbackHandler(webapp2.RequestHandler):
    def get(self):
        resp_code = str(self.request.get('code'))
        resp_state = str(self.request.get('state'))
        if resp_state == linkedin.STATE:
            response = json.loads(urlfetch.fetch(get_linkedin_access_token_url(self.request.get('code')), method=urlfetch.POST).content)
            access_token = response['access_token']
            fetch_and_save_linkedin_user(access_token)

class DribbbleAuthHandler(webapp2.RequestHandler):
	def get(self):
		template_values = {'dribbble_auth_url' : get_dribbble_auth_url()}
		index_path = 'templates/users/login.html'
		self.response.out.write(template.render(index_path, template_values))

class DribbbleCallbackHandler(webapp2.RequestHandler):
	def get(self):
		code = self.request.get('code')
		params = {'code': code, 'client_id': dribbble.CLIENT_ID, 'client_secret': dribbble.CLIENT_SECRET}
		response = json.loads(urlfetch.fetch(dribbble.ACCESS_TOKEN_URL, payload=urllib.urlencode(params), method=urlfetch.POST).content)
		logging.info('callbak-----')
		logging.info(response)
		access_token = response['access_token']
		fetch_and_save_dribbble_user(access_token)

app = webapp2.WSGIApplication([	('/users/github/authorize', GitHubAuthHandler),
								('/users/github/callback', GitHubCallbackHandler),
								('/users/dribbble/authorize', DribbbleAuthHandler),
								('/users/dribbble/callback', DribbbleCallbackHandler),
								('/users/linkedin/authorize', LinkedInAuthHandler),
                                ('/users/handle_linkedin_auth', LinkedInCallbackHandler)])