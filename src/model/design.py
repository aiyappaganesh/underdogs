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

    @classmethod
    def aggregate_data_for(self, company):
        query = Design.all().ancestor(company)
        response = {'live_apps':0,'shots':0,'likes':0,'followers':0,'shot_urls':[]}
        for member in query:
            response['live_apps'] += member.live_apps
            response['shots'] += member.shots
            response['likes'] += member.likes
            response['followers'] += member.followers
            response['shot_urls'].extend(member.shot_urls)
        return response