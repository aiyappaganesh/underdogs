import webapp2
from handlers.web import WebRequestHandler
from model.skill import Skill
from model.company import Company
from google.appengine.api.blobstore import blobstore
import operator
import logging

class StartupsPage(WebRequestHandler):
    def get(self):
        path = 'startups.html'
        template_values = {}
        self.write(self.get_rendered_html(path, template_values), 200)

class StartupsRegistrationPage(WebRequestHandler):
    def get(self):
        path = 'startup_registration.html'
        form_url = blobstore.create_upload_url('/api/startups/add_company')
        template_values = {'form_url':form_url}
        self.write(self.get_rendered_html(path, template_values), 200)

class StartupsCriteriaPage(WebRequestHandler):
    def get(self):
        path = 'startups_search_criteria.html'
        q = Skill.all()
        template_values = {'skills' : q.fetch(50)}
        self.write(self.get_rendered_html(path, template_values), 200)

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