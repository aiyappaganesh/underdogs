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
        template_values = {'chart_desc':chart_desc,
                           'axes_vals':axes_vals,
                           'skills_depth':range(len(skills_heirarchy))}
        self.write(self.get_rendered_html(path, template_values), 200)

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