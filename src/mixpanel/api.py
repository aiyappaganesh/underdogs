from mixpanel import Mixpanel

TOKEN = '46a8b36996f1c18b64c39ec426254234'

def events(email, event_name):
	mp = Mixpanel(TOKEN)
	mp.track(email, event_name)

def users(email, name):
	mp = Mixpanel(TOKEN)
	mp.people_set(email, {'$first_name': name, '$email': email})