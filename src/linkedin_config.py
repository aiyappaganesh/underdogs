RESPONSE_TYPE = 'code'
CLIENT_ID = '75roiql0j3mfv4'
CLIENT_SECRET ='LeW9ypga1UdUo5Ix'
AUTHORIZATION_URL = 'https://www.linkedin.com/uas/oauth2/authorization'
SCOPE = 'r_fullprofile'
STATE = 'karnatakanammarajya'
REDIRECT_URI = 'http://minyattra.appspot.com/users/handle_linkedin_auth'
ACCESS_TOKEN_URL = 'https://www.linkedin.com/uas/oauth2/accessToken'
GRANT_TYPE = 'authorization_code'
PROFILE_URL = 'https://api.linkedin.com/v1/people/~:(%s)?format=json&oauth2_access_token=%s'



config  = {
'client_id': '750e8n3ri1ji6s',
'client_secret': 'TVFJEIv1GEXFL5Na',
'auth_url': 'https://www.linkedin.com/uas/oauth2/authorization',
'token_url': 'https://www.linkedin.com/uas/oauth2/accessToken',
'scope': 'r_fullprofile',
'redirect_url': 'http://minyattra.appspot.com/users/data/linkedin/update_success',
'response_type': 'code'
}

profile_config  = config
profile_config['redirect_url'] = 'http://minyattra.appspot.com/users/profile/linkedin/update_success'
