import logging

from handlers.rest.rest_application import RestApplication
from handlers import RequestHandler
from handlers.web.auth import web_login_required
from gaesessions import get_current_session
from model.project import Project
from model.project_members import ProjectMember
from model.user import User
from datetime import date, datetime

class AddProjectHandler(RequestHandler):
    def create_project(self):
        p = Project()
        p.title = self['project_title']
        p.description = self['description']
        p.skills = self['project_skills'].split(',') if self['project_skills'] else []
        p.end_date = datetime.strptime(str(self['project_end_date']), "%Y-%m-%d").date()
        p.bid = float(self['project_bid'])
        p.put()
        return p

    def create_project_admin(self, p):
        session = get_current_session()
        ProjectMember(parent=p, user_id = session['me_email'], is_admin=True).put()

    @web_login_required
    def post(self):
        p = self.create_project()
        self.create_project_admin(p)
        self.redirect('/startups/search/criteria')

app = RestApplication([
    ('/api/projects/add_project', AddProjectHandler)
])