import logging

from model.company import Company
from model.user import User

def isAdminAccess(req_handler):
    admin_id = req_handler['admin_id']
    company_id = req_handler['company_id']
    c = Company.get_by_id(int(company_id))
    a = User.get_by_key_name(admin_id, parent=c)
    if a:
        return True
    return False