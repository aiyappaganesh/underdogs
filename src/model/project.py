from google.appengine.ext import db

class Project(db.Model):
    title = db.StringProperty(indexed=False)
    description = db.StringProperty(indexed=False)
    end_time = db.TimeProperty(indexed=False)