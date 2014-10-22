level1_skills = {'skills' : [('wd', 'Web Development'), ('gp', 'Programming'), ('md', 'Mobile Development')]}
level2_skills = {'md' : [('ios', 'iOS Programming'), ('and', 'Android Programming')],
				 'wd' : [('gen-wd', 'general')],
				 'gp' : [('gen-gp', 'general')]}
level3_skills = {'gen-wd' : [('c#', 0.25), ('java', 0.25), ('php', 1), ('javascript', 1), ('python', 1), ('scala', 1), ('css', 1), ('web development', 0.5)],
				 'gen-gp' : [('c#', 1), ('java', 1), ('python', 1), ('scala', 1), ('php', 1), ('software development', 0.5), ('software engineering', 0.5), ('javascript', 1), ('objective-c', 1)],
				 'ios' : [('objective-c', 1)],
				 'and' : [('java', 0.25)]}
skills_heirarchy = [level1_skills, level2_skills, level3_skills]

def get_children_for(level_num, key, expertise):
	children = []
	if level_num == 2:
		for (curr_skill_name, weight) in skills_heirarchy[level_num][key]:
			key = curr_skill_name.lower()
			score = 0.0
			if key in expertise:
				score = round(float(expertise[key]) * float(weight), 2)
			children.append({'name' : curr_skill_name, 'score' : score})
	else:
		for (curr_skill_key, curr_skill_name) in skills_heirarchy[level_num][key]:
			curr_json = {}
			curr_json['name'] = curr_skill_name
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
