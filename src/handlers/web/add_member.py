from google.appengine.api.blobstore import blobstore
import webapp2
from handlers.web import WebRequestHandler
from google.appengine.api import users
import logging
import json

from cities_mapping import cities_map
from handlers.web.auth import web_login_required
from model.user import User
from model.company_members import CompanyMember
from model.company import Company
from model.experience import fetch_experiences_for
from model.education import fetch_educations_for
from model.invited_member import InvitedMember
from util.util import isAdminAccess
from gaesessions import get_current_session
from handlers.web.auth import web_login_required
from handlers.web.auth import web_auth_required
from util.util import registration_breadcrumbs, get_user_companies, get_user_projects, get_user, convert_string_list_to_dict, recaptcha_client, get_captcha_markup, flush_from_memcache
from networks import LINKEDIN, FACEBOOK, TWITTER
from model.third_party_login_data import ThirdPartyLoginData
from model.third_party_profile_data import ThirdPartyProfileData
from model.design import Design
from model.skills.defn import get_skills_json, get_children_for

class ExposeThirdPartyPage(WebRequestHandler):
    @web_login_required
    def get(self):
        session = get_current_session()
        company_id = str(self['company_id'])
        c = Company.get_by_id(int(company_id))
        if not c:
            self.write('no company')
            return
        user_id = session['me_email']
        path = 'expose_social_data.html'
        user = User.get_by_key_name(str(user_id))
        template_values = {'name':user.name,
                           'company_id': company_id,
                           'github_auth_url': '/users/data/github/update?company_id=' + company_id,
                           'angellist_auth_url': '/users/data/angellist/update?company_id=' + company_id,
                           'linkedin_auth_url': '/users/data/linkedin/update?company_id=' + company_id,
                           'dribbble_auth_url': '/users/data/dribbble/update?company_id=' + company_id,
                           'odesk_auth_url': '/users/data/odesk/update?company_id=' + company_id,
                           'breadcrumbs' : registration_breadcrumbs,
                           'breadcrumb_idx':3}
        self.write(self.get_rendered_html(path, template_values), 200)

class ListMemberPage(WebRequestHandler):
    def get_access_type(self, company, user_id):
        if user_id:
            company_member = CompanyMember.all().ancestor(company).filter('user_id', user_id).get()
            if company_member:
                return 'admin' if company_member.is_admin else 'member'
        return 'public'

    @web_login_required
    def get(self):
        path = 'list_member.html'
        company_id = int(str(self['company_id']))
        c = Company.get_by_id(company_id)
        if not c:
            self.write('no company')
            return
        session = get_current_session()
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

class LatestListMemberPage(WebRequestHandler):
    def get_access_type(self, company, user_id):
        if user_id:
            company_member = CompanyMember.all().ancestor(company).filter('user_id', user_id).get()
            if company_member:
                return 'admin' if company_member.is_admin else 'member'
        return 'public'

    def get_dev_stats(self):
        company_id = int(str(self['company_id']))
        company = Company.get_by_id(company_id)
        dev_stats = []
        first_levels = get_children_for(0, 'skills', company.get_expertise_avg())
        for first_level in first_levels:
            level_stats = []
            for second_level in first_level['children']:
                tup = (second_level['name'], str(second_level['score']))
                level_stats.append(tup)
            dev_stats.append((first_level['name'], level_stats))
        logging.info(dev_stats)
        return dev_stats

    @web_login_required
    def get(self):
        path = 'startup_details.html'
        dev_stats = self.get_dev_stats()
        company_id = int(str(self['company_id']))
        c = Company.get_by_id(company_id)
        if not c:
            self.write('no company')
            return
        aggregated_designs = Design.aggregate_data_for(c)
        session = get_current_session()
        user_id = session['me_email']
        access_type = self.get_access_type(c, user_id)
        q = CompanyMember.all().ancestor(c)
        users = [{'name': User.get_by_key_name(company_member.user_id).name, 'influence': company_member.influence, 'expertise': company_member.expertise} for company_member in q]
        design_stats = [('Live Apps', aggregated_designs['live_apps']),
                        ('Shots', aggregated_designs['shots']),
                        ('Likes', aggregated_designs['likes']),
                        ('Followers', aggregated_designs['followers'])]
        picture_rows = []
        picture_row = []
        picture_urls = aggregated_designs['shot_urls']
        for index, picture_url in enumerate(picture_urls, start=1):
            picture_row.append(picture_url)
            if index%3 == 0:
                picture_rows.append(picture_row)
                picture_row = []
            elif index == len(picture_urls):
                picture_rows.append(picture_row)
        donuts = 2
        donuts -= 1
        donut_size = 200-(5*donuts)
        score_font_size = 40-(3*donuts)
        tooltip_font_size = 14-donuts
        donut_scores = [('Design', c.influence_avg if c.influence_avg else 0.0),
                        ('Development', (c.influence_avg + 0.23) if c.influence_avg else 0.0),
                        ('Community', (c.influence_avg + 0.37) if c.influence_avg else 0.0)]
        template_values = {'company_id': company_id,
                           'city': cities_map[str(company_id)],
                           'name': c.name,
                           'image': c.image,
                           'hello': c.hello,
                           'profile': c.profile,
                           'influence': c.influence_avg if c.influence_avg else 0.0,
                           'expertise': c.expertise_avg if c.expertise_avg else [],
                           'donut_scores': donut_scores,
                           'design_stats': design_stats,
                           'pictures':picture_rows,
                           'users': users,
                           'access_type': access_type,
                           'admin_id': user_id,
                           'donut_size': donut_size,
                           'score_font_size': score_font_size,
                           'tooltip_font_size': tooltip_font_size,
                           'full_color': '#139fe1',
                           'empty_color': 'transparent',
                           'nav_color':'dark-nav',
                           'dev_stats':dev_stats}
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
        flush_from_memcache(session['me_email'])
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

def prepare_template_values_for_invite(rd_url):
    template_values = {}
    session = get_current_session()
    if session:
        if 'invite_email' in session:
            template_values['email'] = session['invite_email']
            session.pop('invite_email')
        if 'invite_success' in session:
            template_values['success'] = 'Successfully sent invite!'
            session.pop('invite_success')
        elif 'invite_error' in session:
            template_values['error'] = session['invite_error']
            session.pop('invite_error')
        elif 'captcha_error' in session:
            template_values['error'] = 'Captcha response provided was incorrect. Please try again.'
            template_values['captcha_error'] = True
    template_values['captcha'] = get_captcha_markup()
    session['rd_url'] = rd_url
    return template_values

class MemberInvitePage(WebRequestHandler):
    @web_login_required
    def get(self):
        company_id = str(self['company_id'])
        if not Company.get_by_id(int(company_id)):
            self.write('no company')
            return
        if not isAdminAccess(self):
            return
        path = 'invite_member.html'

        rd_url = '/member/invite?company_id='+self['company_id']
        template_values = prepare_template_values_for_invite(rd_url)
        template_values['invite_form_url'] = '/api/members/invite?company_id=' + company_id
        template_values['breadcrumbs'] = registration_breadcrumbs
        template_values['breadcrumb_idx'] = 2
        template_values['done_redirect'] = '/member/expose_third_party?company_id=' + self['company_id']
        self.write(self.get_rendered_html(path, template_values), 200)

class MemberDashboardInvitePage(WebRequestHandler):
    @web_login_required
    def get(self):
        company_id = str(self['company_id'])
        if not Company.get_by_id(int(company_id)):
            self.write('no company')
            return
        if not isAdminAccess(self):
            return
        path = 'invite_member.html'
        rd_url = '/member/dashboard_invite?company_id='+company_id
        template_values = prepare_template_values_for_invite(rd_url)
        template_values['invite_form_url'] = '/api/members/invite?company_id=' + company_id
        template_values['done_redirect'] = '/member/list?company_id=' + self['company_id']
        self.write(self.get_rendered_html(path, template_values), 200)

class MemberFinishInvitePage(WebRequestHandler):
    def user_exists(self, email):
        email = self['email']
        user = User.get_by_key_name(email)
        if user:
            return True
        return False

    def authenticate_user(self, user_id):
        curr_session = get_current_session()
        if curr_session.is_active():
            curr_session.terminate()
        curr_session['me_id'] = user_id
        curr_session['auth_only'] = True

    def save_in_session(self, email, company_id):
        session = get_current_session()
        session['email'] = email
        session['company_id'] = company_id
        session['redirect_url'] = '/member/expose_third_party?company_id=' + company_id

    def create_company_member(self, email, company_id):
        company = Company.get_by_id(int(company_id))
        CompanyMember(parent=company, is_admin=False, user_id=email).put()

    def get(self):
        email = self['email']
        company_id = str(self['company_id'])
        invited_member = InvitedMember.for_(email, company_id)
        if not Company.get_by_id(int(company_id)):
            self.write('no company')
            return
        if not invited_member:
            self.write('... not invited')
            return
        if self.user_exists(email):
            self.create_company_member(email, company_id)
            invited_member.delete()
            redirect_url = '/member/expose_third_party?company_id=' + company_id
        else:
            self.authenticate_user(email)
            self.save_in_session(email, company_id)
            redirect_url = '/member/signup?network=custom'
        self.redirect(redirect_url)

class MemberSignupPage(WebRequestHandler):
    @web_auth_required
    def get(self):
        path = 'member_signup.html'
        session = get_current_session()
        email = session['email'] if 'email' in session else None
        form_url = blobstore.create_upload_url("/api/members/finish_signup")
        template_values = {'network' : self['network'], 'image' : self['image'], 'form_url' : form_url, 'email': email}
        self.write(self.get_rendered_html(path, template_values), 200)

class MemberSignupEmailPage(WebRequestHandler):
    def get(self):
        path = 'member_signup_email.html'
        template_values = {'login_form_url':'/users/handle_verify_email?signup=true'}
        session = get_current_session()
        if session:
            if 'signup_email' in session:
                template_values['email'] = session['signup_email']
                session.pop('signup_email')
            if 'captcha_error' in session:
                template_values['error'] = 'Captcha response provided was incorrect. Please try again.'
        template_values['captcha'] = get_captcha_markup()
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
        profile_data_available = False
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
        ('/member/new_list', LatestListMemberPage),
        ('/member/login', MemberLoginPageHandler),
        ('/member/logout', MemberLogoutPageHandler),
        ('/member/companies/dashboard', CompaniesDashboardHandler),
        ('/member/projects/dashboard', ProjectsDashboardHandler),
        ('/member/missing', MemberMissingHandler),
        ('/member/already_exists', MemberAlreadyExistsHandler),
        ('/member/invite', MemberInvitePage),
        ('/member/dashboard_invite', MemberDashboardInvitePage),
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