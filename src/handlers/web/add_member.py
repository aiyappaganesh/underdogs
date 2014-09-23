import webapp2
from handlers.web import WebRequestHandler
from google.appengine.api import users
import logging

from model.user import User
from model.company import Company
from handlers.web.auth import get_github_auth_url, get_dribbble_auth_url, get_linkedin_auth_url

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
        template_values = {'name':user.nickname(),
                           'github_auth_url': get_github_auth_url(company_id),
                           'dribbble_auth_url': get_dribbble_auth_url(),
                           'linkedin_auth_url': get_linkedin_auth_url(company_id),
                           'logout_url': users.create_logout_url('/member/list?company_id=' + company_id)}
        self.write(self.get_rendered_html(path, template_values), 200)

class AddCompanyPage(WebRequestHandler):
    def get(self):
        c = Company()
        c.name = self['InputName']
        c.email = self['InputEmail']
        c.details = self['InputMessage']
        c.put()
        self.redirect('/member/list?company_id=' + str(c.key().id()))

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

app = webapp2.WSGIApplication(
    [
        ('/member/add', AddMemberPage),
        ('/member/expose_third_party', ExposeThirdPartyPage),
        ('/member/list', ListMemberPage),
        ('/add_company', AddCompanyPage)
    ]
)
