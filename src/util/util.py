import logging

from model.company import Company
from model.company_members import CompanyMember
from model.project import Project
from model.user import User
from gaesessions import get_current_session

registration_breadcrumbs = [('Get started', 'Tell us about your startup!'),
                            ('Invite team members', 'Build your team'),
                            ('Give us access to your data', 'Help us learn more about you')]

separator = '::'

def isAdminAccess(req_handler):
    session = get_current_session()
    admin_id = session['me_email']
    company_id = req_handler['company_id']
    c = Company.get_by_id(int(company_id))
    if c and c.admin_id == admin_id:
        return True
    return False

def get_user_parents(parent_type):
    session = get_current_session()
    user_id = session['me_id']
    member_objs = User.all().filter('login_id =',user_id).fetch(100)
    user_parents = []
    for member_obj in member_objs:
        parent = member_obj.parent()
        if type(parent) is parent_type:
            user_parents.append({'parent':parent,'member':member_obj})
    return user_parents

def get_user_projects():
    return get_user_parents(Project)

def get_user_companies():
    session = get_current_session()
    user_id = session['me_email']
    member_objs = CompanyMember.all().filter('user_id =',user_id).fetch(100)
    user_parents = []
    for member_obj in member_objs:
        parent = member_obj.parent()
        if type(parent) is Company:
            user_parents.append({'parent':parent,'member':member_obj})
    return user_parents

def convert_string_list_to_dict(str_list):
    ret_val = {}
    for param in str_list:
        key, value = param.split(' : ')
        ret_val[key] = value
    return ret_val

def get_user(email):
    return User.get_by_key_name(email)