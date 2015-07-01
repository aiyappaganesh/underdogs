from google.appengine.api import urlfetch
import urllib
import json
import base64
import datetime
import time

APP_ID = 'xouub8j6'
API_KEY = '534ee46e252a2c32cb5d099c5fcd01ff616bf847'

def users(email, **kwargs):
	url = 'https://api.intercom.io/users'
	params = {'email': email}
	params.update(kwargs)
	response = json.loads(urlfetch.fetch(url, payload=json.dumps(params), method=urlfetch.POST, headers={'Content-Type': 'application/json', 'Accept': 'application/json', "Authorization": "Basic %s" % base64.b64encode("%s:%s"%(APP_ID, API_KEY))}).content)
	return response

def events(email, **kwargs):
	url = 'https://api.intercom.io/events'
	params = {'email': email, 'created_at': int(time.time())}
	params.update(kwargs)
	urlfetch.fetch(url, payload=json.dumps(params), method=urlfetch.POST, headers={'Content-Type': 'application/json', 'Accept': 'application/json', "Authorization": "Basic %s" % base64.b64encode("%s:%s"%(APP_ID, API_KEY))}).content
