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
	def delete(cls, email, company_id):
		invited_member = cls.get_by_key_name(email)
		if invited_member:
			if len(invited_member.companies) > 1 and int(company_id) in invited_member.companies:
				invited_member.companies.remove(int(company_id))
				invited_member.put()
			else:
				db.delete(invited_member)


	@classmethod
	def is_invited(cls, email, company_id):
		invited_member = cls.get_by_key_name(email)
		if invited_member and int(company_id) in invited_member.companies:
			return True
		return False