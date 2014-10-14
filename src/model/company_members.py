from google.appengine.ext import db

class CompanyMember(db.Model):
    user_id = db.StringProperty(indexed=True)
    is_admin = db.BooleanProperty(indexed=False)