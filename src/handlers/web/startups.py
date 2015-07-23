import webapp2
from handlers.web import WebRequestHandler
from model.skill import Skill
from model.company import Company
from google.appengine.api.blobstore import blobstore
from gaesessions import get_current_session
from handlers.web.auth import web_login_required
from util.util import registration_breadcrumbs, startups
from util.util import get_user_projects, isAdminAccess
from model.skills.defn import skills_heirarchy
from model.project import Project
from cities_mapping import cities_map

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
        breadcrumb_idx = 1
        template_values = {'form_url': form_url, 
                           'breadcrumb_idx':breadcrumb_idx,
                           'breadcrumbs_len':len(registration_breadcrumbs[startups]),
                           'breadcrumb':registration_breadcrumbs[startups][breadcrumb_idx-1],
                           'progress': (100/len(registration_breadcrumbs[startups]))*breadcrumb_idx}
        self.write(self.get_rendered_html(path, template_values), 200)

class StartupsEditPage(WebRequestHandler):
    def prepare_company_json(self, id):
        company = Company.get_by_id(id)
        company_json = {}
        company_json['id'] = id
        company_json['name'] = company.name
        if company.image:
            company_json['image'] = '/api/common/download_image/'+company.image
            company_json['image_key'] = company.image
        company_json['hello'] = company.hello
        company_json['profile'] = company.profile
        company_json['website'] = company.website
        company_json['tags'] = company.tags
        return company_json

    @web_login_required
    def get(self):
        company_id = int(str(self['company_id']))
        if not Company.get_by_id(company_id):
            self.write('no company')
            return
        if not isAdminAccess(self):
            return
        path = 'startup_edit.html'
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

class LatestStartupsListingPage(WebRequestHandler):
    def make_dict(self, company):
        company_dict = {}
        company_dict['score'] = float(company.influence_avg) if company.influence_avg else 0.0
        company_dict['image'] = '/api/common/download_image/' + str(company.image) if company.image else '/assets/img/company/company.png'
        company_dict['name'] = company.name
        company_dict['hello'] = company.hello if company.hello else '\n'
        company_dict['profile'] = company.profile if company.profile else '\n'
        company_dict['city'] = cities_map[str(id)] if str(id) in cities_map else cities_map['default']
        company_dict['url'] = '/member/new_list?company_id=' + str(company.key().id())
        return company_dict

    def get(self):
        path = 'startups_latest.html'
        q = Company.all()
        logging.info(q.count())
        companies = [self.make_dict(company) for company in q]
        companies.insert(0, {'image': '/assets/img/new_startup.png', 'name': 'Your Startup', 'url': '/startups/registration'})
        sorted_company_rows = [companies[i: i+3] for i in range(0, len(companies), 3)]
        template_values = {'startups' : sorted_company_rows, 'nav_color':'dark-nav'}
        self.write(self.get_rendered_html(path, template_values), 200)

class StartupsHomePage(WebRequestHandler):
    def get(self):
        path = 'startups_home.html'
        template_values = {}
        template_values['no_navbar_onload'] = True
        self.write(self.get_rendered_html(path, template_values), 200)

app = webapp2.WSGIApplication(
    [
        ('/startups_home', StartupsHomePage),
        ('/startups/registration', StartupsRegistrationPage),
        ('/startups/edit', StartupsEditPage),
        ('/startups/search/criteria', StartupsCriteriaPage),
        ('/startups/new_listing', LatestStartupsListingPage),
        ('/startups', StartupsPage)
    ]
)