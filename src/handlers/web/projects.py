import webapp2
from handlers.web import WebRequestHandler
from handlers.web.auth import web_login_required

class ProjectsRegistrationPage(WebRequestHandler):
	@web_login_required
	def get(self):
		path = 'project_registration.html'
		template_values = {}
		self.write(self.get_rendered_html(path, template_values), 200)


app = webapp2.WSGIApplication(
    [
        ('/projects/registration', ProjectsRegistrationPage)
    ]
)