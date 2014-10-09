import webapp2
import logging
import urllib
import json

from handlers.web import WebRequestHandler
from model.skill import Skill
from model.company import Company
from model.user import User

class TempPage(WebRequestHandler):
    def load_skills(self):
        q = Skill.all()
        skills = q.fetch(100)
        ret_val = [s.name for s in skills]
        selected_skill = self['sel_skill']
        if selected_skill:
            ret_val.remove(selected_skill)
            ret_val.insert(0, selected_skill)
        return ret_val

    def get(self):
        skills = self.load_skills()
        path = 'temp.html'
        template_values = {'skills':skills,
                           'query_param':urllib.urlencode({'skill':skills[0]})}
        self.write(self.get_rendered_html(path, template_values), 200)

class CompanyData(WebRequestHandler):
    def get_expertise_val_for(self, c):
        avg_expertise = c.expertise_avg
        for curr_avg in avg_expertise:
            exp, val = curr_avg.split(' : ')
            if exp.strip() == self['skill'].strip():
                return val
        return 0.0

    def get_size_for(self, c):
        q = User.all().ancestor(c)
        return q.count()

    def get(self):
        sel_skill = self['skill']
        q = Company.all()
        ret_val = []
        for c in q.fetch(100):
            curr_c = {}
            curr_c['name'] = c.name
            curr_c['influence'] = c.influence_avg
            curr_c['expertise'] = self.get_expertise_val_for(c)
            curr_c['size'] = self.get_size_for(c)
            logging.info(sel_skill)
            ret_val.append(curr_c)
        logging.info(ret_val)
        self.write(json.dumps(ret_val))

app = webapp2.WSGIApplication(
    [
        ('/temp', TempPage),
        ('/temp/company_data', CompanyData)
    ]
)