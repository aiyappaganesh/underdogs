import webapp2
from handlers.web import WebRequestHandler
from model.company import Company
from cities_mapping import cities_map

def get_template_values_for_landing():
    template_values = {}
    donuts = 3
    donuts -= 1
    donut_size = 200-(5*donuts)
    score_font_size = 40-(3*donuts)
    tooltip_font_size = 14-donuts
    donut_scores = [('Design', 0.58),
                    ('Dev', 0.75),
                    ('Domain', 0.28)]
    template_values['donut_scores'] = donut_scores
    template_values['donut_size'] = donut_size
    template_values['score_font_size'] = score_font_size
    template_values['tooltip_font_size'] = tooltip_font_size
    template_values['full_color'] = '#139fe1'
    template_values['empty_color'] = '#333333'
    template_values['steve_img'] = '/assets/img/landing/steve.png'
    template_values['sec_3_copy_big'] = 'All great products are built by small teams'
    template_values['sec_3_copy_medium'] = 'Every Pirates startup has 3-4 team members who share a deep chemistry and dedication'
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
    template_values['carousel_2_2_des_1_copy_2'] = 'Try making the icons smaller and giving more whitespace'
    template_values['carousel_2_2_des_2_copy_1'] = 'Irea Jackson, Python Developer, Looking Glass'
    template_values['carousel_2_2_des_2_copy_2'] = 'Maybe change the preferences to action sheets'
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