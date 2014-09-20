import webapp2
import logging

from model.third_party_user import ThirdPartyUser
from model.user import User
from networks import GITHUB, LINKEDIN
from user_data import github, linkedin


networks = {
	GITHUB: github,
	LINKEDIN: linkedin
}

class MemberDataPullHandler(webapp2.RequestHandler):
	def get(self):
		network = self.request.get('network')
		email = self.request.get('email')
		user = User.get_by_key_name(email)
		logging.info(email)
		logging.info(user)
		third_party_user = ThirdPartyUser.get_by_key_name(network, parent=user)
		networks[network].pull_data(user, third_party_user)

app = webapp2.WSGIApplication([	('/api/members/pull_data', MemberDataPullHandler)])
