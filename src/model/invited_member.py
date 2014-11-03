from google.appengine.ext import db
import logging

class InvitedMember(db.Model):
	companies = db.ListProperty(int)

	@classmethod
	def create_or_update(cls, email, company_id):
		invited_member = cls.get_by_key_name(email)
		if not invited_member:
			invited_member = cls(key_name=email)
		invited_member.companies.append(int(company_id))
		invited_member.put()

	@classmethod
	def is_invited(cls, email, company_id):
		invited_member = cls.get_by_key_name(email)
		if invited_member and int(company_id) in invited_member.companies:
			return True
		return False