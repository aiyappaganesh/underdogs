from google.appengine.ext import db

class ThirdPartyUser(db.Model):
	followers = db.IntegerProperty(indexed=False)
	access_token = db.StringProperty(indexed=False)
 	id = db.StringProperty(indexed=False)