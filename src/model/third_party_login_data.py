from google.appengine.ext import db

class ThirdPartyLoginData(db.Model):
	parent_id = db.StringProperty(indexed=True)
	network_name = db.StringProperty(indexed=False)