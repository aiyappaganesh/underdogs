level1_skills = {'skills' : [('wd', 'Web Development'), ('gp', 'Programming'), ('md', 'Mobile Development'), ('mg', 'Management')]}
level2_skills = {'md' : [('ios', 'iOS Programming'), ('and', 'Android Programming')],
				 'wd' : [('gen-wd', 'general'), ('java-wd', 'java'), ('ms-wd', 'microsoft')],
				 'mg' : [('gen-mg', 'general')],
				 'gp' : [('gen-gp', 'general'), ('db-gp', 'database'), ('tools-gp', 'tools'), ('cloud-gp', 'cloud')]}
level3_skills = {'gen-wd' : [('html', 1), ('web services', 1), ('xml', 1), ('perl', 1), ('php', 1), ('javascript', 1), ('python', 1), ('css', 1), ('web development', 0.25)],
				 'gen-gp' : [('c#', 1), ('java', 1), ('python', 1), ('scala', 1), ('php', 1), ('software development', 0.25), ('software engineering', 0.25), ('javascript', 1), ('objective-c', 1)],
				 'ios' : [('objective-c', 1)],
				 'and' : [('java', 0.25)],
				 'java-wd': [('java enterprise edition', 1), ('jsp', 1), ('java', 1), ('scala', 1)],
				 'ms-wd': [('c#', 1)],
				 'db-gp': [('sql', 1), ('mysql', 1)],
				 'tools-gp': [('eclipse', 1), ('subversion', 1)],
				 'cloud-gp': [('google appengine', 1)],
				 'gen-mg': [('soa', 1), ('agile methodologies', 1), ('software project management', 1), ('program management', 1), ('requirements analysis', 1)]}
skills_heirarchy = [level1_skills, level2_skills, level3_skills]

def get_children_for(level_num, key, expertise):
	children = []
	if level_num == 2:
		for (curr_skill_name, weight) in skills_heirarchy[level_num][key]:
			key = curr_skill_name.lower()
			score = 0.0
			if key in expertise:
				score = round(float(expertise[key]) * float(weight), 2)
			children.append({'name' : curr_skill_name, 'score' : score, 'key' : curr_skill_name})
	else:
		for (curr_skill_key, curr_skill_name) in skills_heirarchy[level_num][key]:
			curr_json = {}
			curr_json['name'] = curr_skill_name
			curr_json['key'] = curr_skill_key
			curr_json['children'] = get_children_for(level_num + 1, curr_skill_key, expertise)
			score = 0.0
			for child in curr_json['children']:
				score += child['score'] * (1.0 / len(curr_json['children']))
			curr_json['score'] = round(score, 2)
			children.append(curr_json)
	return children

def get_skills_json(expertise):
	skills_json = {'name':'skills', 'children':[]}
	skills_json['children'] = get_children_for(0, 'skills', expertise)
	return skills_json

def get_skills_parents_map():
	curr_level_dict = {}
	for parent_key, curr_level_skills in skills_heirarchy[2].iteritems():
		for (skill_key, skill_name, weight) in curr_level_skills:
			skill_name = skill_name.lower()
			if skill_name not in curr_level_dict:
				curr_level_dict[skill_name] = []
			curr_level_dict[skill_name].append((parent_key, weight))
	return curr_level_dict
