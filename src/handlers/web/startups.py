import webapp2
from handlers.web import WebRequestHandler
from model.skill import Skill
from model.company import Company
from google.appengine.api.blobstore import blobstore
from gaesessions import get_current_session
from handlers.web.auth import web_login_required
from util.util import registration_breadcrumbs
from util.util import get_user_projects

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
        session = get_current_session()
        path = 'startup_registration.html'
        form_url = blobstore.create_upload_url('/api/startups/add_company')
        template_values = {'form_url': form_url, 
                           'user_id': session['me_id'], 
                           'name':session['me_name'], 
                           'access_token':session['me_access_token'],
                           'breadcrumb_idx':1,
                           'breadcrumbs':registration_breadcrumbs}
        self.write(self.get_rendered_html(path, template_values), 200)

class StartupsCriteriaPage(WebRequestHandler):
    def render_project_selector(self, projects):
        path = 'project_selector.html'
        project_options = []
        for project in projects:
            option = {}
            option['name'] = project.title
            option['value'] = project.key().id
            project_options.append(option)
        template_values = {'projects' : project_options}
        self.write(self.get_rendered_html(path, template_values), 200)

    def render_project_creator(self):
        path = 'project_creator.html'
        self.write(self.get_rendered_html(path, None), 200)

    @web_login_required
    def get(self):
        projects = get_user_projects()
        if projects and len(projects) > 0:
            self.render_project_selector(projects)
        else:
            self.render_project_creator()

class StartupsSearchResultsPage(WebRequestHandler):
    def convert_string_list_to_dict(self, str_list):
        ret_val = {}
        for param in str_list:
            skill, score = param.split(' : ')
            ret_val[skill] = score
        return ret_val

    def get(self):
        path = 'startups_search_results.html'
        skill = self['Skill']
        q = Company.all()
        sorted_companies = {}
        for c in q.fetch(50):
            expertise_dict = self.convert_string_list_to_dict(c.expertise_avg)
            score = 0.0
            if skill in expertise_dict:
                score = float(expertise_dict[skill])
            sorted_companies[c] = score
        sorted_companies = sorted(sorted_companies.iteritems(), key=operator.itemgetter(1), reverse = True)
        template_values = {'startups' : sorted_companies}
        self.write(self.get_rendered_html(path, template_values), 200)

app = webapp2.WSGIApplication(
    [
        ('/startups/registration', StartupsRegistrationPage),
        ('/startups/search/criteria', StartupsCriteriaPage),
        ('/startups/search', StartupsSearchResultsPage),
        ('/startups', StartupsPage)
    ]
)