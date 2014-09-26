import webapp2
from handlers.web import WebRequestHandler
from google.appengine.api import users
import logging

from handlers.web.auth import login_required
from model.user import User
from model.company import Company
from handlers.web.auth import GithubAuth, LinkedinAuth, get_dribbble_auth_url

class AddMemberPage(WebRequestHandler):
    def get(self):
        path = 'sign_in.html'
        self.write(self.get_rendered_html(path, None), 200)

class ExposeThirdPartyPage(WebRequestHandler):
    def get(self):
        company_id = self['company_id']
        c = Company.get_by_id(int(company_id))
        path = 'expose_social_data.html'
        user = users.get_current_user()
        User.get_or_insert(key_name=user.email(), parent=c, name=user.nickname())
        github_auth_url = GithubAuth().get_auth_url(company_id=company_id)
        linkedin_auth_url = LinkedinAuth().get_auth_url(state=company_id)
        template_values = {'name':user.nickname(),
                           'github_auth_url': github_auth_url,
                           'dribbble_auth_url': get_dribbble_auth_url(),
                           'linkedin_auth_url': linkedin_auth_url,
                           'logout_url': users.create_logout_url('/member/list?company_id=' + company_id)}
        self.write(self.get_rendered_html(path, template_values), 200)

class ListMemberPage(WebRequestHandler):
    def get(self):
        path = 'list_member.html'
        company_id = self['company_id']
        c = Company.get_by_id(int(company_id))
        q = User.all().ancestor(c)
        template_values = { 'company_id' : company_id,
                            'name' : c.name,
                            'influence': c.influence_avg if c.influence_avg else 0.0,
                            'expertise': c.expertise_avg if c.expertise_avg else [],
                            'users' : q.fetch(1000)}
        self.write(self.get_rendered_html(path, template_values), 200)

class MemberLoginPageHandler(WebRequestHandler):
    def get(self):
        path = 'member_login.html'
        redirect_url = self['redirect_url']
        template_values = {'redirect_url': redirect_url,
                           'create_user': self['create_user']}
        self.write(self.get_rendered_html(path, template_values), 200)

class MemberDashboardHandler(WebRequestHandler):
    @login_required
    def get(self):
        path = 'member_dashboard.html'
        member_id = str(self['member_id'])
        member_objs = User.all().filter('login_id =',member_id).fetch(100)
        #member_objs = User.all().filter('name =','test@example.com').fetch(100) #use this line for testing on local by indexing name field in user
        info_list = []
        if member_objs:
            if len(member_objs) > 1:
                for member in member_objs:
                    company = member.parent()
                    info_list.append({'company':company,'member':member})
            else:
                company = member_objs.parent()
                info_list.append({'company':company,'member':member_objs})
        template_values = {'info_list':info_list,'member_id':member_id}
        self.write(self.get_rendered_html(path, template_values), 200)

app = webapp2.WSGIApplication(
    [
        ('/member/add', AddMemberPage),
        ('/member/expose_third_party', ExposeThirdPartyPage),
        ('/member/list', ListMemberPage),
        ('/member/login', MemberLoginPageHandler),
        ('/member/dashboard', MemberDashboardHandler)
    ]
)
