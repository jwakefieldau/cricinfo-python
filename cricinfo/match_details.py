from .cricinfo import CricinfoGeneric

class MatchDetails(CricinfoGeneric):

	def __init__(self, *args, **kwargs):

		self.ground = None
		self.toss_won_by_team = None
		self.toss_decision_bat = None # False means bowled
		self.series = []
		self.season = None
		self.player_of_the_match = [] # we can have multiple players of the match
		self.series_result = None
		

		super()._set_attrs_from_kwarg_d(kwargs)