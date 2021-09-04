import asyncio

from bs4 import BeautifulSoup

from .cricinfo import CricinfoGeneric
from .match_result import MatchResult
from .team import Team

class Match(CricinfoGeneric):

	endpoints = {
		'from_player_match_list': {
			'url_base': 'https://stats.espncricinfo.com/'
		}
	}

	def __init__(self, *args, **kwargs):
		
		self.id = None
		self.match_result = None
		self.teams = [] 
		self.team_innings_list = []
		self.match_details = None
		self.close_of_play_list = []

		super()._set_attrs_from_kwarg_d(kwargs)

	#TODO - coro for grabbing single match scorecard
	# either from a URL suffix from a match list summary or
	# a full URL 
	#NOTE - why do we want to support full URL?
	@staticmethod
	async def coro_get_match_from_url(player_match_url_suffix=None, url=None):
		(_, match_html) = await Match._coro_req('from_player_match_list', url_suffix=player_match_url_suffix)

		match_result = MatchResult()
		match_result.update_from_html(match_html)

		#TODO parse innings


	#TODO - method for grabbing single match scorecard using coro

	#TODO - method for grabbing player's scorecards in bulk
	# using bulk coro wrapper
