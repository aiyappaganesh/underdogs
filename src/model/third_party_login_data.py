from google.appengine.ext import db

class ThirdPartyLoginData(db.Model):
	parent_id = db.IntegerProperty(indexed=True)
	network_name = db.StringProperty(indexed=False)