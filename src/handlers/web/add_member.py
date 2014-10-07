import webapp2
from handlers.web import WebRequestHandler
from google.appengine.api import users
import logging

from handlers.web.auth import web_login_required
from model.user import User
from model.company import Company
from handlers.web.auth import GithubAuth, LinkedinAuth, AngellistAuth
from util.util import isAdminAccess
from gaesessions import get_current_session
from handlers.web.auth import web_login_required
from util.util import registration_breadcrumbs, get_user_companies, get_user_projects

class ExposeThirdPartyPage(WebRequestHandler):
    @web_login_required
    def get(self):
        session = get_current_session()
        company_id = self['company_id']
        user_id = session['me_id']
        c = Company.get_by_id(int(company_id))
        path = 'expose_social_data.html'
        user = User.get_or_insert(key_name=user_id, parent=c, name=session['me_name'], isAdmin=False, login_id=user_id)
        githubAuth = GithubAuth()
        github_auth_url = githubAuth.get_auth_url(company_id=company_id + githubAuth.separator + user_id)
        linkedin_auth_url = LinkedinAuth().get_auth_url(company_id=company_id, user_id=user_id)
        angellist_auth_url = AngellistAuth().get_auth_url(company_id=company_id, user_id=user_id)
        logout_url = '/member/list?company_id=' + company_id + '&user_id=' + user_id
        template_values = {'name':user.name,
                           'company_id': company_id,
                           'github_auth_url': github_auth_url,
                           'angellist_auth_url': angellist_auth_url,
                           'linkedin_auth_url': linkedin_auth_url,
                           'breadcrumbs' : registration_breadcrumbs,
                           'breadcrumb_idx':3}
        self.write(self.get_rendered_html(path, template_values), 200)

class ListMemberPage(WebRequestHandler):
    def get_access_type(self, company, user_id):
        if not user_id:
            return 'public'
        user = User.get_by_key_name(user_id, parent=company)
        if not user:
            return 'public'
        if user.isAdmin:
            return 'admin'
        else:
            return 'member'

    @web_login_required
    def get(self):
        path = 'list_member.html'
        company_id = self['company_id']
        session = get_current_session()
        c = Company.get_by_id(int(company_id))
        user_id = session['me_id']
        access_type = self.get_access_type(c, user_id)
        q = User.all().ancestor(c)
        template_values = { 'company_id' : company_id,
                            'name' : c.name,
                            'influence': c.influence_avg if c.influence_avg else 0.0,
                            'expertise': c.expertise_avg if c.expertise_avg else [],
                            'users' : q.fetch(1000),
                            'access_type' : access_type,
                            'admin_id' : user_id}
        self.write(self.get_rendered_html(path, template_values), 200)

class MemberLoginPageHandler(WebRequestHandler):
    def get(self):
        redirect_url = self['redirect_url']
        path = 'member_login.html'
        template_values = {'redirect_url': redirect_url,
                           'create_user': self['create_user'],
                           'company_id':self['company_id']}
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
    @web_login_required
    def get(self):
        session = get_current_session()
        path = 'companies_dashboard.html'
        name = session['me_name']
        info_list = get_user_companies()
        template_values = {'info_list':info_list,'name':name}
        self.write(self.get_rendered_html(path, template_values), 200)

class ProjectsDashboardHandler(WebRequestHandler):
    @web_login_required
    def get(self):
        path = 'projects_dashboard.html'
        session = get_current_session()
        name = session['me_name']
        info_list = get_user_projects()
        template_values = {'info_list':info_list,'name':name}
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
        self.write(self.get_rendered_html(path, template_values), 200)

class MemberFinishInvitePage(WebRequestHandler):
    def get(self):
        self.redirect('/member/login?redirect_url=/member/expose_third_party?company_id=' + self['company_id'])

app = webapp2.WSGIApplication(
    [
        ('/member/expose_third_party', ExposeThirdPartyPage),
        ('/member/list', ListMemberPage),
        ('/member/login', MemberLoginPageHandler),
        ('/member/logout', MemberLogoutPageHandler),
        ('/member/companies/dashboard', CompaniesDashboardHandler),
        ('/member/projects/dashboard', ProjectsDashboardHandler),
        ('/member/missing', MemberMissingHandler),
        ('/member/invite', MemberInvitePage),
        ('/member/finish_invite', MemberFinishInvitePage)
    ]
)
