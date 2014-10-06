import logging

from handlers.rest.rest_application import RestApplication
from handlers import RequestHandler

class AddProjectHandler(RequestHandler):
    def post(self):
    	logging.info('here...')

app = RestApplication([
    ('/api/projects/add_project', AddProjectHandler)
])