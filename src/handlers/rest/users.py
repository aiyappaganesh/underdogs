import webapp2
import logging

from google.appengine.ext import deferred
from handlers import RequestHandler
from google.appengine.ext.webapp import blobstore_handlers
from model.third_party_user import ThirdPartyUser
from model.user import User
from model.company import Company
from networks import GITHUB, LINKEDIN, ANGELLIST
from user_data import github, linkedin, angellist
from util.util import isAdminAccess, get_redirect_url_from_session
from handlers.web import WebRequestHandler
from google.appengine.api import mail
from handlers.web.auth import web_login_required, web_auth_required
from model.third_party_login_data import ThirdPartyLoginData
from model.invited_member import InvitedMember
from model.company_members import CompanyMember
from gaesessions import get_current_session
from util.util import separator, get_user

networks = {
GITHUB: github,
LINKEDIN: linkedin,
ANGELLIST: angellist
}

def fetch_users_for(company):
    members = CompanyMember.all().ancestor(company)
    return [m for m in members.fetch(200)]

def init_company(company):
    company.influence_avg = None
    company.expertise_avg = []
    company.put()

def init_member(member):
    member.influence = None
    member.expertise = []
    member.put()

def pull_data_for(member):
    for network, handler in networks.iteritems():
        key_name = network + separator + str(member.parent().key().id()) + separator + str(member.user_id)
        third_party_user = ThirdPartyUser.get_by_key_name(key_name)
        if third_party_user:
            handler.pull_data(member, third_party_user)

def update_averages(member, influence_total, expertise_total):
    if not member.influence or not member.expertise:
        return (influence_total, expertise_total)
    influence_total += member.influence
    for expertise in member.expertise:
        skill, score = expertise.split(' : ')
        if skill not in expertise_total:
            expertise_total[skill] = 0.0
        expertise_total[skill] += float(score)
    return (influence_total, expertise_total)

def pull_company_data(company):
    members = fetch_users_for(company)
    init_company(company)
    influence_total = 0.0
    expertise_total = {}
    for member in members:
        init_member(member)
        pull_data_for(member)
        (influence_total, expertise_total) = update_averages(member, influence_total, expertise_total)
    company.influence_avg = (influence_total) / float(len(members))
    company.expertise_avg = []
    for skill, score in expertise_total.iteritems():
        company.expertise_avg.append(skill + ' : ' + str(score / float(len(members))))
    company.put()

class MemberDataPullHandler(webapp2.RequestHandler):
    def put(self):
        company_id = int(self.request.get('company_id'))
        company = Company.get_by_id(company_id)
        deferred.defer(pull_company_data, company)

class MemberInviteHandler(WebRequestHandler):
    def create_invited_member(self, email, company_id):
        InvitedMember(key_name=email, company_id=company_id).put()

    @web_login_required
    def post(self):
        if not isAdminAccess(self):
            return
        company = Company.get_by_id(int(self['company_id']))
        self.create_invited_member(self['email'], int(self['company_id']))
        mail.send_mail(sender="Underdog Admin <ranju@b-eagles.com>",
                       to=self['email'],
                       subject="Invitation to join " + company.name,
                       body="""
Hello!

Please follow this link to add yourself:

https://minyattra.appspot.com/member/finish_invite?company_id={0}&email={1}

Thanks!
""".format(self['company_id'], self['email']))

def create_tpld(email, network):
    session = get_current_session()
    tpld = ThirdPartyLoginData(key_name = str(session['me_id']))
    tpld.network_name = network
    tpld.parent_id = email
    tpld.put()

def modify_session(email):
    session = get_current_session()
    session['me_email'] = email
    session.pop('auth_only')


class MemberSignupHandler(blobstore_handlers.BlobstoreUploadHandler, RequestHandler):
    def user_exists(self):
        email = self['email']
        user = User.get_by_key_name(email)
        if user:
            return True
        return False

    def create_company_member(self, req_handler):
        invited_member = InvitedMember.get_by_key_name(req_handler['email'])
        if invited_member:
            company_id = invited_member.company_id
            company = Company.get_by_id(company_id)
            CompanyMember(parent=company, is_admin=False, user_id=req_handler['email']).put()

    def create_user(self, req_handler):
        photos = self.get_uploads("uploaded_photo")
        photo = self['image']
        if photos:
            photo_blob_key = photos[0].key()
            photo = '/api/common/download_image/'+str(photo_blob_key)
        self.create_company_member(req_handler)
        user = User(key_name = req_handler['email'], name = req_handler['name'], password = req_handler['password'], photo = photo)
        user.put()

    @web_auth_required
    def post(self):
        email = self['email']
        if not self.user_exists():
            self.create_user(self)
            create_tpld(email, self['network'])
            modify_session(email)
            redirect_url = get_redirect_url_from_session()
            self.redirect(redirect_url)
        else:
            self.redirect('/member/already_exists?email=' + email + '&network=' + self['network'])

class MemberProfileUpdateHandler(blobstore_handlers.BlobstoreUploadHandler, RequestHandler):
    @web_login_required
    def post(self):
        session = get_current_session()
        email = session['me_email']
        name = self['name']
        password = self['password']
        photos = self.get_uploads("uploaded_photo")
        photo = self['image']
        if photos:
            photo_blob_key = photos[0].key()
            photo = '/api/common/download_image/'+str(photo_blob_key)
        User.update(email=email,name=name,password=password,photo=photo)
        self.redirect('/member/profile')

class MemberVerificationHandler(WebRequestHandler):
    @web_auth_required
    def post(self):
        redirect_url = get_redirect_url_from_session()
        user = User.get_by_key_name(self['email'])
        if user.password == self['password']:
            create_tpld(self['email'], self['network'])
            modify_session(self['email'])
            self.redirect(redirect_url)
        else:
            session = get_current_session()
            session.terminate()
            self.redirect('/member/verification_failed')

app = webapp2.WSGIApplication([
                                ('/api/members/pull_data', MemberDataPullHandler),
                                ('/api/members/invite', MemberInviteHandler),
                                ('/api/members/finish_signup', MemberSignupHandler),
                                ('/api/members/verify_cred', MemberVerificationHandler),
                                ('/api/members/update_profile', MemberProfileUpdateHandler)
                            ])
