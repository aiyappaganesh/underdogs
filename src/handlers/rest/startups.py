from handlers.rest.rest_application import RestApplication
from handlers import RequestHandler
from google.appengine.ext.webapp import blobstore_handlers
from model.company import Company

class AddCompanyPage(blobstore_handlers.BlobstoreUploadHandler, RequestHandler):
    def post(self):
        image = self.get_uploads("company_image")
        image_key = str(image[0].key()) if image else None
        c = Company()
        c.name = self['InputName']
        c.email = self['InputEmail']
        c.details = self['InputMessage']
        c.image = image_key
        c.put()
        self.redirect('/member/list?company_id=' + str(c.key().id()))

app = RestApplication([
    ('/api/startups/add_company', AddCompanyPage)
])