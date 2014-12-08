import logging
import model

from model.project_members import ProjectMember
from model.project import Project
from model.user import User
from model.skill import Skill
from gaesessions import get_current_session
from model.third_party_login_data import ThirdPartyLoginData
from recaptcha import RecaptchaClient
from google.appengine.api import memcache

RECAPTCHA_PUBLIC_KEY = '6LeA6PwSAAAAAOeT-mnBNsppSoKgygqv1xqChz2s'
RECAPTCHA_PRIVATE_KEY = '6LeA6PwSAAAAAB9Wv1qmmnxnsZySbb8nQwdqUvbv'

recaptcha_client = RecaptchaClient(RECAPTCHA_PRIVATE_KEY, RECAPTCHA_PUBLIC_KEY, recaptcha_options={'theme':'clean'})

registration_breadcrumbs = [('Get started', 'Tell us about your startup!'),
                            ('Invite team members', 'Build your team'),
                            ('Give us access to your data', 'Help us learn more about you')]

separator = '::'

def is_user_in_db(email):
    if not is_user_in_memcache(email):
        if not User.get_by_key_name(email):
            return False
        add_user_to_memcache(email)
    return True

def flush_from_memcache(email):
    users_in_memcache = memcache.get('users')
    if users_in_memcache and email in users_in_memcache:
        users_in_memcache.remove(email)
        memcache.set('users', users_in_memcache)

def is_user_in_memcache(email):
    users_in_memcache = memcache.get('users')
    if not users_in_memcache or not len(users_in_memcache) > 0 or not email in users_in_memcache:
        return False
    return True

def add_user_to_memcache(email):
    users_in_memcache = memcache.get('users')
    if not users_in_memcache:
        users_in_memcache = [email]
    else:
        users_in_memcache.append(email)
    memcache.set('users', users_in_memcache)

def isAdminAccess(req_handler):
    session = get_current_session()
    admin_id = session['me_email']
    company_id = req_handler['company_id']
    c =  model.company.Company.get_by_id(int(company_id))
    from model.company_members import CompanyMember
    company_member = CompanyMember.all().ancestor(c).filter('user_id', admin_id).get()
    return True if (company_member and company_member.is_admin) else False

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

def get_company_id_from_session():
    session = get_current_session()
    return int(session['company_id']) if 'company_id' in session else None

def get_captcha_markup():
    was_previous_solution_incorrect=False
    session = get_current_session()
    if session and 'captcha_error' in session:
        was_previous_solution_incorrect=True
        session.pop('captcha_error')
    return recaptcha_client.get_challenge_markup(was_previous_solution_incorrect=was_previous_solution_incorrect, use_ssl=True)

def validate_captcha(solution, challenge, remote_ip):
    return recaptcha_client.is_solution_correct(solution,challenge,remote_ip)

def get_skills_json():
    q = Skill.all()
    skills = q.fetch(100)
    skill_options = []
    for skill in skills:
        skill_option = {}
        skill_option['name'] = skill.name
        skill_option['value'] = skill.name
        skill_options.append(skill_option)
    return skill_options