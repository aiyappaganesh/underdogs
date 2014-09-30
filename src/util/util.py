import logging

from model.company import Company
from model.user import User
from gaesessions import get_current_session

registration_breadcrumbs = [('Get started', 'Tell us about your startup!'),
              ('Invite team members', 'Build your team'),
              ('Give us access to your data', 'Help us learn more about you')]

def isAdminAccess(req_handler):
	session = get_current_session()
	admin_id = session['me_id']
	company_id = req_handler['company_id']
	c = Company.get_by_id(int(company_id))
	a = User.get_by_key_name(admin_id, parent=c)
	if a and a.isAdmin:
		return True
	return False