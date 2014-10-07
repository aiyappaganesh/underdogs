from google.appengine.ext import db

class Project(db.Model):
    title = db.StringProperty(indexed=False)
    description = db.StringProperty(indexed=False)
    bid = db.FloatProperty()
    end_date = db.DateProperty()
    skills = db.StringListProperty(indexed=False)