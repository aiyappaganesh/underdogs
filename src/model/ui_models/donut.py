class Donut():
	def __init__(self, size, cutout, title, score, container_color, full_color, empty_color):
		self.size = size
		self.cutout = cutout
		self.container_side = size * cutout
		self.container_pos = (size / 2.0) - (self.container_side / 2.0)
		self.title = title
		self.score = score
		self.font_size = self.container_side * 0.4
		self.container_color = container_color
		self.full_color = full_color
		self.empty_color = empty_color