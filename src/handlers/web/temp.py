import webapp2
import logging
import urllib
import json

from handlers.web import WebRequestHandler
from model.skill import Skill
from model.company import Company
from model.company_members import CompanyMember
from model.skills.defn import get_skills_json

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
        chart_axes = [('x_axis', 'X Axis'),
                      ('y_axis', 'Y Axis'),
                      ('radius', 'Radius')]
        axes_vals = ['Expertise', 'Influence', 'Size']
        axis_ids = [chart_axis[0] for chart_axis in chart_axes]
        chart_desc = {}
        for chart_axis in chart_axes:
            chart_desc[chart_axis] = axes_vals
        template_values = {'skills':skills,
                           'query_param':urllib.urlencode({'skill':skills[0]}),
                           'chart_desc':chart_desc,
                           'axes_vals':axes_vals}
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
        q = CompanyMember.all().ancestor(c)
        return q.count()

    def get(self):
        sel_skill = self['skill']
        q = Company.all()
        companies = []
        domain = {'influence' : [0, 1],
                  'expertise' : [0, 1],
                  'size' : [0, 5]}
        for c in q.fetch(100):
            curr_c = {}
            curr_c['name'] = c.name
            curr_c['influence'] = c.influence_avg
            curr_c['expertise'] = float(self.get_expertise_val_for(c))
            curr_c['id'] = c.key().id()
            curr_c['size'] = self.get_size_for(c)
            companies.append(curr_c)
        ret_val = {'companies' : companies,
                   'domain' : domain}
        self.write(json.dumps(ret_val))

class SkillsVisualiser(WebRequestHandler):
    def get(self):
        path = 'skills_visualise.html'
        self.write(self.get_rendered_html(path, {}), 200)

class SkillsData(WebRequestHandler):
    def get(self):
        self.write(json.dumps(get_skills_json()))

app = webapp2.WSGIApplication(
    [
        ('/temp', TempPage),
        ('/temp/company_data', CompanyData),
        ('/temp/visualise_skills', SkillsVisualiser),
        ('/temp/skills_data', SkillsData)
    ]
)