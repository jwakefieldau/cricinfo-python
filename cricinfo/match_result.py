from .cricinfo import CricinfoGeneric

class MatchResult(CricinfoGeneric):

	def __init__(self, *args, **kwargs):

		self.winning_team = None
		self.win = False
		self.run_margin = None
		self.wicket_margin = None
		self.innings_margin = False
		self.draw = False
		self.tie = False
		self.abandoned = False
		self.cancelled = False
		self.postponed = False

		self._set_attrs_from_kwarg_d(kwargs)