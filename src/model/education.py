from google.appengine.ext import db

class Education(db.Model):
    school = db.StringProperty(indexed=False)
    field = db.StringProperty(indexed=False)
    start = db.DateProperty()
    end = db.DateProperty()
    degree = db.StringProperty(indexed=False)

def fetch_educations_for(user):
    educations = Education.all().ancestor(user).order('-start')
    return [e for e in educations.fetch(200)]