import urlparse

def write(response,text=None, status=None, content_type = None):
    response.out.write(text)
    if status:
        response.set_status(status)
    if content_type:
        response.headers['Content-type'] = content_type

def is_absolute(uri):
    res =  urlparse.urlparse(uri)
    return res.scheme

def baseuri(uri):
    assert is_absolute(uri)
    res =  urlparse.urlparse(uri)
    return uri.rsplit(res.path)[0]