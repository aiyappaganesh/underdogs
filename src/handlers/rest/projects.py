import logging

from handlers.rest.rest_application import RestApplication
from handlers import RequestHandler
from handlers.web.auth import web_login_required
from gaesessions import get_current_session
from model.project import Project
from model.user import User
from datetime import date, datetime

class AddProjectHandler(RequestHandler):
    def create_project(self):
        p = Project()
        p.title = self['project_title']
        p.description = self['description']
        p.skills = self.get_all('skills')
        p.end_date = datetime.strptime(str(self['project_end_date']), "%Y-%m-%d").date()
        p.bid = self['bid']
        p.put()
        return p

    def create_project_admin(self, project):
        session = get_current_session()
        admin = User.get_or_insert(key_name=session['me_id'], 
                                   parent=project, 
                                   name=session['me_name'], 
                                   isAdmin=True, 
                                   login_id=session['me_id'])
        return admin

    @web_login_required
    def post(self):
        p = self.create_project()
        a = self.create_project_admin(p)
        self.redirect('/startups/search/criteria')

app = RestApplication([
    ('/api/projects/add_project', AddProjectHandler)
])