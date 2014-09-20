import json
import logging
import urllib2
import math

from google.appengine.api import urlfetch
from google.appengine.ext import deferred

import linkedin_config as linkedin

def pull_data(user, third_party_user):
    response = json.loads(urlfetch.fetch(linkedin.PROFILE_URL%('num-connections,num-recommenders,publications,patents,skills,positions,educations,certifications', third_party_user.access_token)).content)
    connections = response['numConnections']
    recommenders = response['numRecommenders']
    patents = response['patents']['_total'] if 'patents' in response else None
    publications = response['publications']['_total'] if 'publications' in response else None
    skills = [skill['skill']['name'] for skill in response['skills']['values']] if 'skills' in response and response['skills']['_total'] > 0 else None

    influence_raw = (4 * connections) + (4 * recommenders) + (1 * patents) + (1 * publications)
    influence = math.log(influence_raw)/10.0
    expertise = ''
    for skill in skills:
    	expertise = expertise + skill +':0.5,'
    
    user.influence = influence if influence < 1.0 else 1.0
    user.expertise = expertise
    user.put()
