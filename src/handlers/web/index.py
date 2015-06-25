import webapp2
from handlers.web import WebRequestHandler
from model.company import Company
from cities_mapping import cities_map
from model.ui_models.donut import Donut
from model.ui_models.landing_page_team_member import TeamMember
from model.ui_models.factories.donut_factory import DonutFactory

def get_team_members():
    members = [("Designer", '/assets/img/landing/slide-3-1.png'),
               ("Back end Developer", '/assets/img/landing/slide-3-2.png'),
               ("Mobile Developer", '/assets/img/landing/slide-3-3.png')]
    ret_val = []
    for member in members:
        m = TeamMember(member[0], member[1])
        ret_val.append(m)
    return ret_val

def get_template_values_for_landing():
    template_values = {}
    template_values['team_members'] = get_team_members()
    template_values['donuts'] = DonutFactory.get_donuts(128, 0.8, [('Design', 0.58), ('Dev', 0.75), ('Domain', 0.28)], '#ffffff', '#139fe1', '#333333')
    template_values['steve_img'] = '/assets/img/landing/steve.png'
    template_values['startups_copy_big_1'] = 'Browse through the best startups'
    template_values['startups_copy_big_2'] = 'Select your favorite startup to build your app'
    template_values['startups_copy_medium'] = "Startup Color Door's appeal to a Fortune 500 bank looking to build a new retail banking app"
    template_values['carousel_2_1_img_1'] = '/assets/img/landing/design_1.png'
    template_values['carousel_2_1_img_2'] = '/assets/img/landing/design_2.png'
    template_values['carousel_2_1_copy_big'] = 'The entire Design community of Pirates contributes\nto ensure your app has the best user experience'
    template_values['carousel_2_1_des_1_copy_1'] = 'Adam Jackson, Designer, Haze'
    template_values['carousel_2_1_des_1_copy_2'] = 'Try making the icons smaller and giving more whitespace'
    template_values['carousel_2_1_des_2_copy_1'] = 'Hailey Peterson, Designer, For Me'
    template_values['carousel_2_1_des_2_copy_2'] = 'Maybe change the preferences to action sheets'
    template_values['carousel_2_2_img_1'] = '/assets/img/landing/dev_1.png'
    template_values['carousel_2_2_img_2'] = '/assets/img/landing/dev_2.png'
    template_values['carousel_2_2_copy_big'] = 'Pirates developers help each to\nsolve problems and write the best code'
    template_values['carousel_2_2_des_1_copy_1'] = 'Eric Erickson, iOS Developer, Beagles Labs'
    template_values['carousel_2_2_des_1_copy_2'] = 'Set "Clip Subviews" to true for the corner radius to show'
    template_values['carousel_2_2_des_2_copy_1'] = 'Irea Jackson, Python Developer, Looking Glass'
    template_values['carousel_2_2_des_2_copy_2'] = 'Have you created an __init.py__ in the directory?'
    template_values['track_img_1'] = '/assets/img/landing/track_1.gif' #'http://winnerhun.uw.hu/vigyorpofa.gif'
    template_values['track_img_2'] = '/assets/img/landing/track_2.png'
    template_values['track_copy_1'] = 'PARTICIPATE'
    template_values['track_copy_2'] = 'TRACK REAL TIME'
    template_values['no_navbar_onload'] = True
    template_values['nav_color'] = 'light-nav'
    template_values['unscrolled'] = True
    return template_values

class LandingPage(WebRequestHandler):
    def get(self):
        path = 'landing.html'
        template_values = get_template_values_for_landing()
        self.write(self.get_rendered_html(path, template_values), 200)

app = webapp2.WSGIApplication(
    [
        ('/', LandingPage)
    ]
)