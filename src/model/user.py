from google.appengine.ext import db

class User(db.Model):
   	name = db.StringProperty(indexed=False)
   	influence = db.FloatProperty(indexed=False)