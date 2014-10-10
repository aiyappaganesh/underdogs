import urllib
from handlers.rest.rest_application import RestApplication
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

class ImageDownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, picture_key):
        if picture_key:
            resource = str(urllib.unquote(picture_key))
            blob_info = blobstore.BlobInfo.get(resource)
            self.send_blob(blob_info)
            return

app = RestApplication([("/api/common/download_image/([^/]+)",ImageDownloadHandler)])