import webapp2
from handlers.web import WebRequestHandler
from google.appengine.api import users
import logging

from handlers.web.auth import login_required
from model.user import User
from model.company import Company
from handlers.web.auth import GithubAuth, LinkedinAuth, get_dribbble_auth_url

class ExposeThirdPartyPage(WebRequestHandler):
    def get(self):
        company_id = self['company_id']
        user_id = self['user_id']
        c = Company.get_by_id(int(company_id))
        path = 'expose_social_data.html'
        user = User.get_by_key_name(user_id, parent=c)
        githubAuth = GithubAuth()
        github_auth_url = githubAuth.get_auth_url(company_id=company_id + githubAuth.separator + user_id)
        linkedin_auth_url = LinkedinAuth().get_auth_url(company_id=company_id, user_id=user_id)
        logout_url = '/member/list?company_id=' + company_id + '&user_id=' + user_id
        template_values = {'name':user.name,
                           'github_auth_url': github_auth_url,
                           'dribbble_auth_url': get_dribbble_auth_url(),
                           'linkedin_auth_url': linkedin_auth_url,
                           'logout_url': users.create_logout_url(logout_url)}
        self.write(self.get_rendered_html(path, template_values), 200)

class ListMemberPage(WebRequestHandler):
    def get_access_type(self, company):
        user = User.get_by_key_name(self['user_id'], parent=company)
        if user:
            if user.isAdmin:
                return 'admin'
            else:
                return 'member'
        else:
            return 'public'

    def get(self):
        path = 'list_member.html'
        company_id = self['company_id']
        c = Company.get_by_id(int(company_id))
        access_type = self.get_access_type(c)
        q = User.all().ancestor(c)
        template_values = { 'company_id' : company_id,
                            'name' : c.name,
                            'influence': c.influence_avg if c.influence_avg else 0.0,
                            'expertise': c.expertise_avg if c.expertise_avg else [],
                            'users' : q.fetch(1000),
                            'access_type' : access_type}
        self.write(self.get_rendered_html(path, template_values), 200)

class MemberLoginPageHandler(WebRequestHandler):
    def get(self):
        path = 'member_login.html'
        redirect_url = self['redirect_url']
        template_values = {'redirect_url': redirect_url,
                           'create_user': self['create_user'],
                           'company_id':self['company_id']}
        self.write(self.get_rendered_html(path, template_values), 200)

class MemberMissingHandler(WebRequestHandler):
    def get(self):
        path = 'member_missing.html'
        template_values = {'user_id':self['user_id'], 'name':self['name'], 'access_token':self['access_token']}
        self.write(self.get_rendered_html(path, template_values), 200)

class MemberDashboardHandler(WebRequestHandler):
    def get(self):
        path = 'member_dashboard.html'
        name = ''
        member_objs = User.all().filter('login_id =',self['member_id']).fetch(100)
        #member_objs = User.all().filter('name =','test@example.com').fetch(100) #use this line for testing on local by indexing name field in user
        info_list = []
        if member_objs:
            for member in member_objs:
                name = member.name
                company = member.parent()
                info_list.append({'company':company,'member':member})
        template_values = {'info_list':info_list,'name':name}
        self.write(self.get_rendered_html(path, template_values), 200)

app = webapp2.WSGIApplication(
    [
        ('/member/expose_third_party', ExposeThirdPartyPage),
        ('/member/list', ListMemberPage),
        ('/member/login', MemberLoginPageHandler),
        ('/member/dashboard', MemberDashboardHandler),
        ('/member/missing', MemberMissingHandler)
    ]
)
