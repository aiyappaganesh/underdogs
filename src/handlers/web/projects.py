import webapp2
from model.skill import Skill
from handlers.web import WebRequestHandler
from handlers.web.auth import web_login_required
from util.util import convert_string_list_to_dict
from model.company import Company
from model.project import Project
import operator

class ProjectsRegistrationPage(WebRequestHandler):
    @web_login_required
    def get(self):
        path = 'project_registration.html'
        template_values = {}
        template_values['duration_options'] = [{'name':'Less than 3 months','value':'3'},
                                               {'name':'3 to 6 months','value':'6'},
                                               {'name':'More than 6 months','value':'12'}]
        q = Skill.all()
        skills = q.fetch(100)
        skill_options = []
        for skill in skills:
            skill_option = {}
            skill_option['name'] = skill.name
            skill_option['value'] = skill.name
            skill_options.append(skill_option)
        template_values['skills'] = skill_options
        self.write(self.get_rendered_html(path, template_values), 200)

class ProjectStartupsMatchingPage(WebRequestHandler):
    def get(self):
        path = 'startups_search_results.html'
        project_id = long(self['project_id'])
        project = Project.get_by_id(project_id)
        skills = project.skills
        q = Company.all()
        sorted_companies = {}
        for c in q.fetch(50):
            expertise_dict = convert_string_list_to_dict(c.expertise_avg)
            score = 0.0
            if skills:
                for skill in skills:
                    if skill in expertise_dict:
                        score += float(expertise_dict[skill])
                score = float(score / len(skills))
            sorted_companies[c] = score
        sorted_companies = sorted(sorted_companies.iteritems(), key=operator.itemgetter(1), reverse = True)
        template_values = {'startups' : sorted_companies}
        self.write(self.get_rendered_html(path, template_values), 200)

app = webapp2.WSGIApplication(
    [
        ('/projects/registration', ProjectsRegistrationPage),
        ('/projects/fitting_startups', ProjectStartupsMatchingPage)
    ]
)