from google.appengine.ext import db

class Company(db.Model):
    name = db.StringProperty(indexed=False)
    email = db.StringProperty()
    details = db.StringProperty(indexed=False)
    influence_avg = db.FloatProperty(indexed=False)
    expertise_avg = db.StringListProperty(indexed=False)