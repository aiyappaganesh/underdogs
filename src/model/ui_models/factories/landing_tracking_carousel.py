from model.ui_models.centered_contents import CenteredContents, CenteredContent

class Slide():
    def __init__(self, img, centered):
        self.img = img
        self.centered = centered

class TrackingCarousel():
    def build_slides(self):
        COPY_CLASS = 'track-copy'
        s1 = Slide('/assets/img/landing/track_1.gif',CenteredContents(200, 0, [CenteredContent("COLLABORATE AT EVERY STAGE", [COPY_CLASS, "header-1", "center-align"])], False))
        s2 = Slide('/assets/img/landing/track_2.png',CenteredContents(200, 0, [CenteredContent("TRACK IN REAL TIME", [COPY_CLASS, "header-1", "center-align"])], False))
        return [s1, s2]

    def __init__(self):
        self.slides = self.build_slides()