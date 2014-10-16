import logging

from handlers.rest.rest_application import RestApplication
from handlers import RequestHandler
from google.appengine.ext.webapp import blobstore_handlers
from model.company import Company
from model.user import User
from model.company_members import CompanyMember
from gaesessions import get_current_session
from handlers.web.auth import web_login_required

class AddCompanyPage(blobstore_handlers.BlobstoreUploadHandler, RequestHandler):
    def read_image(self):
        image = self.get_uploads("company_image")
        image_key = str(image[0].key()) if image else None
        return image_key

    def create_company(self, image_key):
        c = Company()
        c.name = self['company_name']
        c.email = self['InputEmail']
        c.details = self['InputMessage']
        c.image = image_key
        c.put()
        return c

    def create_company_admin(self, c):
        session = get_current_session()
        CompanyMember(parent=c, is_admin=True, user_id=session['me_email']).put()

    @web_login_required
    def post(self):
        image_key = self.read_image()
        c = self.create_company(image_key)
        adming = self.create_company_admin(c)
        self.redirect('/member/invite?company_id=' + str(c.key().id()))

app = RestApplication([
    ('/api/startups/add_company', AddCompanyPage)
])