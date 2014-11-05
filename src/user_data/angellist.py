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
    response = json.loads(urlfetch.fetch('https://api.angel.co/1/me?access_token=' + third_party_user.access_token).content)
    followers = response['follower_count'] if 'follower_count' in response else 0
    skills = [skill['name'] for skill in response['skills']] if 'skills' in response and len(response['skills']) > 0 else []

    influence_raw = (10 * followers)
    influence = math.log(influence_raw) / 10.0 if influence_raw > 0 else 0.0

    expertise = {}
    for skill in skills:
        key = skill.lower()
        expertise[key] = '0.5'
        Skill.get_or_insert(key_name=key, name=key)

    influence_score = influence if influence < 1.0 else 1.0
    member.update_score(influence_score)
    member.update_expertise_score(expertise)


def pull_profile_data(third_party_profile_data):
    response = json.loads(urlfetch.fetch('https://api.angel.co/1/me?access_token=' + third_party_profile_data.access_token).content)
    if 'startup_roles' in response and response['total'] > 0:
        for role in response['startup_roles']:
            title = role['title'] if 'role' in role else ''
            summary = role['startup']['high_concept'] if 'startup' in role and 'high_concept' in role['startup'] else ''
            start = None
            if 'started_at' in role:
                start = date(role['started_at'])
            end = None
            if 'ended_at' in role:
                end = date(role['ended_at'])
            company = role['startup']['name'] if 'startup' in role and 'name' in role['startup'] else ''
            key_name = str(company)+str(start)
            experience = Experience.get_or_insert(key_name=key_name, parent=third_party_profile_data)
            experience.company = company
            experience.title = title
            experience.summary = summary
            experience.start = start
            experience.end = end
            experience.put()