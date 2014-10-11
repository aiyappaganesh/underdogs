import webapp2
import logging

from handlers.web import WebRequestHandler
from networks import LINKEDIN, FACEBOOK, TWITTER

class ThirdPartyLoginHandler(WebRequestHandler):
    def get(self):
        logging.info('Here..')

handlers = []
for network in [FACEBOOK, LINKEDIN, TWITTER]:
    handlers.append(('/users/' + network + '/login_callback', ThirdPartyLoginHandler))

app = webapp2.WSGIApplication(handlers)