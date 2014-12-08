import webapp2
import logging

from webapp2_extras.security import generate_password_hash, check_password_hash

from google.appengine.ext import deferred
from handlers.request_handler import RequestHandler
from google.appengine.ext.webapp import blobstore_handlers
from model.third_party_user import ThirdPartyUser
from networks import GITHUB, LINKEDIN, ANGELLIST, DRIBBBLE
from user_data import github, linkedin, angellist, dribbble
from util import util
from handlers.web.web_request_handler import WebRequestHandler
from google.appengine.api import mail
from handlers.web.auth import web_login_required, web_auth_required
from model.third_party_login_data import ThirdPartyLoginData
from model.invited_member import InvitedMember
from model.signedup_member import SignedUpMember
from model.company_members import CompanyMember
from gaesessions import get_current_session
from util.util import separator, get_user, get_company_id_from_session, validate_captcha
from model.user import User
from model.company import Company

networks = {
GITHUB: github,
LINKEDIN: linkedin,
ANGELLIST: angellist,
DRIBBBLE: dribbble
}

def fetch_users_for(company):
    return CompanyMember.all().ancestor(company)

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
    logging.info(members)
    init_company(company)
    influence_total = 0.0
    expertise_total = {}
    members_count = float(members.count())
    for member in members:
        init_member(member)
        pull_data_for(member)
        (influence_total, expertise_total) = update_averages(member, influence_total, expertise_total)
    company.influence_avg = (influence_total) / members_count
    company.expertise_avg = []
    for skill, score in expertise_total.iteritems():
        company.expertise_avg.append(skill + ' : ' + str(score / members_count))
    company.put()

class MemberDataPullHandler(webapp2.RequestHandler):
    def put(self):
        company_id = int(str(self.request.get('company_id')))
        company = Company.get_by_id(company_id)
        deferred.defer(pull_company_data, company)

class MemberInviteHandler(WebRequestHandler):
    @web_login_required
    def post(self):
        email = self['email']
        company_id = int(str(self['company_id']))
        if not Company.get_by_id(company_id):
            self.write('no company')
            return
        if not util.isAdminAccess(self):
            return
        challenge = self['recaptcha_challenge_field']
        solution = self['recaptcha_response_field']
        remote_ip = self.request.remote_addr
        is_solution_correct = validate_captcha(solution, challenge, remote_ip)
        curr_session = get_current_session()
        if is_solution_correct:
            if InvitedMember.for_(email, company_id):
                curr_session['invite_error'] = "Invite already sent"
            else:
                company = Company.get_by_id(company_id)
                InvitedMember.create_(email, company_id)
                mail.send_mail(sender="Pirates Admin <ranju@b-eagles.com>",
                               to=email,
                               subject="Invitation to join " + company.name,
                               body="""
        Hello!

        Please follow this link to add yourself:

        https://minyattra.appspot.com/member/finish_invite?company_id={0}&email={1}

        Thanks!
        """.format(self['company_id'], self['email']))
                curr_session['invite_success'] = True
        else:
            curr_session['invite_email'] = self['email']
            curr_session['captcha_error'] = True
        rd_url = curr_session['rd_url']
        curr_session.pop('rd_url')
        self.redirect(rd_url)

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
    if 'email' in session:
        session.pop('email')
    if 'company_id' in session:
        session.pop('company_id')


class MemberSignupHandler(blobstore_handlers.BlobstoreUploadHandler, RequestHandler):
    def user_exists(self):
        email = self['email']
        user = User.get_by_key_name(email)
        if user:
            return True
        return False

    def create_company_member(self, email, company_id):
        company = Company.get_by_id(company_id)
        CompanyMember(parent=company, is_admin=False, user_id=email).put()

    def create_user(self, req_handler):
        photos = self.get_uploads("uploaded_photo")
        photo = self['image']
        email = req_handler['email']
        if photos:
            photo_blob_key = photos[0].key()
            photo = '/api/common/download_image/'+str(photo_blob_key)
        password_hash = generate_password_hash(req_handler['password'])
        user = User(key_name = email, name = req_handler['name'], password = password_hash, photo = photo)
        user.put()

    def delete_signedup_member(self, email):
        SignedUpMember.delete(email)

    @web_auth_required
    def post(self):
        email = self['email']
        company_id = get_company_id_from_session()
        invited_member = InvitedMember.for_(email, company_id)
        if invited_member:
            invited_member.delete()
        if not self.user_exists():
            self.delete_signedup_member(email)
            self.create_user(self)
            if company_id:
                self.create_company_member(email, company_id)
            create_tpld(email, self['network'])
            modify_session(email)
            util.add_user_to_memcache(email)
            redirect_url = util.get_redirect_url_from_session()
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
        redirect_url = util.get_redirect_url_from_session()
        email = self['email']
        user = User.get_by_key_name(email)
        if check_password_hash(self['password'], user.password):
            create_tpld(email, self['network'])
            modify_session(email)
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
