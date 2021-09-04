from .cricinfo import CricinfoGeneric

class MatchTeamInnings(CricinfoGeneric):

	def __init__(self, *args, **kwargs):

		self.team = None # Team
		self.batter_innings_list = []
		self.extras = None
		self.bowler_innings_list = []
		self.fow_list = []
		self.wickets = None
		self.total = None
		self.declared = None
		self.compulsory_closure = None

		super()._set_attrs_from_kwarg_d(kwargs)
