level1_skills = {'skills' : [('wd', 'Web Development'), ('gp', 'General Programming'), ('md', 'Mobile Development')]}
level2_skills = {'md' : [('ios', 'iOS Programming'), ('and', 'Android Programming')],
				 'wd' : [('gen-wd', 'general')],
				 'gp' : [('gen-gp', 'general')]}
level3_skills = {'gen-wd' : [('c#', 'c#', 0.25), ('java', 'Java', 0.25), ('php', 'PHP', 1), ('js', 'JavaScript', 1), ('py', 'Python', 1), ('scala', 'Scala', 1), ('css', 'CSS', 1), ('wd', 'Web development', 0.5)],
				 'gen-gp' : [('c#', 'c#', 1), ('java', 'java', 1), ('py', 'Python', 1), ('scala', 'scala', 1), ('php', 'PHP', 1), ('sd', 'Software Development', 0.5), ('swe', 'Software Engineering', 0.5), ('js', 'JavaScript', 1), ('oc', 'objective-c', 1)],
				 'ios' : [('oc', 'objective-c', 1)],
				 'and' : [('java', 'java', 1)]}
skills_heirarchy = [level1_skills, level2_skills, level3_skills]

def get_children_for(level_num, key):
	children = []
	if level_num == 2:
		for (curr_skill_key, curr_skill_name, weight) in skills_heirarchy[level_num][key]:
			children.append({'name' : curr_skill_name, 'weight' : weight})
	else:
		for (curr_skill_key, curr_skill_name) in skills_heirarchy[level_num][key]:
			curr_json = {}
			curr_json['name'] = curr_skill_name
			curr_json['children'] = get_children_for(level_num + 1, curr_skill_key)
			children.append(curr_json)
	return children

def get_skills_json():
	skills_json = {'name':'skills', 'children':[]}
	skills_json['children'] = get_children_for(0, 'skills')
	return skills_json