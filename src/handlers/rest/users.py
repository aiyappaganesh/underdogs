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
		company_id = self.request.get('company_id')
		company = Company.get_by_id(int(company_id))
		users = User.all().ancestor(company)
		for user in users:
			for network, user_data in networks.iteritems():
				logging.info(network)
				logging.info(user.key().name())
				third_party_user = ThirdPartyUser.get_by_key_name(network, parent=user)
				logging.info(third_party_user)
				user_data.pull_data(user, third_party_user)

app = webapp2.WSGIApplication([	('/api/members/pull_data', MemberDataPullHandler)])
