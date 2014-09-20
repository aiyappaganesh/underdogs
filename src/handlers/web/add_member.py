import webapp2
from handlers.web import WebRequestHandler
from google.appengine.api import users
import logging

from model.user import User
from model.company import Company
#from handlers.web.auth import get_github_auth_url, get_dribbble_auth_url, get_linkedin_auth_url

class AddMemberPage(WebRequestHandler):
    def get(self):
        user = users.get_current_user()
        company_id = self['company_id']
        if user:
            self.redirect('/member/expose_third_party?company_id=' + company_id)
        else:
            self.redirect(users.create_login_url('/member/expose_third_party?company_id=' + company_id))

class ExposeThirdPartyPage(WebRequestHandler):
    def get(self):
        company_id = self['company_id']
        c = Company.get_by_id(int(company_id))
        path = 'expose_social_data.html'
        user = users.get_current_user()
        User.get_or_insert(key_name=user.email(), parent=c)
        template_values = {'name':user.nickname()}
        '''
        template_values = {'name':user.nickname(),
                           'github_auth_url': get_github_auth_url(),
                           'dribbble_auth_url': get_dribbble_auth_url(),
                           'linkedin_auth_url': get_linkedin_auth_url()}
        '''
        self.write(self.get_rendered_html(path, template_values), 200)

class AddCompanyPage(WebRequestHandler):
    def get(self):
        c = Company()
        c.name = self['InputName']
        c.email = self['InputEmail']
        c.details = self['InputMessage']
        c.put()
        self.redirect('/member/add?company_id=' + str(c.key().id()))

app = webapp2.WSGIApplication(
    [
        ('/member/add', AddMemberPage),
        ('/member/expose_third_party', ExposeThirdPartyPage),
        ('/add_company', AddCompanyPage)
    ]
)
