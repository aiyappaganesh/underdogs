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
    response = json.loads(urlfetch.fetch('https://api.dribbble.com/v1/shots?access_token=' + third_party_user.access_token).content)
    logging.info(response)
