import logging
import time
import urllib
import json
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import blobstore_handlers
from handlers.rest.rest_application import RestApplication
from handlers import RequestHandler
from handlers.web.auth import web_login_required
from gaesessions import get_current_session
from model.project import Project
from model.project_members import ProjectMember
from model.user import User
from datetime import date, datetime, timedelta
from intercomio import api as intercomio_api
from mixpanel import api as mixpanel_api

typeform_id = 'z299KT'
typeform_url = 'https://api.typeform.com/v0/form/'+typeform_id
typeform_key = 'ba3e6147586f116c0f2b65770ea446d5a44f4db6'
one_day_in_seconds = 86400

class AddProjectHandler(blobstore_handlers.BlobstoreUploadHandler, RequestHandler):
    def read_image(self):
        image = self.get_uploads("project_image")
        image_key = str(image[0].key()) if image else None
        return image_key

    def create_project(self, image_key):
        p = Project()
        p.title = self['project_title']
        p.description = self['description']
        p.skills = self['project_skills'].split(',') if self['project_skills'] else []
        p.end_date = datetime.strptime(str(self['project_end_date']), "%Y-%m-%d").date()
        p.bid = float(self['project_bid'])
        p.category = self['category']
        p.image = image_key
        p.put()
        return p

    def create_project_admin(self, p, user_id):
        session = get_current_session()
        ProjectMember(parent=p, user_id = user_id, is_admin=True).put()

    @web_login_required
    def post(self):
        image_key = self.read_image()
        p = self.create_project(image_key)
        session = get_current_session()
        self.create_project_admin(p, session['me_email'])
        intercomio_api.events(session['me_email'], event_name='created_project')
        mixpanel_api.events(session['me_email'], 'created_project')
        self.redirect('/startups/search/criteria')

class UpdateProjectHandler(RequestHandler):
    def update_project(self):
        id = int(str(self['project_id']))
        if id:
            p = Project.get_by_id(id)
            p.title = self['project_title']
            p.description = self['description']
            p.skills = self['project_skills'].split(',') if self['project_skills'] else []
            p.end_date = datetime.strptime(str(self['project_end_date']), "%Y-%m-%d").date()
            p.bid = float(self['project_bid'])
            p.put()

    @web_login_required
    def post(self):
        p = self.update_project()
        self.redirect('/member/projects/dashboard')

class FetchProjectsHandler(RequestHandler):
    questions_list = {'Name of your project':'title',
                      'Describe your project':'description',
                      'Project Completion Day':'end_day',
                      'Project Completion Month':'end_month',
                      'Project Completion Year':'end_year',
                      'What type of app would you like to be built?':'category'
    }

    def get(self):
        current_time = time.time()
        time_day_back = current_time - (timedelta(seconds=one_day_in_seconds).total_seconds())
        until = self['until'] if self['until'] else str(int(current_time))
        since = self['since'] if self['since'] else str(int(time_day_back))
        params = {'key':typeform_key,
                  'completed':True,
                  'since':since,
                  'until':until}
        url = typeform_url + '?' + urllib.urlencode(params)
        resp = urlfetch.fetch(url, deadline=60)
        result = json.loads(resp.content)
        if 200 <= result['http_status'] < 300:
            for response in result['responses']:
                project = {}
                for question in result['questions']:
                    q = question['question']
                    if q in self.questions_list:
                        qid = str(question['id'])
                        project[self.questions_list[q]] = response['answers'][qid] if qid in response['answers'] else None
                if project:
                    p = Project()
                    p.title = project['title']
                    p.description = project['description']
                    p.end_date = datetime.strptime(str(project['end_day'])+'-'+str(project['end_month'])+'-'+str(project['end_year']), "%d-%m-%Y").date() if project['end_day'] and project['end_month'] and project['end_year'] else None
                    p.category = project['category']
                    p.put() #logging.info(p)

app = RestApplication([
    ('/api/projects/add_project', AddProjectHandler),
    ('/api/projects/update_project', UpdateProjectHandler),
    ('/api/projects/fetch_projects', FetchProjectsHandler)
])