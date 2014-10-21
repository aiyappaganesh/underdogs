from google.appengine.ext import db

class ThirdPartyProfileData(db.Model):
	access_token = db.StringProperty(indexed=False)