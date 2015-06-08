from google.appengine.ext import db
from util.util import convert_string_list_to_dict
from model.design import Design
import logging

class CompanyMember(db.Model):
    user_id = db.StringProperty(indexed=True)
    is_admin = db.BooleanProperty(indexed=False)
    influence = db.FloatProperty(indexed=False)
    expertise = db.StringListProperty(indexed=False)

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
                    saved_score = float(saved_expertise[key])
                    new_score = float(expertise_score[key])
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

    def update_design_score(self, dribbble_user, shots_data):
        design = Design(parent=self.parent(), key_name=self.user_id)
        design.update_score(shots_data, dribbble_user['followers_count'])
        design.put()
        self.get_design_score()

    def get_design_score(self):
        logging.info(Design.aggregate_data_for(self.parent()))
        return Design.aggregate_data_for(self.parent())

    def get_expertise(self):
        return convert_string_list_to_dict(self.expertise)