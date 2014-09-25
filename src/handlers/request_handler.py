from util import http_util
import webapp2
import webapp2_extras
from webapp2_extras import sessions

webapp2_extras.sessions.default_config['secret_key'] = 'asdfasdf'
webapp2_extras.sessions.default_config['cookie_name'] = 'underdogs'

APP_JSON = "application/json"

class RequestHandlerMixin(object):
    def write(self,text=None, status=None, content_type = None):
        http_util.write(self.response, text, status, content_type)

    def set_status(self,value):
        self.response.set_status(value)

    def __getitem__(self, name):
        return self.request.get(name, default_value=None)

    def get_all(self, name):
        return self.request.get_all(name, default_value=None)

class RequestHandler(webapp2.RequestHandler, RequestHandlerMixin):
    def dispatch(self):
        self.session_store = sessions.get_store(request=self.request)
        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session()