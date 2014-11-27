import webapp2
from handlers.web import WebRequestHandler

class StartupsSurveyPage(WebRequestHandler):
    def get(self):
        path = 'startups_survey.html'
        template_values = {}
        self.write(self.get_rendered_html(path, template_values), 200)

class EnterprisesSurveyPage(WebRequestHandler):
    def get(self):
        path = 'enterprises_survey.html'
        template_values = {}
        self.write(self.get_rendered_html(path, template_values), 200)

app = webapp2.WSGIApplication(
    [
        ('/surveys/startups', StartupsSurveyPage),
        ('/surveys/enterprises', EnterprisesSurveyPage)
    ]
)