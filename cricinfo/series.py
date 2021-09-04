from .cricinfo import CricinfoGeneric

class Series(CricinfoGeneric):

	def __init__(self, *args, **kwargs):
		self.id = None
		self.name = None

		#TODO - more

		self._set_attrs_from_kwarg_d(kwargs)
