import urllib
import json
from handlers.rest.rest_application import RestApplication
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from handlers import RequestHandler
from util.util import validate_captcha

class ImageDownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, picture_key):
        if picture_key:
            resource = str(urllib.unquote(picture_key))
            blob_info = blobstore.BlobInfo.get(resource)
            self.send_blob(blob_info)
            return

class ValidateCaptchaHandler(RequestHandler):
    def post(self):
        challenge = self['recaptcha_challenge_field']
        solution = self['recaptcha_response_field']
        remote_ip = self.request.remote_addr
        is_solution_correct = validate_captcha(solution, challenge, remote_ip)
        self.write(json.dumps({'solution_correct': is_solution_correct}), 200, 'application/json')

app = RestApplication([("/api/common/download_image/([^/]+)",ImageDownloadHandler),
                       ("/api/common/validate_captcha",ValidateCaptchaHandler)])