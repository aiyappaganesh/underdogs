import webapp2
import logging

from google.appengine.ext import deferred

from model.third_party_user import ThirdPartyUser
from model.user import User
from model.company import Company
from networks import GITHUB, LINKEDIN, ANGELLIST
from user_data import github, linkedin, angellist
from util.util import isAdminAccess
from handlers.web import WebRequestHandler
from google.appengine.api import mail
from handlers.web.auth import web_login_required
from model.third_party_login_data import ThirdPartyLoginData

networks = {
	GITHUB: github,
	LINKEDIN: linkedin,
    ANGELLIST: angellist
}

def pull_company_data(company):
    users = User.all().ancestor(company)
    company.influence_avg = None
    company.expertise_avg = []
    company.put()
    influence_total = 0.0
    expertise_total = {}
    for user in users:
        user.influence = None
        user.expertise = []
        user.put()
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
    	company.expertise_avg.append(skill + ' : ' + str(score / float(users.count())))
    company.put()

class MemberDataPullHandler(webapp2.RequestHandler):
    def put(self):
        company_id = int(self.request.get('company_id'))
        company = Company.get_by_id(company_id)
        deferred.defer(pull_company_data, company)

class MemberInviteHandler(WebRequestHandler):
    @web_login_required
    def post(self):
        if not isAdminAccess(self):
            return
        company = Company.get_by_id(int(self['company_id']))
        mail.send_mail(sender="Underdog Admin <ranju@b-eagles.com>",
              to=self['email'],
              subject="Invitation to join " + company.name,
              body="""
Hello!

Please follow this link to add yourself:

https://minyattra.appspot.com/member/finish_invite?company_id={0}

Thanks!
""".format(self['company_id']))

class MemberSignupHandler(WebRequestHandler):
    def user_exists(self):
        email = self['email']
        user = User.get_by_key_name(email)
        if user:
            return True
        return False

    @web_login_required
    def post(self):
        email = self['email']
        if not self.user_exists():
            user = User(key_name = email)
            tpld = ThirdPartyLoginData()
            tpld.network_name = self['network']
            tpld.parent_id = email
            user.put()
            tpld.put()
            self.redirect('/')
        else:
            self.write("Internal error", 500)

app = webapp2.WSGIApplication([	('/api/members/pull_data', MemberDataPullHandler),
                                ('/api/members/invite', MemberInviteHandler),
                                ('/api/members/finish_signup', MemberSignupHandler)])
