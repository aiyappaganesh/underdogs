import json
import logging
import urllib2
import math

from google.appengine.api import urlfetch
from google.appengine.ext import deferred

from model.skill import Skill

import linkedin_config as linkedin

def pull_data(member, third_party_user):
    response = json.loads(urlfetch.fetch('https://api.angel.co/1/me?access_token=' + third_party_user.access_token).content)
    followers = response['follower_count'] if 'follower_count' in response else 0
    skills = [skill['name'] for skill in response['skills']] if 'skills' in response and len(response['skills']) > 0 else []

    influence_raw = (10 * followers)
    influence = math.log(influence_raw) / 10.0

    expertise = {}
    for skill in skills:
        key = skill.lower()
        expertise[key] = '0.5'
        Skill.get_or_insert(key_name=key, name=key)

    influence_score = influence if influence < 1.0 else 1.0
    member.update_score(influence_score)
    member.update_expertise_score(expertise)