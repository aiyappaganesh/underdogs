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
        c.hello = self['hello']
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
        self.create_company_admin(c)
        self.redirect('/member/invite?company_id=' + str(c.key().id()))


class UpdateCompanyPage(blobstore_handlers.BlobstoreUploadHandler, RequestHandler):
    def read_image(self):
        image = self.get_uploads("company_image")
        image_key = self['image_key']
        if image:
            image_key = str(image[0].key())
        return image_key

    def update_company(self):
        company_id = int(str(self['company_id']))
        c = Company.get_by_id(company_id)
        if c:
            c.name = self['company_name']
            c.email = self['InputEmail']
            c.details = self['InputMessage']
            c.hello = self['hello']
            c.image = self.read_image()
            c.put()

    @web_login_required
    def post(self):
        self.update_company()
        self.redirect('/member/companies/dashboard')

app = RestApplication([
    ('/api/startups/add_company', AddCompanyPage),
    ('/api/startups/update_company', UpdateCompanyPage)
])