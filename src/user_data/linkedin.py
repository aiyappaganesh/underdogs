import json
import logging
import urllib2
import math

from google.appengine.api import urlfetch
from google.appengine.ext import deferred

from model.skill import Skill
from model.experience import Experience
from model.education import Education
from model.user import User
from datetime import date

import linkedin_config as linkedin

def pull_data(member, third_party_user):
    response = json.loads(urlfetch.fetch(linkedin.PROFILE_URL%('num-connections,num-recommenders,publications,patents,skills,positions,educations,certifications', third_party_user.access_token)).content)
    connections = response['numConnections'] if 'numConnections' in response else 0
    recommenders = response['numRecommenders'] if 'numRecommenders' in response else 0
    patents = response['patents']['_total'] if 'patents' in response else 0
    publications = response['publications']['_total'] if 'publications' in response else 0
    skills = [skill['skill']['name'] for skill in response['skills']['values']] if 'skills' in response and response['skills']['_total'] > 0 else None
    user = User.get_by_key_name(member.user_id)

    if 'positions' in response and response['positions']['_total'] > 0:
        for position in response['positions']['values']:
            title = position['title'] if 'title' in position else ''
            summary = position['summary'] if 'summary' in position else ''
            startDate = None
            if 'startDate' in position:
                startDate = date(position['startDate']['year'], position['startDate']['month'], 1)
            endDate = None
            if 'endDate' in position:
                endDate = date(position['endDate']['year'], position['endDate']['month'], 1)
            company = position['company']['name'] if 'company' in position and 'name' in position['company'] else ''
            key_name = str(company)+str(startDate)
            experience = Experience.get_or_insert(key_name=key_name, parent=user)
            experience.company = company
            experience.title = title
            experience.summary = summary
            experience.start = startDate
            experience.end = endDate
            experience.put()

    if 'educations' in response and response['educations']['_total'] > 0:
        for education in response['educations']['values']:
            school = education['schoolName'] if 'schoolName' in education else ''
            field = education['fieldOfStudy'] if 'fieldOfStudy' in education else ''
            degree = education['degree'] if 'degree' in education else ''
            start = None
            if 'startDate' in education:
                start = date(education['startDate']['year'], 1, 1)
            end = None
            if 'endDate' in education:
                end = date(education['endDate']['year'], 1, 1)
            key_name = str(school)+str(start)
            edu = Education.get_or_insert(key_name=key_name, parent=user)
            edu.school = school
            edu.field = field
            edu.degree = degree
            edu.start = start
            edu.end = end
            edu.put()

    influence_raw = (4 * connections) + (4 * recommenders) + (1 * patents) + (1 * publications)
    influence = math.log(influence_raw)/10.0
    expertise = {}
    for skill in skills:
        key = skill.lower()
    	expertise[key] = '0.5'
        Skill.get_or_insert(key_name=key, name=key)
    
    influence_score = influence if influence < 1.0 else 1.0
    member.update_score(influence_score)
    member.update_expertise_score(expertise)

