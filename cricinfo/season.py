from .cricinfo import CricinfoGeneric

class Season(CricinfoGeneric):

	def __init__(self, *args, **kwargs):
		self.id = None
		self.year = None
		self.next_year = None # this is for eg: 1974-1975

		#TODO
		self._set_attrs_from_kwarg_d(kwargs)