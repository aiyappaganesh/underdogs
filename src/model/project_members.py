from google.appengine.ext import db
import logging

class ProjectMember(db.Model):
    user_id = db.StringProperty(indexed=True)
    is_admin = db.BooleanProperty(indexed=False)