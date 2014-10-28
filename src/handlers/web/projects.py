import logging
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
            matched_skills = 0.0
            fit = 0.0
            id = c.key().id()
            sorted_companies[id] = {}
            sorted_companies[id]['name'] = c.name
            sorted_companies[id]['influence'] = c.influence_avg
            sorted_companies[id]['skills'] = []
            if skills:
                for skill in skills:
                    skill = str(skill)
                    if skill in expertise_dict:
                        skill_dict = { 'name':skill,'value':float(expertise_dict[skill]) }
                        score += float(expertise_dict[skill])
                        matched_skills += 1
                    else:
                        skill_dict = { 'name':skill,'value':0.0 }
                    sorted_companies[id]['skills'].append(skill_dict)
                score = float(score / len(skills))
                fit = float(matched_skills / len(skills)) if matched_skills > 0.0 else 0.0
            sorted_companies[id]['combined']=score
            sorted_companies[id]['fit']=fit
        donuts = (len(skills) if skills else 0) + 3
        sorted_companies = sorted(sorted_companies.iteritems(), key=lambda (k,v): v['combined'], reverse = True)
        donut_size = 80-(5*donuts)
        score_font_size = 40-(3*donuts)
        tooltip_font_size = 14-donuts
        template_values = {'startups' : sorted_companies, 'skills' : skills, 'donut_size' : donut_size, 'score_font_size' : score_font_size, 'tooltip_font_size' : tooltip_font_size}
        self.write(self.get_rendered_html(path, template_values), 200)

class ProjectListPage(WebRequestHandler):
    def make_json(self, projects):
        return [{'title': project.title, 'description': project.description, 'skills': project.skills, 'bid': project.bid, 'end_date': project.end_date} for project in projects]

    def get_all_projects(self, order, column):
        q = Project.all()
        if order == 'desc':
            q.order('-' + column)
        elif order == 'asc':
            q.order(column)
        return q.fetch(100)

    def get(self):
        order = self['order'] if self['order'] else 'desc'
        column = self['column'] if self['column'] else 'end_date'
        path = 'list_projects.html'
        projects = self.make_json(self.get_all_projects(order, column))
        template_values = {'projects': projects, 'order': order, 'column': column}
        self.write(self.get_rendered_html(path, template_values), 200)


app = webapp2.WSGIApplication(
    [
        ('/projects/registration', ProjectsRegistrationPage),
        ('/projects/list', ProjectListPage),
        ('/projects/fitting_startups', ProjectStartupsMatchingPage)
    ]
)