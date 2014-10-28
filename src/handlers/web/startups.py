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
        path = 'startup_registration.html'
        form_url = blobstore.create_upload_url('/api/startups/add_company')
        template_values = {'form_url': form_url, 
                           'breadcrumb_idx':1,
                           'breadcrumbs':registration_breadcrumbs}
        self.write(self.get_rendered_html(path, template_values), 200)

class StartupsCriteriaPage(WebRequestHandler):
    def render_project_selector(self, projects):
        path = 'project_selector.html'
        project_options = []
        for user_project in projects:
            option = {}
            option['name'] = user_project['parent'].title
            option['value'] = user_project['parent'].key().id
            project_options.append(option)
        template_values = {'projects' : project_options}
        self.write(self.get_rendered_html(path, template_values), 200)

    def render_project_creator(self):
        path = 'project_creator.html'
        self.write(self.get_rendered_html(path, None), 200)

    @web_login_required
    def get(self):
        user_projects = get_user_projects()
        if user_projects and len(user_projects) > 0:
            self.render_project_selector(user_projects)
        else:
            self.render_project_creator()

class StartupsListingPage(WebRequestHandler):
    def get(self):
        path = 'startups_listing.html'
        q = Company.all()
        sorted_companies = {}
        for c in q.fetch(50):
            score = float(c.influence_avg) if c.influence_avg else 0.0
            sorted_companies[c] = score
        sorted_companies = sorted(sorted_companies.iteritems(), key=operator.itemgetter(1), reverse = True)
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
        ('/startups/search/criteria', StartupsCriteriaPage),
        ('/startups/listing', StartupsListingPage),
        ('/startups', StartupsPage)
    ]
)