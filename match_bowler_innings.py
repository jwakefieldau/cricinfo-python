from .cricinfo import CricinfoGeneric

class MatchBowlerInnings(CricinfoGeneric):

	def __init__(self, *args, **kwargs):

		# TODO attributes

		super()._set_attrs_from_kwarg_d(kwargs)