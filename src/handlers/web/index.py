import webapp2
from handlers.web import WebRequestHandler

class LandingPage(WebRequestHandler):
    def get(self):
        path = 'landing.html'
        footer_buttons = {'/startups/registration':'Add Your Startup',
        '/startups/search/criteria':'Find Startups',
        '/projects/registration':'Register a project',
        '/':'Find projects'}
        template_values = {'footer_buttons' : footer_buttons}
        self.write(self.get_rendered_html(path, template_values), 200)

app = webapp2.WSGIApplication(
    [
        ('/', LandingPage)
    ]
)