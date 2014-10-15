from google.appengine.ext import db
import logging

class User(db.Model):
    name = db.StringProperty(indexed=False)
    password = db.StringProperty(indexed=False)
    isAdmin = db.BooleanProperty()
    photo = db.StringProperty(indexed=False)