import logging
import webapp2
from handlers.web import WebRequestHandler

class LoginPageHadler(WebRequestHandler):
	def get(self):
		path = 'login_page.html'
		self.write(, 200)

app = webapp2.WSGIApplication([('/login', LoginPageHadler)])