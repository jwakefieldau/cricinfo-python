from .cricinfo import CricinfoGeneric

class MatchFOW(CricinfoGeneric):

	def __init__(self, *args, **kwargs):

		self.wicket = None
		self.runs = None
		self.out_batter = None # Player
		self.over = None

		super()._set_attrs_from_kwarg_d(kwargs)