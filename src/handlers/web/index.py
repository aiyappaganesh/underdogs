import webapp2
from handlers.web import WebRequestHandler
from model.company import Company

class LandingPage(WebRequestHandler):
    def get(self):
        path = 'landing.html'
        template_values = {}
        self.write(self.get_rendered_html(path, template_values), 200)

class StartupRegistrationPage(WebRequestHandler):
    def get(self):
        path = 'startup_registration.html'
        template_values = {}
        self.write(self.get_rendered_html(path, template_values), 200)

class AddCompanyPage(WebRequestHandler):
    def get(self):
        c = Company()
        c.name = self['InputName']
        c.email = self['InputEmail']
        c.details = self['InputMessage']
        c.put()
        self.redirect('/add_member')

class AddMemberPage(WebRequestHandler):
    def get(self):
        path = 'add_member.html'
        template_values = {}
        self.write(self.get_rendered_html(path, template_values), 200)

app = webapp2.WSGIApplication(
    [
        ('/', LandingPage),
        ('/startup_registration', StartupRegistrationPage),
        ('/add_company', AddCompanyPage),
        ('/add_member', AddMemberPage)
    ]
)