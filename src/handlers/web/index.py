import webapp2
from handlers.web import WebRequestHandler
from model.company import Company
from cities_mapping import cities_map

def get_template_values_for_landing():
    template_values = {}
    q = Company.all()
    sorted_companies = {}
    for c in q.fetch(3):
        id = c.key().id()
        sorted_companies[id] = {}
        score = float(c.influence_avg) if c.influence_avg else 0.0
        sorted_companies[id]['score'] = score
        sorted_companies[id]['image'] = c.image
        sorted_companies[id]['name'] = c.name
        sorted_companies[id]['hello'] = c.hello
        sorted_companies[id]['profile'] = c.profile
        sorted_companies[id]['city'] = cities_map[str(id)] if str(id) in cities_map else cities_map['default']
    sorted_companies = sorted(sorted_companies.iteritems(), key=lambda (k,v): v['score'], reverse = True)
    template_values['startups'] = sorted_companies
    template_values['steve_img'] = '/assets/img/landing/steve.png'
    template_values['sec_3_copy_big'] = 'All great products are built by small teams'
    template_values['sec_3_copy_medium'] = 'Every Pirates startup has 3-4 team members who share a deep chemistry and dedication'
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