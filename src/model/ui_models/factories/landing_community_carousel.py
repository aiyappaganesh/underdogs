class SlidePerson():
	def __init__(self, name, desc, img):
		self.name = name
		self.desc = desc
		self.img = img
		
class Slide():
	def __init__(self, title, people):
		self.title = title
		self.people = people
		
class Carousel():
	def build_slides(self):
		people = [SlidePerson("Adam Jackson, Designer, Haze", "Try making the icons smaller and giving more whitespace", "/assets/img/landing/design_1.png"),
				  SlidePerson("Hailey Peterson, Designer, For Me", "Maybe change the preferences to action sheets", "/assets/img/landing/design_2.png")]
		s1 = Slide("The entire Design community of Pirates contributes to ensure your app has the best user experience", people)
		people = [SlidePerson("Eric Erickson, iOS Developer, Beagles Labs", "Set 'Clip Subviews' to true for the corner radius to show", "/assets/img/landing/dev_1.png"),
				  SlidePerson("Irea Jackson, Python Developer, Looking Glass", "Have you created an __init.py__ in the directory?", "/assets/img/landing/dev_2.png")]
		s2 = Slide("Pirates developers help each to solve problems and write the best code", people)
		return [s1, s2]

	def __init__(self):
		self.slides = self.build_slides()		