from google.appengine.ext.webapp import template
from gaesessions import get_current_session
import logging

register =  template.create_template_register()

@register.filter
def is_user_logged_in(dummy):
	session = get_current_session()
	if session.is_active() and \
	   'me_email' in session and \
	   'auth_only' not in session:
		return True
	return False

@register.filter
def is_user_not_logged_in(dummy):
	return not is_user_logged_in(dummy)