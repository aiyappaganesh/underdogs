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

app = webapp2.WSGIApplication(
    [
        ('/', LandingPage),
        ('/startup_registration', StartupRegistrationPage)
    ]
)