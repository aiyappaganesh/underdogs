from model.ui_models.donut import Donut
class DonutFactory():
	@classmethod
	def get_donuts(cls, size, cutout, scores, container_color, full_color, empty_color):
		ret_val = []
		for score in scores:
			d = Donut(size, cutout, score[0], score[1], container_color, full_color, empty_color)
			ret_val.append(d)
		return ret_val