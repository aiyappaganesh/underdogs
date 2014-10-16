from google.appengine.ext import db

class InvitedMember(db.Model):
    company_id = db.IntegerProperty(indexed=True)
