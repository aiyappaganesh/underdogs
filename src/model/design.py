from google.appengine.ext import db
import logging

class Design(db.Model):
    live_apps = db.IntegerProperty(indexed=False)
    shots = db.IntegerProperty(indexed=False)
    likes = db.IntegerProperty(indexed=False)
    followers = db.IntegerProperty(indexed=False)
    shot_urls = db.StringListProperty(indexed=False)

    def update_score(self, dribbble_response, followers_count):
        self.shots = int(len(dribbble_response))
        self.likes = 0
        for shot in dribbble_response:
        	self.likes += int(shot['likes_count'])
        	self.shot_urls.append(shot['images']['normal'])
        self.followers = followers_count
        self.live_apps = 3

    def aggregate_data_for(self, company):
    	Design.all().ancestor(company)