from .cricinfo import CricinfoGeneric

class Team(CricinfoGeneric):

	def __init__(self, *args, **kwargs):

		self.id = None
		self.name = None

		super()._set_attrs_from_kwarg_d(kwargs)