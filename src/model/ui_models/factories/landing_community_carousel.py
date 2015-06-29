from model.ui_models.centered_contents import CenteredContents, CenteredContent

class SlidePerson():
    def __init__(self, centered, img):
        self.img = img
        self.centered = centered
		
class Slide():
    def __init__(self, title, people):
        self.title = title
        self.people = people
		
class Carousel():
    def build_slides(self):
        MEDIUM_COPY = "header-3"
        SMALL_COPY = "normal-copy"
        people = [SlidePerson(CenteredContents(128, 15, [CenteredContent("Adam Jackson, Designer, Haze", [MEDIUM_COPY, "left-align", "white-font"]), CenteredContent("Try making the icons smaller and giving more whitespace", [SMALL_COPY, "left-align", "white-font"])]), "/assets/img/landing/design_1.png"),
				  SlidePerson(CenteredContents(128, 15, [CenteredContent("Hailey Peterson, Designer, For Me", [MEDIUM_COPY, "left-align", "white-font"]), CenteredContent("Maybe change the preferences to action sheets", [SMALL_COPY, "left-align", "white-font"])]), "/assets/img/landing/design_2.png")]
        s1 = Slide("PIRATES DESIGN TOGETHER", people)
        people = [SlidePerson(CenteredContents(128, 15, [CenteredContent("Eric Erickson, iOS Developer, Beagles Labs", [MEDIUM_COPY, "left-align", "white-font"]), CenteredContent("Set 'Clip Subviews' to true for the corner radius to show", [SMALL_COPY, "left-align", "white-font"])]), "/assets/img/landing/dev_1.png"),
				  SlidePerson(CenteredContents(128, 15, [CenteredContent("Irea Jackson, Python Developer, Looking Glass", [MEDIUM_COPY, "left-align", "white-font"]), CenteredContent("Have you created an __init.py__ in the directory?", [SMALL_COPY, "left-align", "white-font"])]), "/assets/img/landing/dev_2.png")]
        s2 = Slide("PIRATES CODE TOGETHER", people)
        return [s1, s2]

    def __init__(self):
        self.slides = self.build_slides()