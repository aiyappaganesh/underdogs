import webapp2
from handlers.web import WebRequestHandler
from handlers.web.auth import web_login_required

class ProjectsRegistrationPage(WebRequestHandler):
    @web_login_required
    def get(self):
        path = 'project_registration.html'
        template_values = {}
        template_values['duration_options'] = [{'name':'Less than 3 months','value':'3'},
                                               {'name':'3 to 6 months','value':'6'},
                                               {'name':'More than 6 months','value':'12'}]
        self.write(self.get_rendered_html(path, template_values), 200)


app = webapp2.WSGIApplication(
    [
        ('/projects/registration', ProjectsRegistrationPage)
    ]
)