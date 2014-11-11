import webapp2
from handlers.web import WebRequestHandler
from model.skill import Skill
from model.company import Company
from google.appengine.api.blobstore import blobstore
from gaesessions import get_current_session
from handlers.web.auth import web_login_required
from util.util import registration_breadcrumbs
from util.util import get_user_projects
from model.skills.defn import skills_heirarchy
from model.project import Project

import operator
import logging

class StartupsPage(WebRequestHandler):
    def get(self):
        path = 'startups.html'
        template_values = {}
        self.write(self.get_rendered_html(path, template_values), 200)

class StartupsRegistrationPage(WebRequestHandler):
    @web_login_required
    def get(self):
        path = 'startup_registration.html'
        form_url = blobstore.create_upload_url('/api/startups/add_company')
        template_values = {'form_url': form_url, 
                           'breadcrumb_idx':1,
                           'breadcrumbs':registration_breadcrumbs}
        self.write(self.get_rendered_html(path, template_values), 200)

class StartupsEditPage(WebRequestHandler):
    def prepare_company_json(self, id):
        company = Company.get_by_id(id)
        company_json = {}
        company_json['id'] = id
        company_json['name'] = company.name
        company_json['image'] = '/api/common/download_image/'+company.image
        company_json['image_key'] = company.image
        company_json['hello'] = company.hello
        company_json['details'] = company.details
        return company_json

    @web_login_required
    def get(self):
        path = 'startup_edit.html'
        company_id = int(str(self['company_id']))
        company_json = self.prepare_company_json(company_id)
        form_url = blobstore.create_upload_url('/api/startups/update_company')
        template_values = {'form_url': form_url, 'company':company_json}
        self.write(self.get_rendered_html(path, template_values), 200)

class StartupsCriteriaPage(WebRequestHandler):
    def prepare_projects(self, projects):
        project_options = []
        for project in projects:
            option = {}
            option['name'] = project.title
            option['value'] = project.key().id
            project_options.append(option)
        return project_options

    def get(self):
        path = 'startup_selector.html'
        chart_axes = [('x_axis', 'X Axis'),
                      ('y_axis', 'Y Axis'),
                      ('radius', 'Radius')]
        axes_vals = ['Expertise', 'Influence', 'Size']
        axis_ids = [chart_axis[0] for chart_axis in chart_axes]
        chart_desc = {}
        for chart_axis in chart_axes:
            chart_desc[chart_axis] = axes_vals
        session = get_current_session()
        user_projects = []
        if 'me_email' in session:
            user_project_members = get_user_projects()
            if user_project_members:
                user_projects = [user_project_member['parent'] for user_project_member in user_project_members]
        else:
            user_projects = [project for project in Project.all()]

        projects = []
        if user_projects and len(user_projects) > 0:
            projects = self.prepare_projects(user_projects)

        template_values = {'chart_desc':chart_desc,
                           'axes_vals':axes_vals,
                           'skills_depth':range(len(skills_heirarchy)),
                           'projects':projects}
        self.write(self.get_rendered_html(path, template_values), 200)

class StartupsListingPage(WebRequestHandler):
    def get(self):
        path = 'startups_listing.html'
        q = Company.all()
        sorted_companies = {}
        for c in q.fetch(50):
            id = c.key().id()
            sorted_companies[id] = {}
            score = float(c.influence_avg) if c.influence_avg else 0.0
            sorted_companies[id]['score'] = score
            sorted_companies[id]['image'] = c.image
            sorted_companies[id]['name'] = c.name
            sorted_companies[id]['hello'] = c.hello
        sorted_companies = sorted(sorted_companies.iteritems(), key=lambda (k,v): v['score'], reverse = True)
        donuts = 1
        donuts = donuts - 1
        donut_size = 80-(5*donuts)
        score_font_size = 40-(3*donuts)
        tooltip_font_size = 14-donuts
        template_values = {'startups' : sorted_companies, 'donut_size' : donut_size, 'score_font_size' : score_font_size, 'tooltip_font_size' : tooltip_font_size}
        self.write(self.get_rendered_html(path, template_values), 200)

app = webapp2.WSGIApplication(
    [
        ('/startups/registration', StartupsRegistrationPage),
        ('/startups/edit', StartupsEditPage),
        ('/startups/search/criteria', StartupsCriteriaPage),
        ('/startups/listing', StartupsListingPage),
        ('/startups', StartupsPage)
    ]
)