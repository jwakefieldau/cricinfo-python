from .cricinfo import CricinfoGeneric

class MatchBatterInnings(CricinfoGeneric):

	def __init__(self, *args, **kwargs):

		self.batter_id = None
		self.batter_name = None
		self.captain = False
		self.wicket_keeper = False
		self.not_out = None
		self.how_out_method = None
		self.how_out_fielder = None
		self.how_out_bowler = None
		self.runs = None
		self.balls = None
		self.minutes = None
		self.fours = None
		self.sixes = None
		self.strike_rate = None

		self._set_attrs_from_kwarg_d(kwargs)