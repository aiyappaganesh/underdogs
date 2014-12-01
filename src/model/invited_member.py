from google.appengine.ext import db
import logging

class InvitedMember(db.Model):
	companies = db.ListProperty(int)

	@classmethod
	def create_(cls, email, company_id):
		cls(key_name="%s###%s"%(email, company_id)).put()

	@classmethod
	def for_(cls, email, company_id):
		return cls.get_by_key_name("%s###%s"%(email, company_id))

	def delete(self):
		db.delete(self)
