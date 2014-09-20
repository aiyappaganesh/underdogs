import webapp2
import logging

from model.third_party_user import ThirdPartyUser
from model.user import User
from model.company import Company
from networks import GITHUB, LINKEDIN
from user_data import github, linkedin


networks = {
	GITHUB: github,
	LINKEDIN: linkedin
}

class MemberDataPullHandler(webapp2.RequestHandler):
	def get(self):
		company_id = int(self.request.get('company_id'))
		company = Company.get_by_id(company_id)
		users = User.all().ancestor(company)
		for user in users:
			for network, user_data in networks.iteritems():
				third_party_user = ThirdPartyUser.get_by_key_name(network, parent=user)
				if third_party_user:
					user_data.pull_data(user, third_party_user)
		self.redirect('/member/list?company_id' + company_id)

app = webapp2.WSGIApplication([	('/api/members/pull_data', MemberDataPullHandler)])
