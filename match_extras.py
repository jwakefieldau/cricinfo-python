from .cricinfo import CricinfoGeneric

class MatchExtras(CricinfoGeneric):

	def __init__(self, *args, **kwargs):

		self.byes = 0
		self.leg_byes = 0
		self.wides = 0
		self.no_balls = 0
		self.penalties = 0