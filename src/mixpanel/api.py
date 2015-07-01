from mixpanel import Mixpanel

TOKEN = '46a8b36996f1c18b64c39ec426254234'

def events(email, event_name):
	mp = Mixpanel(TOKEN)
	mp.track(email, event_name)

def users(email, name=None, ip=None):
	mp = Mixpanel(TOKEN)
	params = {'$email': email}
	if name:
		params['$name'] = name
	if ip:
		params['$ip'] = ip
	mp.people_set(email, params)