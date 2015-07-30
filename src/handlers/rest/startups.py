import logging
import re
from handlers.rest.rest_application import RestApplication
from handlers import RequestHandler
from google.appengine.ext.webapp import blobstore_handlers
from model.company import Company
from model.user import User
from model.company_members import CompanyMember
from model.registration_queue import RegistrationQueue
from gaesessions import get_current_session
from handlers.web.auth import web_login_required
from util.util import isAdminAccess


class AddCompanyPage(blobstore_handlers.BlobstoreUploadHandler, RequestHandler):
    def read_image(self):
        image = self.get_uploads("company_image")
        image_key = str(image[0].key()) if image else None
        return image_key

    def create_company(self, image_key):
        c = Company()
        c.name = self['company_name']
        c.website = self['website']
        c.profile = self['profile']
        c.hello = self['hello']
        tags = re.findall(r"[\w']+", str(self['tags']))
        c.tags = tags[0:3] if len(tags)>3 else tags
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
            c.website = self['website']
            c.profile = self['profile']
            c.hello = self['hello']
            tags = re.findall(r"[\w']+", str(self['tags']))
            c.tags = tags[0:3] if len(tags)>3 else tags
            image = self.read_image()
            if image:
                c.image = image
            c.put()

    @web_login_required
    def post(self):
        if not isAdminAccess(self):
            return
        self.update_company()
        self.redirect('/member/companies/dashboard')

class QueueCompanyPage(RequestHandler):
    def post(self):
        name = self['name']
        email = self['email']
        RegistrationQueue(key_name=email, name=name).put()
        self.redirect('/startups/new_listing')

app = RestApplication([
    ('/api/startups/add_company', AddCompanyPage),
    ('/api/startups/queue_company', QueueCompanyPage),
    ('/api/startups/update_company', UpdateCompanyPage)
])