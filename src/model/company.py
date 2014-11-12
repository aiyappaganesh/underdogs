from google.appengine.ext import db
from util.util import convert_string_list_to_dict

class Company(db.Model):
    name = db.StringProperty(indexed=False)
    website = db.StringProperty(indexed=False)
    hello = db.StringProperty(indexed=False)
    profile = db.StringProperty(indexed=False)
    image = db.StringProperty(indexed=False)
    tags = db.StringProperty(indexed=False)
    influence_avg = db.FloatProperty(indexed=False)
    expertise_avg = db.StringListProperty(indexed=False)

    def get_expertise_avg(self):
    	return convert_string_list_to_dict(self.expertise_avg)