from google.appengine.ext import db

class Experience(db.Model):
    title = db.StringProperty(indexed=False)
    summary = db.TextProperty(indexed=False)
    start = db.DateProperty()
    end = db.DateProperty()
    company = db.StringProperty(indexed=False)

def fetch_experiences_for(user):
    experiences = Experience.all().ancestor(user).order('-start')
    return [e for e in experiences.fetch(200)]