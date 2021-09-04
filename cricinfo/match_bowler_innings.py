from .cricinfo import CricinfoGeneric

class MatchBowlerInnings(CricinfoGeneric):

	def __init__(self, *args, **kwargs):

		self.bowler = None # Player
		self.overs = None
		self.maidens = None
		self.runs = None
		self.wickets = None
		self.economy_rate = None
		self.wides = None
		self.no_balls = None

		super()._set_attrs_from_kwarg_d(kwargs)

