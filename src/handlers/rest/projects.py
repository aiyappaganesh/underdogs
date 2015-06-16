import logging

from google.appengine.ext.webapp import blobstore_handlers
from handlers.rest.rest_application import RestApplication
from handlers import RequestHandler
from handlers.web.auth import web_login_required
from gaesessions import get_current_session
from model.project import Project
from model.project_members import ProjectMember
from model.user import User
from datetime import date, datetime

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

    def create_project_admin(self, p):
        session = get_current_session()
        ProjectMember(parent=p, user_id = session['me_email'], is_admin=True).put()

    @web_login_required
    def post(self):
        image_key = self.read_image()
        p = self.create_project(image_key)
        self.create_project_admin(p)
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

app = RestApplication([
    ('/api/projects/add_project', AddProjectHandler),
    ('/api/projects/update_project', UpdateProjectHandler)
])