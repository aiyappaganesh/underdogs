from google.appengine.ext import db

class Skill(db.Model):
    name = db.StringProperty(indexed=True)
