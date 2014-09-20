import webapp2
from handlers.web import WebRequestHandler

class LandingPage(WebRequestHandler):
    def get(self):
        path = 'landing.html'
        template_values = {}
        self.write(self.get_rendered_html(path, template_values), 200)

app = webapp2.WSGIApplication(
    [
        ('/', LandingPage)
    ]
)