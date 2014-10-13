from google.appengine.ext import db
import logging

class User(db.Model):
    name = db.StringProperty(indexed=False)
    password = db.StringProperty(indexed=False)
    influence = db.FloatProperty(indexed=False)
    expertise = db.StringListProperty(indexed=False)
    isAdmin = db.BooleanProperty()

    def update_score(self, influence_score):
        if not self.influence:
            self.influence = (1.0/3.0) * influence_score
        else:
            self.influence = self.influence + ((1.0/3.0) * influence_score)
        self.put()

    def update_expertise_score(self, expertise_score):
        if not self.expertise:
            skills = []
            for skill, score in expertise_score.iteritems():
                skills.append(skill + " : " + str(score))
            self.expertise = skills
        else:
            updated_expertise = {}
            saved_expertise = {}
            for expertise in self.expertise:
                skill, score = expertise.split(' : ')
                saved_expertise[skill] = score
            saved_keys = set(saved_expertise.keys())
            new_keys = set(expertise_score.keys())
            collisions = saved_keys.intersection(new_keys)
            all_keys = saved_keys.union(new_keys)
            for key in all_keys:
                if key in collisions:
                    logging.info('>>>> Collision for: ' + key)
                    saved_score = float(saved_expertise[key])
                    new_score = float(expertise_score[key])
                    logging.info(str(saved_score) + " .... " + str(new_score))
                    norm_score = (0.5 * saved_score) + (0.5 * new_score)
                    updated_expertise[key] = norm_score
                elif key in saved_keys:
                    updated_expertise[key] = saved_expertise[key]
                else:
                    updated_expertise[key] = expertise_score[key]
            self.expertise = []
            for skill, score in updated_expertise.iteritems():
                self.expertise.append(skill + " : " + str(score))
        self.put()