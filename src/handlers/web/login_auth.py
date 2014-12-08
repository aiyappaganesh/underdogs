import webapp2
import logging
import json

from webapp2_extras.security import generate_password_hash, check_password_hash

from google.appengine.api.blobstore import blobstore
from handlers.web import WebRequestHandler
from networks import LINKEDIN, FACEBOOK, TWITTER
from facebook_config import config as fb_config
from twitter_config import config as tw_config
from linkedin_config import config as li_config
from google.appengine.api import urlfetch
from gaesessions import get_current_session
from twitter import Twitter
from model.third_party_login_data import ThirdPartyLoginData
from google.appengine.api import mail
from model.user import User
from model.company import Company
from model.company_members import CompanyMember
from model.signedup_member import SignedUpMember
from util import util

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
            redirect_url = 'http://minyattra.appspot.com/users/login_success?network=' + FACEBOOK
            at_url = self.config['accesstoken_url']%(self.config['client_id'], redirect_url, self.config['client_secret'], req_handler['code'])
            response = urlfetch.fetch(at_url).content
            at = self.parse_at(response)
        return at

    def get_id_and_picture(self, at):
        profile_url = 'https://graph.facebook.com/me?access_token=%s'
        response = json.loads(urlfetch.fetch(profile_url%at).content)
        user_id = response['id']
        return user_id, 'http://graph.facebook.com/' + user_id +'/picture?height=100&width=100'

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

    def get_id_and_picture(self, at):
        temp_at, ts = get_current_session()['__tmp_twitter_tokens__']
        tw = Twitter(self.config['consumer_key'],
                     self.config['consumer_secret'],
                     '',
                     access_token = at,
                     token_secret = ts)
        response = tw.fetch_json('https://api.twitter.com/1.1/account/verify_credentials.json',
                  {'include_entities': 'false'})
        return response['id'], response['profile_image_url']

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

    def get_id_and_picture(self, at):
        url = 'https://api.linkedin.com/v1/people/~:(id,picture-url)?scope=r_basicprofile&format=json&oauth2_access_token=' + at
        content = urlfetch.fetch(url).content
        response = json.loads(content)
        return response['id'], response['pictureUrl'] if 'pictureUrl' in response else ''

class ThirdPartyLoginHandler(WebRequestHandler):
    def get(self, network):
        handler = LoginAuth.get_handler_obj(network)
        self.redirect(handler.get_login_dialog_redirect_url())

class ThirdPartyLoginSuccessHandler(WebRequestHandler):
    def authenticate_user(self, user_id):
        curr_session = get_current_session()
        redirect_url = curr_session['redirect_url'] if 'redirect_url' in curr_session else None
        email = curr_session['email'] if 'email' in curr_session else None
        company_id = curr_session['company_id'] if 'company_id' in curr_session else None
        if curr_session.is_active():
            curr_session.terminate()
        curr_session['me_id'] = user_id
        curr_session['auth_only'] = True
        if email:
            curr_session['email'] = email
        if company_id:
            curr_session['company_id'] = company_id
        if redirect_url:
            curr_session['redirect_url'] = redirect_url

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

    def create_company_member(self, email, company_id):
        company = Company.get_by_id(int(company_id))
        CompanyMember(parent=company, is_admin=False, user_id=email).put()

    def save_in_memcache(self):
        session = get_current_session()
        util.add_user_to_memcache(session['me_email'])

    def get(self):
        handler = LoginAuth.get_handler_obj(self['network'])
        at = handler.exchange_accesstoken(self)
        user_id, profile_image_url = handler.get_id_and_picture(at)
        redirect_url = util.get_redirect_url_from_session()
        if self.is_user_created(user_id):
            self.login_user(user_id)
            self.save_in_memcache()
            self.redirect(redirect_url)
        else:
            self.authenticate_user(user_id)
            self.redirect('/member/signup?network=' + self['network'] + '&image=' + profile_image_url)

class CustomLoginHandler(WebRequestHandler):
    def login_user(self):
        curr_session = get_current_session()
        if curr_session.is_active():
            curr_session.terminate()
        curr_session['me_email'] = self['email']
        curr_session['me_name'] = User.get_by_key_name(self['email']).name
        curr_session['me_id'] = self['email']

    def post(self):
        email = self['email']
        user = util.get_user(email)
        if not user:
            rd_url = '/member/check_email'
        else:
            rd_url = util.get_redirect_url_from_session()
            if check_password_hash(self['password'], user.password):
                self.login_user()
                util.add_user_to_memcache(email)
            else:
                session = get_current_session()
                session.terminate()
                rd_url = '/member/verification_failed'
        self.redirect(rd_url)

class VerifyEmailHandler(WebRequestHandler):
    def post(self):
        email = self['email']
        challenge = self['recaptcha_challenge_field']
        solution = self['recaptcha_response_field']
        remote_ip = self.request.remote_addr
        is_solution_correct = util.validate_captcha(solution, challenge, remote_ip)
        if is_solution_correct:
            if SignedUpMember.is_signedup(email):
                rd_url = '/member/check_email?signup=true'
            else:
                user = util.get_user(email)
                if not user:
                    SignedUpMember.create(email)
                    self.send_subscription_email(self['email'])
                    rd_url = '/member/check_email?signup=true'
                else:
                    rd_url = '/member/user_exists'
        else:
            rd_url = '/member/signup_email'
            curr_session = get_current_session()
            curr_session['signup_email'] = self['email']
            curr_session['captcha_error'] = True
        self.redirect(rd_url)

    def send_subscription_email(self, email):
        mail.send_mail(sender="Pirates Admin <ranju@b-eagles.com>",
                       to=email,
                       subject="Confirming your email address for Pirates",
                       body="""
Hello!

Please follow this link to confirm your email id:

https://minyattra.appspot.com/users/confirm_email?email={0}

Thanks!
""".format(email))

class EmailConfirmationHandler(WebRequestHandler):
    def authenticate_user(self):
        curr_session = get_current_session()
        email = curr_session['email'] if 'email' in curr_session else self['email'] if self['email'] else None
        company_id = curr_session['company_id'] if 'company_id' in curr_session else None
        if curr_session.is_active():
            curr_session.terminate()
        curr_session['auth_only'] = True
        curr_session['me_id'] = self['email']
        if email:
            curr_session['email'] = email
        if company_id:
            curr_session['company_id'] = company_id

    def get(self):
        email = self['email']
        if not SignedUpMember.is_signedup(email):
            logging.info('... not signedup')
            return
        self.authenticate_user()
        self.redirect('/member/signup?network=custom')

handlers = []
handlers.append(('/users/([^/]+)/login_callback', ThirdPartyLoginHandler))
handlers.append(('/users/login_success', ThirdPartyLoginSuccessHandler))
handlers.append(('/users/handle_custom_login', CustomLoginHandler))
handlers.append(('/users/handle_verify_email', VerifyEmailHandler))
handlers.append(('/users/confirm_email', EmailConfirmationHandler))

app = webapp2.WSGIApplication(handlers)