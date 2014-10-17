import webapp2
from handlers.web import WebRequestHandler

class LandingPage(WebRequestHandler):
    def get(self):
        path = 'landing.html'
        template_values = {}
        template_values['startup_icons'] = {}
        template_values['startup_icons']['icon_sets'] = \
            [
                ['landing/startups/bergerfohr.png','landing/startups/partender.png','landing/startups/tendigi.png'],
                ['landing/startups/fueled.jpg','landing/startups/beagleslabs.png','landing/startups/AppSheet.png'],
                ['landing/startups/meloman.png','landing/startups/shuffle.jpg','landing/startups/phonio.jpg'],
                ['landing/startups/scalyr.png','landing/startups/shout.jpg','landing/startups/mixmax.jpg']
            ]
        template_values['startup_icons']['title'] = 'Startups'
        template_values['startup_icons']['description'] = 'Startups have very good developers and designers but are constantly looking for working capital.'
        template_values['startup_icons']['icons_first'] = True
        template_values['startup_icons']['buttons'] = [{'link':'/startups/registration','name':'Add Your Startup'},
                                                       {'link':'/projects/list','name':'Find projects'}]

        template_values['enterprise_icons'] = {}
        template_values['enterprise_icons']['icon_sets'] = \
            [
                ['landing/enterprises/ibm.png','landing/enterprises/accenture.png','landing/enterprises/airasia.png'],
                ['landing/enterprises/airtel.png','landing/enterprises/thomascook.png','landing/enterprises/capgemini.png'],
                ['landing/enterprises/sheraton.png','landing/enterprises/goldmansachs.png','landing/enterprises/mckinsey.png'],
                ['landing/enterprises/bofa.png','landing/enterprises/icici.png','landing/enterprises/cafecoffeeday.jpg']
            ]
        template_values['enterprise_icons']['title'] = 'Enterprises'
        template_values['enterprise_icons']['description'] = 'Enterprises often give projects to outsourcing companies and freelancers, both of who lack the dev and design talent of startups.'
        template_values['enterprise_icons']['icons_first'] = False
        template_values['enterprise_icons']['buttons'] = [{'link':'/projects/registration','name':'Register a project'},
                                                          {'link':'/startups/search/criteria','name':'Fitting Startups'}]

        self.write(self.get_rendered_html(path, template_values), 200)

app = webapp2.WSGIApplication(
    [
        ('/', LandingPage)
    ]
)