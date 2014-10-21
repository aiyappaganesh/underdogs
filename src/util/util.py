import logging
import model

from model.project_members import ProjectMember
from model.project import Project
from model.user import User
from gaesessions import get_current_session
from model.third_party_login_data import ThirdPartyLoginData

registration_breadcrumbs = [('Get started', 'Tell us about your startup!'),
                            ('Invite team members', 'Build your team'),
                            ('Give us access to your data', 'Help us learn more about you')]

separator = '::'

def isAdminAccess(req_handler):
    session = get_current_session()
    admin_id = session['me_email']
    company_id = req_handler['company_id']
    c =  model.company.Company.get_by_id(int(company_id))
    cms = model.company_members.CompanyMember.all().ancestor(c)
    for cm in cms.fetch(1000):
        if cm.user_id == admin_id and cm.is_admin:
            return True
        elif cm.user_id == admin_id:
            return False
    return False

def get_user_parents(member_type, parent_type):
    session = get_current_session()
    user_id = session['me_email']
    member_objs = member_type.all().filter('user_id =',user_id).fetch(100)
    user_parents = []
    for member_obj in member_objs:
        parent = member_obj.parent()
        if type(parent) is parent_type:
            user_parents.append({'parent':parent,'member':member_obj})
    return user_parents

def get_user_projects():
    return get_user_parents(ProjectMember, Project)

def get_user_companies():
    return get_user_parents(model.company_members.CompanyMember, model.company.Company)

def convert_string_list_to_dict(str_list, separator = ' : '):
    ret_val = {}
    for param in str_list:
        key, value = param.split(separator)
        ret_val[key] = value
    return ret_val

def get_user(email):
    return User.get_by_key_name(email)

def get_user_tp_ids(email):
    tp_ids = {}
    tplds = ThirdPartyLoginData.all().filter('parent_id =',email).fetch(10)
    for tpld in tplds:
        if tpld.network_name == 'facebook':
            tp_ids['FB'] = tpld.key().name()
        elif tpld.network_name == 'linkedin':
            tp_ids['LI'] = tpld.key().name()
        elif tpld.network_name == 'twitter':
            tp_ids['TW'] = tpld.key().name()
    return tp_ids

def get_redirect_url_from_session():
    session = get_current_session()
    return session['redirect_url'] if 'redirect_url' in session else '/'