from google.appengine.ext import db

class RegistrationQueue(db.Model):
    name = db.StringProperty(indexed=False)
