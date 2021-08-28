from .cricinfo import CricinfoGeneric

class MatchListStats(CricinfoGeneric):

	def __init__(self, *args, **kwargs):

		self.first_innings_score = None
		self.first_innings_not_out = None
		self.second_innings_score = None
		self.second_innings_not_out = None
		self.total_wickets = None
		self.runs_conceded = None
		self.catches = None
		self.stumpings = None
		self.opposition = None
		self.ground = None
		self.start_dt = None # store a datetime object
		self.scorecard_url_path = None

		super()._set_attrs_from_kwarg_d(kwargs)

