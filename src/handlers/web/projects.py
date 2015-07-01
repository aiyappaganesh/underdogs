import logging
import webapp2
from model.skill import Skill
from handlers.web import WebRequestHandler
from handlers.web.auth import web_login_required
from util.util import convert_string_list_to_dict, get_skills_json
from model.company import Company
from model.project import Project
from model.category import categories
from datetime import datetime
from google.appengine.api.blobstore import blobstore
import operator
from model.ui_models.factories.donut_factory import DonutFactory

DURATION_OPTIONS = [{'name':'Less than 3 months','value':'3'},
                    {'name':'3 to 6 months','value':'6'},
                    {'name':'More than 6 months','value':'12'}]

def get_project(id):
    return Project.get_by_id(id)

class ProjectsRegistrationPage(WebRequestHandler):
    @web_login_required
    def get(self):
        path = 'project_registration.html'
        form_url = blobstore.create_upload_url('/api/projects/add_project')
        template_values = {}
        template_values['duration_options'] = DURATION_OPTIONS
        template_values['categories'] = categories
        template_values['skills'] = get_skills_json()
        template_values['form_url'] = form_url
        self.write(self.get_rendered_html(path, template_values), 200)

class ProjectsEditPage(WebRequestHandler):
    @web_login_required
    def get(self):
        path = 'project_edit.html'
        template_values = {}
        template_values['duration_options'] = DURATION_OPTIONS
        template_values['skills'] = get_skills_json()
        project = {}
        id = int(str(self['project_id']))
        if id:
            p = Project.get_by_id(id)
            project['id'] = id
            project['title'] = p.title
            project['description'] = p.description
            project['skills'] = p.skills
            project['end_date'] = p.end_date.strftime("%Y-%m-%d")
            project['bid'] = p.bid
        template_values['project'] = project
        self.write(self.get_rendered_html(path, template_values), 200)

class ProjectStartupsMatchingPage(WebRequestHandler):
    def get(self):
        path = 'startups_search_results.html'
        project_id = long(self['project_id'])
        project = Project.get_by_id(project_id)
        skills = project.skills
        q = Company.all()
        sorted_companies = {}
        for c in q.fetch(50):
            expertise_dict = convert_string_list_to_dict(c.expertise_avg)
            score = 0.0
            matched_skills = 0.0
            fit = 0.0
            id = c.key().id()
            sorted_companies[id] = {}
            sorted_companies[id]['name'] = c.name
            sorted_companies[id]['influence'] = c.influence_avg
            sorted_companies[id]['skills'] = []
            if skills:
                for skill in skills:
                    skill = str(skill)
                    if skill in expertise_dict:
                        skill_dict = { 'name':skill,'value':float(expertise_dict[skill]) }
                        score += float(expertise_dict[skill])
                        matched_skills += 1
                    else:
                        skill_dict = { 'name':skill,'value':0.0 }
                    sorted_companies[id]['skills'].append(skill_dict)
                score = float(score / len(skills))
                fit = float(matched_skills / len(skills)) if matched_skills > 0.0 else 0.0
            sorted_companies[id]['combined']=score
            sorted_companies[id]['fit']=fit
        donuts = (len(skills) if skills else 0) + 3
        sorted_companies = sorted(sorted_companies.iteritems(), key=lambda (k,v): v['combined'], reverse = True)
        donut_size = 80-(5*donuts)
        score_font_size = 40-(2.25*donuts)
        tooltip_font_size = 14-donuts
        template_values = {'startups' : sorted_companies, 'skills' : skills, 'donut_size' : donut_size, 'score_font_size' : score_font_size, 'tooltip_font_size' : tooltip_font_size}
        self.write(self.get_rendered_html(path, template_values), 200)

class ProjectListPage(WebRequestHandler):
    def get_all_projects(self, order, column):
        q = Project.all()
        if order == 'desc':
            q.order('-' + column)
        elif order == 'asc':
            q.order(column)
        return q.fetch(100)

    def get(self):
        order = self['order'] if self['order'] else 'desc'
        column = self['column'] if self['column'] else 'end_date'
        path = 'list_projects.html'
        projects = self.get_all_projects(order, column)
        project_rows = [projects[i:i+3] for i in range(0, len(projects), 3)]
        logging.info(project_rows)
        template_values = {'project_rows': project_rows, 'order': order, 'column': column}
        self.write(self.get_rendered_html(path, template_values), 200)

class UpcomingProjectDetailsPage(WebRequestHandler):
    def make_json(self, project):
        return {'id': project.id, 'title': project.title, 'image': project.image, 'category': project.category if project.category else categories[0], 'description': project.description, 'skills': project.skills, 'bid': project.bid, 'end_date': project.end_date}

    def get(self):
        project_id = long(self['id'])
        path = 'upcoming_project_details.html'
        template_values = self.make_json(get_project(project_id))
        self.write(self.get_rendered_html(path, template_values), 200)

class CompletedProjectDetailsPage(WebRequestHandler):
    def make_json(self, project):
        return {'title': project.title, 'image': project.image, 'category': project.category if project.category else categories[0], 'description': project.description, 'skills': project.skills, 'bid': project.bid, 'end_date': project.end_date}

    def get(self):
        project_id = long(self['id'])
        path = 'completed_project_details.html'
        template_values = self.make_json(get_project(project_id))
        self.write(self.get_rendered_html(path, template_values), 200)

class ProjectStudyPage(WebRequestHandler):
    def make_json(self, project):
        return {'id': project.id, 'title': project.title, 'image': project.image, 'category': project.category if project.category else categories[0], 'description': project.description, 'skills': project.skills, 'bid': project.bid, 'end_date': project.end_date}

    def get(self):
        project_id = long(self['id'])
        path = 'project_study.html'
        template_values = self.make_json(get_project(project_id))
        template_values['sec_1_bg'] = '/assets/img/study/sec_1_bg.png'
        template_values['sec_1_title'] = 'COMFORT'
        template_values['sec_1_subtitle'] = 'Healthcare with TLC'
        template_values['sec_2_title'] = 'MAKE HEALTHCARE APPEALING FOR THE YOUNG'
        template_values['sec_2_copy'] = \
            "HealthCo (name changed) is one of the largest Health Insurance companies. They wanted to freshen their brand and create an app that would appeal to a younger audience. All the internal efforts to create a new experience for their users had resulted in incremental improvements, but their app still felt very much like a stoic, health insurance app and they didn't see increased engagement among the 20s and 30s demographics.\n\nHealthCo put their project on the Pirate ship to see if the innovate Pirates startups could make a radical difference that would make them instantly more appealing to the 20 and 30 year olds.\nThey laid out two high level goals for the app.\n\n1. Create an app that would allow users to select their doctors based on community review and be able to connect with the doctor in real time.\n\n2. Create a use case for the users to engage with the app to track their health on a regular basis, and not only  when they have an ailment and need to see a doctor."
        template_values['sec_3_bg'] = '/assets/img/study/sec_3_bg.png'
        template_values['sec_3_title'] = 'HAZE'
        template_values['sec_3_copy'] = "After reviewing a short list of startups on the Pirates ship, HealthCo selected Haze.\n\nHaze is a startup in Boston, building a healthcare app to bring transparent pricing to all. HealthCo selected Haze based on Haze's excellent design portfolio and Health domain expertise."
        template_values['sec_3_subtitle'] = "Haze's appeal to HealthCo"
        template_values['founder_image'] = '/assets/img/study/founder.png'
        template_values['founder_name'] = 'Adam Jackson'
        template_values['founder_desc'] = 'Founder, Haze'
        template_values['sec_4_copy'] = "The first concepts that came up when we brainstormed HealthCo's app, were comfort, easy access and fun lifestyle. We all coalesced around the concept of comfort. When one's sick, one really wants some comfort and TLC and not anxiety about doctors, prescriptions and bills. So we branded the app Comfort and then we came up with the tag line \"Healthcare with TLC\". This really sets HealthCo apart from all the other Health Insurance companies, and makes it a friendly app the users would love to use as opposed to a stress inducing Health Insurance app.\n\nIn order to make the app relevant to users on a regular basis, we decided to make the focus of the app a healthy lifestyle, including fitness, nutrition and health tipcs, in addition to connecting with doctors."
        template_values['branding_bg'] = '/assets/img/study/branding_bg.png'
        template_values['branding_title'] = "EVERYONE'S CUP OF TEA"
        template_values['branding_copy_top'] = "We created beautiful imagery of tea, as a symbol of comfort. Everyone has a story of how their mom or their grand-mom gave them lemon tea or chamomile tea to comfort them from a cold or a tummy ache. Before doctors there was tea. So we decided to use beautiful high resolution images of tea throughout the app to give the feeling of comfort and cosiness to users."
        template_values['branding_img'] = '/assets/img/study/comfort.png'
        template_values['branding_copy_bottom'] = "As one of the first tasks of branding the app, we designed the app icon, which would also form the base for the logo. We used the concept of using tea as a symbol for comfort and added some personality to it. Once the logo was set, it coalesced everyone in the team strongly around the concept."
        template_values['donuts'] = DonutFactory.get_donuts(128, 0.8, [('Design', 0.58), ('Dev', 0.75), ('Domain', 0.28)], 'transparent', '#139fe1', '#ffffff')
        template_values['no_navbar_onload'] = True
        template_values['nav_color'] = 'light-nav'
        template_values['unscrolled'] = True
        template_values['app_shots'] = [ 
                {'bg_color': '#397ca0', 'copy': 'A HOME SCREEN AND PROFILE THAT REFLECT THE COMFORT BRAND', 'image': '/assets/img/study/Comfort-ID-Animation.gif'},
                {'bg_color': '#b5a330', 'copy': 'FITNESS AND NUTRITION DATA TO TAKE PRIDE IN', 'image': '/assets/img/study/Comfort-Health-Stats-mockup.gif'},
                {'bg_color': '#589a2d', 'copy': 'FIND THE BEST DOCTORS AS EASY AS FINDING THE BEST RESTAURANTS', 'image': '/assets/img/study/Comfort-Doctor-Animation-2.gif'},
                {'bg_color': '#b04f4f', 'copy': 'GET DIAGNOSIS AND TREATMENT THROUGH TEXT MESSAGE', 'image': '/assets/img/study/Comfort-Interact-Animation.gif'}
        ]
        template_values['sprint_images'] = ['/assets/img/study/sprints_img_1.png', '/assets/img/study/sprints_img_2.png']
        self.write(self.get_rendered_html(path, template_values), 200)

app = webapp2.WSGIApplication(
    [
        ('/projects/registration', ProjectsRegistrationPage),
        ('/projects/edit', ProjectsEditPage),
        ('/projects/list', ProjectListPage),
        ('/projects/fitting_startups', ProjectStartupsMatchingPage),
        ('/projects/upcoming/details', UpcomingProjectDetailsPage),
        ('/projects/completed/details', CompletedProjectDetailsPage),
        ('/projects/study', ProjectStudyPage)
    ]
)