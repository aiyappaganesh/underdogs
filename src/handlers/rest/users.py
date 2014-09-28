import webapp2
import logging

from google.appengine.ext import deferred

from model.third_party_user import ThirdPartyUser
from model.user import User
from model.company import Company
from networks import GITHUB, LINKEDIN
from user_data import github, linkedin


networks = {
	GITHUB: github,
	LINKEDIN: linkedin
}

def pull_company_data(company):
    users = User.all().ancestor(company)
    influence_total = 0.0
    expertise_total = {}
    for user in users:
        for network, user_data in networks.iteritems():
            third_party_user = ThirdPartyUser.get_by_key_name(network, parent=user)
            if third_party_user:
            	user_data.pull_data(user, third_party_user)
        if not user.influence or not user.expertise:
        	continue
        influence_total += user.influence
        for expertise in user.expertise:
        	skill, score = expertise.split(' : ')
        	if skill not in expertise_total:
        		expertise_total[skill] = 0.0
        	expertise_total[skill] += float(score)
    company.influence_avg = (influence_total) / float(users.count())
    company.expertise_avg = []
    for skill, score in expertise_total.iteritems():
    	logging.info('here...')
    	company.expertise_avg.append(skill + ' : ' + str(score / float(users.count())))
    company.put()

class MemberDataPullHandler(webapp2.RequestHandler):
    def put(self):
        company_id = int(self.request.get('company_id'))
        company = Company.get_by_id(company_id)
        deferred.defer(pull_company_data, company)

app = webapp2.WSGIApplication([	('/api/members/pull_data', MemberDataPullHandler)])
