import webapp2
import logging
import json
from util import http_util

def _handle_500(request,  response,  exception):
    logging.exception(exception)
    http_util.write(response,
                    text = json.dumps({'errors' : [
                        exception.message
                        if exception
                        else "An error occured"
                    ]}),
                    content_type = "application/json",
                    status = 500)


class RestApplication(webapp2.WSGIApplication):
    def __init__(self, *args,**kwargs):
        super(RestApplication, self).__init__(*args,**kwargs)
        self.error_handlers[500] = _handle_500


