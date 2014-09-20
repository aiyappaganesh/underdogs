from google.appengine.ext import db

class User(db.Model):
   	name = db.StringProperty(indexed=False)
   	influence = db.FloatProperty(indexed=False)
	expertise = db.StringProperty(indexed=False)

	def update_score(self, influence_score):
	    if not self.influence:
	        self.influence = influence_score
	    else:
	        self.influence = (0.5 * self.influence) + (0.5 * influence_score)
	    self.put()

    def update_expertise_score(self, expertise_score):
        if not self.expertise:
            self.expertise = str(expertise_score)
        else:
            self.expertise += str(expertise_score)
        self.put()
