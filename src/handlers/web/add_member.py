from google.appengine.api.blobstore import blobstore
import webapp2
from handlers.web import WebRequestHandler
from google.appengine.api import users
import logging
import json

from handlers.web.auth import web_login_required
from model.user import User
from model.company_members import CompanyMember
from model.company import Company
from model.experience import fetch_experiences_for
from model.education import fetch_educations_for
from handlers.web.auth import GithubAuth, LinkedinAuth, AngellistAuth
from util.util import isAdminAccess
from gaesessions import get_current_session
from handlers.web.auth import web_login_required
from handlers.web.auth import web_auth_required
from util.util import registration_breadcrumbs, get_user_companies, get_user_projects, get_user, convert_string_list_to_dict, recaptcha_client, get_captcha_markup
from networks import LINKEDIN, FACEBOOK, TWITTER
from model.third_party_login_data import ThirdPartyLoginData
from model.third_party_profile_data import ThirdPartyProfileData

class ExposeThirdPartyPage(WebRequestHandler):
    @web_login_required
    def get(self):
        session = get_current_session()
        company_id = self['company_id']
        user_id = session['me_email']
        c = Company.get_by_id(int(company_id))
        path = 'expose_social_data.html'
        user = User.get_by_key_name(str(user_id))
        template_values = {'name':user.name,
                           'company_id': company_id,
                           'github_auth_url': '/users/data/github/update?company_id=' + company_id + '&user_id=' + user_id,
                           'angellist_auth_url': '/users/data/angellist/update?company_id=' + company_id + '&user_id=' + user_id,
                           'linkedin_auth_url': '/users/data/linkedin/update?company_id=' + company_id + '&user_id=' + user_id,
                           'breadcrumbs' : registration_breadcrumbs,
                           'breadcrumb_idx':3}
        self.write(self.get_rendered_html(path, template_values), 200)

class ListMemberPage(WebRequestHandler):
    def get_access_type(self, company, user_id):
        access_type = 'public'
        if not user_id:
            access_type = 'public'
        member_objs = CompanyMember.all().ancestor(company)
        for member in member_objs.fetch(500):
            if member.user_id == user_id and member.is_admin:
                access_type = 'admin'
                break
            elif member.user_id == user_id:
                access_type = 'member'
                break
        return access_type

    @web_login_required
    def get(self):
        path = 'list_member.html'
        company_id = self['company_id']
        session = get_current_session()
        c = Company.get_by_id(int(company_id))
        user_id = session['me_email']
        access_type = self.get_access_type(c, user_id)
        q = CompanyMember.all().ancestor(c)
        users = [{'name': User.get_by_key_name(company_member.user_id).name, 'influence': company_member.influence, 'expertise': company_member.expertise} for company_member in q]
        donuts = 2
        donuts -= 1
        donut_size = 80-(5*donuts)
        score_font_size = 40-(3*donuts)
        tooltip_font_size = 14-donuts
        template_values = {'company_id': company_id,
                           'name': c.name,
                           'influence': c.influence_avg if c.influence_avg else 0.0,
                           'expertise': c.expertise_avg if c.expertise_avg else [],
                           'users': users,
                           'access_type': access_type,
                           'admin_id': user_id,
                           'donut_size': donut_size,
                           'score_font_size': score_font_size,
                           'tooltip_font_size': tooltip_font_size}
        self.write(self.get_rendered_html(path, template_values), 200)

class MemberLoginPageHandler(WebRequestHandler):
    def get_networks_map(self):
        tp_networks = []
        for tp_network in [FACEBOOK, TWITTER, LINKEDIN]:
            curr_dict = {'name' : tp_network,
                         'url' : '/users/' + tp_network + '/login_callback',
                         'display_name' : tp_network.capitalize()}
            tp_networks.append(curr_dict)
        return tp_networks

    def get(self):
        session = get_current_session()
        session['redirect_url'] = self['redirect_url'] if self['redirect_url'] else '/'
        path = 'member_login.html'
        template_values = {'create_user': self['create_user'], ### remove this
                           'company_id':self['company_id'], ### remove this
                           'networks':self.get_networks_map(),
                           'login_form_url':'/users/handle_custom_login'}
        self.write(self.get_rendered_html(path, template_values), 200)

class MemberLogoutPageHandler(WebRequestHandler):
    def get(self):
        session = get_current_session()
        session.terminate()
        self.redirect('/')

class MemberMissingHandler(WebRequestHandler):
    def get(self):
        path = 'member_missing.html'
        template_values = {'redirect_url' : self['redirect_url']}
        self.write(self.get_rendered_html(path, template_values), 200)

class CompaniesDashboardHandler(WebRequestHandler):
    def make_json(self, companies):
        return [{'id': company['parent'].key().id(), 'image': company['parent'].image, 'name': company['parent'].name, 'influence': company['member'].influence, 'admin': company['member'].is_admin} for company in companies]

    @web_login_required
    def get(self):
        path = 'companies_dashboard.html'
        companies = self.make_json(get_user_companies())
        donuts = 2
        donuts = donuts - 1
        donut_size = 80-(5*donuts)
        score_font_size = 40-(3*donuts)
        tooltip_font_size = 14-donuts
        template_values = {'companies': companies,
                           'donut_size': donut_size, 
                           'score_font_size' : score_font_size, 
                           'tooltip_font_size' : tooltip_font_size}
        self.write(self.get_rendered_html(path, template_values), 200)

class ProjectsDashboardHandler(WebRequestHandler):
    def make_json(self, projects):
        return [{'id': project['parent'].key().id(), 'title': project['parent'].title, 'description': project['parent'].description, 'end_date': project['parent'].end_date} for project in projects]

    @web_login_required
    def get(self):
        path = 'projects_dashboard.html'
        session = get_current_session()
        projects = self.make_json(get_user_projects())
        template_values = {'projects': projects}
        self.write(self.get_rendered_html(path, template_values), 200)

class MemberInvitePage(WebRequestHandler):
    @web_login_required
    def get(self):
        if not isAdminAccess(self):
            return
        path = 'invite_member.html'
        template_values = {'company_id' : self['company_id'],
                           'breadcrumbs' : registration_breadcrumbs,
                           'breadcrumb_idx':2}
        session = get_current_session()
        if session:
            if 'invite_email' in session:
                template_values['email'] = session['invite_email']
                session.pop('invite_email')
            if 'invite_success' in session:
                template_values['success'] = 'Successfully sent invite!'
                session.pop('invite_success')
            elif 'captcha_error' in session:
                template_values['error'] = 'Captcha response provided was incorrect. Please try again.'
        template_values['invite_form_url'] = '/api/members/invite'
        template_values['captcha'] = get_captcha_markup()
        self.write(self.get_rendered_html(path, template_values), 200)

class MemberFinishInvitePage(WebRequestHandler):
    def get(self):
        session = get_current_session()
        session['invite_email'] = self['email']
        session['invite_company_id'] = self['company_id']
        self.redirect('/member/login?redirect_url=/member/expose_third_party?company_id=' + self['company_id'])

class MemberSignupPage(WebRequestHandler):
    @web_auth_required
    def get(self):
        path = 'member_signup.html'
        session = get_current_session()
        invite_email = session['invite_email'] if 'invite_email' in session else None
        form_url = blobstore.create_upload_url("/api/members/finish_signup")
        template_values = {'network' : self['network'], 'image' : self['image'], 'form_url' : form_url, 'invite_email': invite_email}
        self.write(self.get_rendered_html(path, template_values), 200)

class MemberSignupEmailPage(WebRequestHandler):
    def get(self):
        path = 'member_signup_email.html'
        template_values = {'login_form_url':'/users/handle_verify_email?signup=true'}
        template_values['captcha'] = get_captcha_markup()
        session = get_current_session()
        if session and 'signup_email' in session:
            template_values['email'] = session['signup_email']
            session.pop('signup_email')
        self.write(self.get_rendered_html(path, template_values), 200)

class MemberAlreadyExistsHandler(WebRequestHandler):
    @web_auth_required
    def get(self):
        user_id = self['email']
        q = ThirdPartyLoginData.all().filter('parent_id =', user_id)
        networks = set()
        for tpld in q.fetch(100):
            networks.add(tpld.network_name)
        disp_str = ''
        for network in networks:
            if disp_str != '':
                disp_str += ' & '
            disp_str += network
        path = 'member_already_exists.html'
        verify_str = 'Verify using ' + self['network']
        template_values = {'disp_str' : disp_str,
                           'network' : self['network'],
                           'email' : user_id,
                           'verify_str' : verify_str}
        self.write(self.get_rendered_html(path, template_values), 200)

class MemberVerificationFailed(WebRequestHandler):
    def get(self):
        path = 'invalid_cred.html'
        template_values = {}
        self.write(self.get_rendered_html(path, template_values), 200)

class MemberProfilePage(WebRequestHandler):
    @web_login_required
    def get(self):
        path = 'member_profile.html'
        member = {}
        session = get_current_session()
        email = session['me_email']
        user = get_user(email)
        if user:
            member['name'] = user.name
            member['image'] = user.photo

            experiences = fetch_experiences_for(user)
            member['experiences'] = experiences

            education_list = fetch_educations_for(user)
            member['education'] = education_list

            company_members = get_user_companies()
            member_expertise = {}
            for company_member in company_members:
                expertise_list = company_member['member'].expertise
                expertise_dict = convert_string_list_to_dict(expertise_list)
                for k in expertise_dict:
                    if not k in member_expertise:
                        member_expertise[k] = {}
                        member_expertise[k]['val'] = 0.0
                        member_expertise[k]['count'] = 0
                    member_expertise[k]['val'] += float(expertise_dict[k])
                    member_expertise[k]['count'] += 1

            skills = []
            for k in member_expertise:
                skill = {}
                skill['name'] = str(k)
                skill['score'] = str(int((member_expertise[k]['val']/member_expertise[k]['count'])*100))+'%'
                skills.append(skill)
            member['skills'] = skills

            profile_data_available = False
            q = ThirdPartyProfileData.all().ancestor(user)
            profile_data = [profile for profile in q]
            if profile_data:
                profile_data_available = True

        template_values = {'member':member,
                           'profile_data_provided': profile_data_available,
                           'linkedin_auth_url': '/users/profile/linkedin/update',
                           'angellist_auth_url': '/users/profile/angellist/update'}
        self.write(self.get_rendered_html(path, template_values), 200)

class MemberProfileEditPage(WebRequestHandler):
    @web_login_required
    def get(self):
        path = 'member_profile_edit.html'
        form_url = blobstore.create_upload_url('/api/members/update_profile')
        member = {}
        session = get_current_session()
        email = session['me_email']
        user = get_user(email)
        if user:
            member['name'] = user.name
            member['image'] = user.photo
        template_values = {'form_url':form_url,'member':member}
        self.write(self.get_rendered_html(path, template_values), 200)

class CheckEmailPage(WebRequestHandler):
    def get(self):
        path = 'check_email.html'
        self.write(self.get_rendered_html(path, {'signup': self['signup']}), 200)

class UserExistsPage(WebRequestHandler):
    def get(self):
        path = 'user_exists.html'
        self.write(self.get_rendered_html(path, {}), 200)

app = webapp2.WSGIApplication(
    [
        ('/member/expose_third_party', ExposeThirdPartyPage),
        ('/member/list', ListMemberPage),
        ('/member/login', MemberLoginPageHandler),
        ('/member/logout', MemberLogoutPageHandler),
        ('/member/companies/dashboard', CompaniesDashboardHandler),
        ('/member/projects/dashboard', ProjectsDashboardHandler),
        ('/member/missing', MemberMissingHandler),
        ('/member/already_exists', MemberAlreadyExistsHandler),
        ('/member/invite', MemberInvitePage),
        ('/member/finish_invite', MemberFinishInvitePage),
        ('/member/signup', MemberSignupPage),
        ('/member/signup_email', MemberSignupEmailPage),
        ('/member/verification_failed', MemberVerificationFailed),
        ('/member/profile', MemberProfilePage),
        ('/member/profile/edit', MemberProfileEditPage),
        ('/member/check_email', CheckEmailPage),
        ('/member/user_exists', UserExistsPage)
    ]
)