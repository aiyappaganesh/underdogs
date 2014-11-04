import webapp2
import logging
import urllib
import json

from handlers.web.auth import web_login_required
from handlers.web import WebRequestHandler
from gaesessions import get_current_session
from model.user import User
from model.skill import Skill
from model.company import Company
from model.company_members import CompanyMember
from model.skills.defn import get_skills_json, get_skills_parents_map, skills_heirarchy

class TempPage(WebRequestHandler):
    def get(self):
        path = 'temp.html'
        self.write(self.get_rendered_html(path, {}), 200)

class CompanyData(WebRequestHandler):
    def get_expertise_val_for(self, c):
        avg_expertise = c.expertise_avg
        for curr_avg in avg_expertise:
            exp, val = curr_avg.split(' : ')
            if exp.strip() == self['skill'].strip():
                return val
        return 0.0

    def get_size_for(self, c):
        q = CompanyMember.all().ancestor(c)
        return q.count()

    def get(self):
        q = Company.all()
        companies = []
        domain = {'influence' : [0, 1],
                  'expertise' : [0, 1],
                  'size' : [0, 5]}
        for c in q.fetch(100):
            curr_c = {}
            curr_c['name'] = c.name
            curr_c['influence'] = c.influence_avg
            curr_c['expertise'] = get_skills_json(c.get_expertise_avg())
            curr_c['id'] = c.key().id()
            curr_c['size'] = self.get_size_for(c)
            companies.append(curr_c)
        ret_val = {'companies' : companies,
                   'domain' : domain}
        self.write(json.dumps(ret_val))

class CompanyMembers(WebRequestHandler):
    def get(self):
        company = Company.get_by_id(int(str(self['company_id'])))
        if not company:
            self.write('no company')
            return
        members = CompanyMember.all().ancestor(company)
        ret_val = []
        for member in members.fetch(1000):
            user = User.get_by_key_name(member.user_id)
            ret_val.append({'name' : user.name, 'id' : member.key().id()})
        self.write(json.dumps(ret_val))

class SkillsVisualiser(WebRequestHandler):
    def get_companies(self):
        q = Company.all()
        companies = []
        for company in q.fetch(100):
            companies.append({'value' : company.key().id(), 'name' : company.name})
        return companies

    def get(self):
        path = 'skills_visualise.html'
        self.write(self.get_rendered_html(path, {'companies' : self.get_companies()}), 200)

class ProfileSkillsVisualiser(WebRequestHandler):
    def get_companies_for(self, email):
        members = CompanyMember.all().filter('user_id =', email)
        companies = []
        for company_member in members.fetch(100):
            user = User.get_by_key_name(company_member.user_id)
            companies.append({'value' : company_member.parent().key().id(), 'name' : company_member.parent().name, 'member_name' : user.name, 'member_id' : company_member.key().id()})
        return companies

    @web_login_required
    def get(self):
        path = 'skills_visualise.html'
        session = get_current_session()
        email = session['me_email']
        self.write(self.get_rendered_html(path, {'companies' : self.get_companies_for(email), 'for_profile' : True}), 200)

class SkillsData(WebRequestHandler):
    def get_skills_json_for(self, company_id):
        skills_heirarchy = get_skills_json()
        parents_map = get_skills_parents_map()

    def get(self):
        expertise = None
        company = Company.get_by_id(int(str(self['company_id'])))
        if not company:
            self.write('no company')
            return
        if self['member_id']:
            member = CompanyMember.get_by_id(int(str(self['member_id'])), parent=company)
            expertise = member.get_expertise()
        else:
            expertise = company.get_expertise_avg()
        self.write(json.dumps(get_skills_json(expertise)))

class SkillsHeirarchy(WebRequestHandler):
    def get(self):
        self.write(json.dumps(skills_heirarchy))

app = webapp2.WSGIApplication(
    [
        ('/temp', TempPage),
        ('/temp/company_data', CompanyData),
        ('/temp/company_members', CompanyMembers),
        ('/temp/visualise_skills', SkillsVisualiser),
        ('/temp/visualise_profile_skills', ProfileSkillsVisualiser),
        ('/temp/skills_data', SkillsData),
        ('/temp/skills_heirarchy', SkillsHeirarchy)
    ]
)