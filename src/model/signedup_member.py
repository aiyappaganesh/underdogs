from google.appengine.ext import db

class SignedUpMember(db.Model):
    pass

    @classmethod
    def create(cls, email):
        SignedUpMember(key_name=email).put()
        
    @classmethod
    def is_signedup(cls, email):
        signedup_member = cls.get_by_key_name(email)
        if signedup_member:
            return True
        return False