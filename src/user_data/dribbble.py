import json
import logging
import urllib2
import math

from google.appengine.api import urlfetch
from google.appengine.ext import deferred
from datetime import date
from model.skill import Skill
from model.experience import Experience

def pull_data(member, third_party_user):
    user_response = json.loads(urlfetch.fetch('https://api.dribbble.com/v1/user?access_token=' + third_party_user.access_token).content)
    shots_url = user_response['shots_url']
    logging.info(third_party_user.access_token)
    shots_response = json.loads(urlfetch.fetch(shots_url + '?access_token=' + third_party_user.access_token).content)
    member.update_design_score(user_response, shots_response)