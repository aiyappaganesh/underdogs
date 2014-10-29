from google.appengine.ext import db
from webapp2_extras.security import generate_password_hash, check_password_hash

import logging

class User(db.Model):
    name = db.StringProperty(indexed=False)
    password = db.StringProperty(indexed=False)
    photo = db.StringProperty(indexed=False)

    @classmethod
    def update(cls, email, name=None, password=None, photo=None):
        user = cls.get_by_key_name(email)
        if user:
            if name:
                user.name = name
            if password:
                user.password = generate_password_hash(password)
            if photo:
                user.photo = photo
            user.put()
