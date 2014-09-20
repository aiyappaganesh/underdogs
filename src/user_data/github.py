import json
import logging
import urllib2
import math

from google.appengine.api import urlfetch
from google.appengine.ext import deferred

import github_config as github

def pull_data(user, third_party_user):
    profile = json.loads(urlfetch.fetch(github.USER_URL%third_party_user.access_token).content)
    repos = json.loads(urlfetch.fetch(profile['repos_url'] + '?access_token=' + third_party_user.access_token).content)
    gists = json.loads(urlfetch.fetch(profile['gists_url'].replace('{/gist_id}','') + '?access_token=' + third_party_user.access_token).content)

    followers = profile['followers']
    stars = 0
    forks = 0
    contributors = 0
    comments = 0
    for repo in repos:
        stars += repo['stargazers_count']
        forks += repo['forks_count']
        contributors += len(json.loads(urlfetch.fetch(repo['contributors_url'] + '?access_token=' + third_party_user.access_token).content)) - 1
    for gist in gists:
        comments += int(gist['comments'])

    influence_raw = (followers * 4) + (forks * 2) + (stars + 2) + (contributors * 1.5) + (comments * 0.5)
    influence = math.log(influence_raw)/10
    influence_score = influence if influence < 1.0 else 1.0
    user.update_score(influence_score)
