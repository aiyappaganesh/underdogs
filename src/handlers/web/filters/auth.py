from google.appengine.ext.webapp import template
from gaesessions import get_current_session
import logging

register =  template.create_template_register()

@register.filter
def is_user_logged_in(dummy):
	logging.info('here!!!!!!!')
	session = get_current_session()
	if session.is_active() and 'me_id' in session:
		logging.info('Returning true...')
		return True
	logging.info('Returning false...')
	return False