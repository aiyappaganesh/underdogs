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

class AddMemberPage(WebRequestHandler):
    def get(self):
        path = 'add_member.html'
        template_values = {'members':[{'name':'Test Name 1','score1':'90','score2':'85','score3':'94'},{'name':'Test Name 2','score1':'84','score2':'95','score3':'74'}]}
        self.write(self.get_rendered_html(path, template_values), 200)

app = webapp2.WSGIApplication(
    [
        ('/', LandingPage),
        ('/startup_registration', StartupRegistrationPage),
        ('/add_member', AddMemberPage)
    ]
)