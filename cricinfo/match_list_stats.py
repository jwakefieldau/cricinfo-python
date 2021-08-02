from cricinfo import CricinfoGeneric

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

	@staticmethod
	def parse_score(score_str):
		if score_str in ['DNB', '-']:
			num_score = None
			not_out = None
		elif score_str.endswith('*'):
			not_out = True
			num_score = int(score_str[:-1])
		else:
			not_out = False
			num_score = int(score_str)

		return (num_score, not_out,)