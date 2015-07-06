import webapp2
import logging

from handlers.web import WebRequestHandler
from model.company import Company
from cities_mapping import cities_map
from model.ui_models.donut import Donut
from model.ui_models.landing_page_team_member import TeamMember
from model.ui_models.landing_startup import Startup
from model.ui_models.factories.landing_community_carousel import Carousel
from model.ui_models.factories.landing_tracking_carousel import TrackingCarousel
from model.ui_models.factories.donut_factory import DonutFactory
from model.ui_models.centered_contents import CenteredContents, CenteredContent

def get_team_members():
    members = [("Designer", '/assets/img/landing/slide-3-1.png'),
               ("Full Stack Developer", '/assets/img/landing/slide-3-2.png'),
               ("Mobile Developer", '/assets/img/landing/slide-3-3.png')]
    return [TeamMember(member[0], member[1]) for member in members]

def get_startups():
    startups = [("Haggle", "Your World. Your Price.", "/assets/img/landing/slide-startups-1.png"),
                ("Color Door", "Rent broker free", "/assets/img/landing/slide-startups-2.png"),
                ("Haze", "Transparent healthcare for all", "/assets/img/landing/slide-startups-3.png")]
    return [Startup(s[0], s[1], s[2]) for s in startups]

def get_landing_centered_contents():
    contents_arr = [("BUILD TOGETHER",["header-1","white-font"], None), 
                    ("Hire creative startups to build innovative apps",["header-3","white-font"], None), 
                    (None, None, "components/get_started_button.html")]
    contents = [CenteredContent(s[0], s[1], s[2]) for s in contents_arr]
    return CenteredContents(None, 0, contents, False)

def get_steve_centered_contents():
    contents_arr = [("\"It's better to be a pirate than join the navy\"", ["header-2", "center-align"]),
        ("Steve Jobs, 1984",["header-3", "right-align"]),
        ("Urban legend has it that the original Macintosh team flew a Pirate flag over the building as they raced against time and naysayers to build the Mac.",["normal-copy"])]
    contents = [CenteredContent(s[0], s[1]) for s in contents_arr]
    return CenteredContents(406, 0, contents)

def get_template_values_for_landing():
    template_values = {}
    template_values['team_members'] = get_team_members()
    template_values['startups'] = get_startups()
    template_values['landing_centered'] = get_landing_centered_contents()
    template_values['steve_centered'] = get_steve_centered_contents()
    template_values['donuts'] = DonutFactory.get_donuts(128, 0.8, [('Design', 0.58), ('Dev', 0.75), ('Domain', 0.28)], '#ffffff', '#139fe1', '#333333')
    template_values['community_carousel'] = Carousel()
    template_values['tracking_carousel'] = TrackingCarousel()
    template_values['no_navbar_onload'] = True
    template_values['nav_color'] = 'light-nav'
    template_values['unscrolled'] = True
    return template_values

class LandingPage(WebRequestHandler):
    def get(self):
        path = 'landing.html'
        template_values = get_template_values_for_landing()
        self.write(self.get_rendered_html(path, template_values), 200)

class GetStartedTypeformPage(WebRequestHandler):
    def get(self):
        path = 'get_started_typeform.html'
        self.write(self.get_rendered_html(path, {}), 200)

app = webapp2.WSGIApplication(
    [
        ('/get_started_typeform', GetStartedTypeformPage),
        ('/', LandingPage)
    ]
)