import logging

from handlers.rest.rest_application import RestApplication
from handlers import RequestHandler
from google.appengine.ext.webapp import blobstore_handlers
from model.company import Company
from model.user import User

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
        admin = User.get_or_insert(key_name=self['user_id'], parent=c, name=self['name'], isAdmin=True, login_id=self['user_id'])
        return admin

    def post(self):
        image_key = self.read_image()
        c = self.create_company(image_key)
        a = self.create_company_admin(c)
        self.redirect('/member/invite?company_id=' + str(c.key().id()))

app = RestApplication([
    ('/api/startups/add_company', AddCompanyPage)
])