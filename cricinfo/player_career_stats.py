from cricinfo import CricinfoGeneric

class PlayerCareerStats(CricinfoGeneric):

	def __init__(self, *args, **kwargs):

		self.career_year_span = None
		self.matches = None
		self.runs = None
		self.highest_score = None
		self.highest_score_not_out = None
		self.batting_average = None
		self.hundreds = None
		self.wickets = None
		self.best_bowling_innings = None
		self.bowling_average = None
		self.five_wickets_innings = None
		self.catches = None
		self.stumpings = None

		super()._set_attrs_from_kwarg_d(kwargs)