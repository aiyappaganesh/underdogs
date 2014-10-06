from google.appengine.ext import db

class Project(db.Model):
    title = db.StringProperty(indexed=False)