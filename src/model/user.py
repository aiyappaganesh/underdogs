from google.appengine.ext import db
import logging

class User(db.Model):
    name = db.StringProperty(indexed=False)
    password = db.StringProperty(indexed=False)
    isAdmin = db.BooleanProperty()
    photo = db.StringProperty(indexed=False)

    @classmethod
    def update(cls, email, name=None, password=None, photo=None):
        user = User.get_by_key_name(email)
        if user:
            if name:
                user.name = name
            if password:
                user.password = password
            if photo:
                user.photo = photo
            user.put()