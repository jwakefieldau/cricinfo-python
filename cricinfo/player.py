import asyncio
import re

from collections import defaultdict
from datetime import datetime
from bs4 import BeautifulSoup

from .cricinfo import CricinfoGeneric, _bulk_coro_wrapper, _bulk_obj_method_coro_wrapper
from .player_career_stats import PlayerCareerStats
from .match_list_stats import MatchListStats

class Player(CricinfoGeneric):

	# note that following links in browser elicits requests for param1=value;param2=value
	# but ampersands are still accepted
	endpoints = {
		'player_search': {
			'url': 'https://search.espncricinfo.com/ci/content/site/search.html',
			'params': [
				'search',
				'type'
			]
		},
		'player_detail': {
			'url_base': 'https://search.espncricinfo.com/'
		},
		'player_matches': {
			# class=1 - Test, class=2 - ODI, class=3 - T20I,
			# class=11 - Test/ODI/T20I, class=20 - Youth Test, class=21 - Youth ODI, 
			# ../player/[num].html/?class={1,2,3,11,20,20,21};template=results;type=allround;view=match
			'url_base': 'https://stats.espncricinfo.com/ci/engine/player/',
			'params': [
				'class',
				'template',
				'type',
				'view'
			]
		}
	}

	id_from_detail_url_path_re = re.compile('^.+/([0-9]+)\.html$')

	def __init__(self, *args, **kwargs):

		self.id = None
		self.country = None
		self.name = None
		self.birth_year = None
		self.death_year = None
		self.got_details = False
		self.got_stats = False
		self.got_matches = False
		self.detail_url_path = None
		self.redir_detail_url = None # this is where we get redirected to
		self.full_name = None
		self.batting_style = None
		self.bowling_style = None
		self.born = None
		self.teams = []
		self.career_stats_dict = {}
		self.match_list_stats_dict = defaultdict(list)

		super()._set_attrs_from_kwarg_d(kwargs)

	def __str__(self):
		name_str = self.name if self.name else '[Unknown Name]'
		yob_str = self.birth_year if self.birth_year else ''
		yod_str = self.death_year if self.death_year else ''
		lifetime_str = f"{yob_str}-{yod_str}"
		country_str = self.country if self.country else '[Unknown Country]'	

		return f"{name_str}, {lifetime_str}, {country_str}"

	@staticmethod
	async def coro_player_search(search_str):

		ret_players = []

		(_, search_resp_text,) = await Player._coro_req(endpoint_k='player_search',
			param_d={'search': search_str, 'type': 'player'}
		)

		# <ul class="player-list three-item-stack">
		bs = BeautifulSoup(search_resp_text, 'html.parser')
		results_ul = bs.find('ul', attrs={'class': 'player-list three-item-stack'})	

		cur_country = None
		for player_li in results_ul.find_all('li'):

			player_li_classes = player_li.get('class') 
			# country header
			if player_li_classes and player_li_classes[0] == 'country-from':
				player_country_h3 = player_li.find('h3')

				if not player_country_h3:
					raise ValueError(f"couldn't find player country <h3> tag.  <li>:{player_li}:")

				cur_country = str(player_country_h3.string)
				if not cur_country or cur_country == '':
					raise ValueError(f"Couldn't get player country from <h3> tag.  <h3>:{player_country_h3}:")

			# player
			else:
				# set country to whatever the current one is
				player_obj = Player(country=cur_country)

				player_name_p = player_li.find('p', attrs={'class': 'alphabetical-name'})

				if not player_name_p:
					raise ValueError(f"couldn't find player name <p> tag.  <li>:{player_li}:")

				name_dates_str = str(player_name_p.string)
				name_dates_fields = name_dates_str.rsplit(',', 1)
				player_obj.name = name_dates_fields[0].strip()

				if not player_obj.name or player_obj.name == '':
					raise ValueError(f"Couldn't get player name from <p> tag.  <p>:{player_name_p}")

				if len(name_dates_fields) == 2:
					yob_yod_str = name_dates_fields[1].strip()
					yob_yod_fields = yob_yod_str.split('-')
					yob_str = yob_yod_fields[0].strip()
					yod_str = yob_yod_fields[1].strip()

					if len(yob_str) > 0:
						player_obj.birth_year = int(yob_str)

					if len(yod_str) > 0:
						player_obj.death_year = int(yod_str)

				player_detail_url_a = player_li.find('a')
				if not player_detail_url_a:
					raise ValueError(f"Couldn't find player detail URL <a> tag. <li>:{player_li}:") 

				player_obj.detail_url_path = str(player_detail_url_a['href'])
				if not player_obj.detail_url_path or player_obj.detail_url_path == '':
					raise ValueError(f"Couldn't find player detail URL path, <a>:player_detail_url_a:")

				# grab the player's numerical ID from the detail URL path,
				# to use later for match list stuff	
				player_id_m = Player.id_from_detail_url_path_re.match(player_obj.detail_url_path)

				if not player_id_m:
					raise ValueError(f"Couldn't extract player ID from player detail URL path:{player_obj.detail_url_path}")

				player_obj.id = player_id_m.group(1)
				
				ret_players.append(player_obj)

		return ret_players

	@staticmethod
	def player_search(search_str):
		return asyncio.run(Player.coro_player_search(search_str))

	@staticmethod
	def bulk_player_search(search_str_list):
		return _bulk_coro_wrapper(Player.coro_player_search, search_str_list)

	async def coro_get_details(self):
		(player_detail_resp, player_detail_text,) = await Player._coro_req('player_detail', url_suffix=self.detail_url_path)

		player_detail_resp_history = player_detail_resp.history
		if len(player_detail_resp_history) < 1:
			raise ValueError("Expected a redirection history after getting player details HTML")

		self.redir_detail_url = player_detail_resp_history[-1]['Location']

		#<div class="player-overview-details>"
		bs = BeautifulSoup(player_detail_text, 'html.parser')

		# there are further divs inside here, each with a <p>
		# whose text describes the attribute, and a <h5> whose
		# text has the value
		details_div = bs.find('div', attrs={'class': 'player_overview-grid'})
		if not details_div:
			raise ValueError("Cannot find details div")

		for inner_div in details_div.find_all('div'):

			desc_str = None
			value_str = None 

			desc_p = inner_div.find('p')
			if not desc_p:
				raise ValueError(f"Cannot find description <p> in div:{inner_div}:")
			desc_str = str(desc_p.string)
			
			value_h5 = inner_div.find('h5')
			if not value_h5:
				raise ValueError(f"Cannot find value <h5> in div:{inner_div}:")
			value_str = str(value_h5.string)

			if desc_str == 'Full Name':
				self.full_name = value_str
			elif desc_str == 'Born':
				self.born = value_str
			elif desc_str == 'Batting Style':
				self.batting_style = value_str
			elif desc_str == 'Bowling Style':
				self.bowling_style = value_str

		# <div class="overview-teams-grid mb-4">
		# teams are in a separate grid, each in <h5> tags
		teams_div = bs.find('div', attrs={'class': 'overview-teams-grid mb-4'})
		if not teams_div:
			raise ValueError("Cannot find teams div")

		for team_h5 in teams_div.find_all('h5'):
			self.teams.append(str(team_h5.string))

		self.got_details = True

	def get_details(self):
		asyncio.run(self.coro_get_details())

	async def coro_get_match_summaries_career_stats(self, match_selector='senior-international'):

		match_selector_d = {
			'senior-international': 11,
			'test': 1,
			'odi': 2,
			't20i': 3,
			'youth-test': 20,
			'youth-odi': 21
		}
		match_selector_num = match_selector_d.get(match_selector)
		if not match_selector_num:
			raise ValueError(f"Unknown match selector: {match_selector}")

		url_suffix = f"{self.id}.html"

		(_, http_resp_text) = await Player._coro_req(
			'player_matches', param_d={
				'class': match_selector_num,
				'template': 'results',
				'type': 'allround',
				'view': 'match'
			},
			url_suffix=url_suffix
		)

		bs = BeautifulSoup(http_resp_text, 'html.parser')

		# <caption>Career averages</caption>
		# the <table> that is the parent of this is what we want
		captions = bs.find_all('caption')
		if not captions or len(captions) < 2:
			raise ValueError(f"Missing <caption> tags")

		if captions[0].string == 'Career averages':
			averages_table = captions[0].parent

		if averages_table.name != 'table':
			raise ValueError(f"parent tag of averages caption is not <table>")

		averages_thead = averages_table.find('thead')
		averages_thead_tr = averages_thead.find('tr')

		# check order of string values in <th>s in <thead><tr>
		# as this determines the order of stats <td>s in <tbody><tr>
		field_indices = []
		for averages_th in averages_thead_tr.find_all('th'):
			# otherwise we get 'None' instead of None and that's annoying
			field_name = str(averages_th.string) if averages_th.string else None
			field_indices.append(field_name)

		averages_tbody = averages_table.find('tbody')
		averages_tbody_tr = averages_tbody.find('tr')

		stats_obj = PlayerCareerStats()
		for (i, averages_td,) in enumerate(averages_tbody_tr.find_all('td')):
			
			cur_val = str(averages_td.string)

			# if this belongs to a blank header, skip it
			if not field_indices[i]:
				continue

			elif field_indices[i] == 'Span':
				stats_obj.career_year_span = cur_val

			elif field_indices[i] == 'Mat':
				stats_obj.matches = int(cur_val) 

			elif field_indices[i] == 'Runs':
				stats_obj.runs = int(cur_val)

			elif field_indices[i] == 'HS':
				stats_obj.highest_score = int(cur_val)

			elif field_indices[i] == 'Bat Av':
				stats_obj.batting_average = float(cur_val)	

			elif field_indices[i] == '100':
				stats_obj.hundreds = int(cur_val)

			elif field_indices[i] == 'Wkts':
				stats_obj.wickets = int(cur_val)

			elif field_indices[i] == 'BBI':
				stats_obj.best_bowling_innings = cur_val

			elif field_indices[i] == 'Bowl Av':
				stats_obj.bowling_average = float(cur_val)

			elif field_indices[i] == '5':
				stats_obj.five_wickets_innings = int(cur_val)

			elif field_indices[i] == 'Ct':
				stats_obj.catches = int(cur_val)

			elif field_indices[i] == 'St':
				stats_obj.stumpings = int(cur_val)

			# we don't need to store this specifically
			elif field_indices[i] == 'Ave Diff':
				continue

			else:
				raise ValueError(f"Unknown field name {field_indices[i]}")

			self.career_stats_dict[match_selector] = stats_obj

		# <caption>Match by match list</caption>
		# similar to above but create MatchListStats instances in list at
		# self.match_list_stats_dict[match_selector]
		if captions[1].string == 'Match by match list':
			match_list_table = captions[1].parent

		match_list_thead = match_list_table.find('thead')
		match_list_thead_tr = match_list_thead.find('tr')

		field_indices = []
		for match_list_th in match_list_thead_tr.find_all('th'):
			# otherwise we get 'None' instead of None and that's annoying
			field_name = str(match_list_th.string) if match_list_th.string else None
			field_indices.append(field_name)

		match_list_tbody = match_list_table.find('tbody')
		match_list_tbody_tr = match_list_tbody.find('tr')

		match_stats_obj = MatchListStats()
		for (i, match_td,) in enumerate(match_list_tbody_tr.find_all('td')):

			cur_val = str(match_td.string)

			if field_indices[i] == 'Bat1':
				(num_score, not_out,) = MatchListStats.parse_score(cur_val)
				match_stats_obj.first_innings_score = num_score
				match_stats_obj.first_innings_not_out = not_out

			elif field_indices[i] == 'Bat2':
				(num_score, not_out,) = MatchListStats.parse_score(cur_val)
				match_stats_obj.second_innings_score = num_score
				match_stats_obj.second_innings_not_out = not_out

			# ignore total runs as it's trivial
			elif field_indices[i] == 'Runs':
				continue

			elif field_indices[i] == 'Wkts':
				match_stats_obj.total_wickets = int(cur_val)

			elif field_indices[i] == 'Conc':
				match_stats_obj.runs_conceded = int(cur_val)

			elif field_indices[i] == 'Ct':
				match_stats_obj.catches = int(cur_val)

			elif field_indices[i] == 'St':
				match_stats_obj.stumpings = int(cur_val)

			elif field_indices[i] == 'Opposition':
				match_stats_obj.opposition = cur_val

			elif field_indices[i] == 'Ground':
				match_stats_obj.ground = cur_val

			elif field_indices[i] == 'Start Date':
				# '2 Dec 1999'
				match_stats_obj.start_dt = datetime.strptime(cur_val, "%d %b %Y")

			# blank header, specifically at the end, is where the link to the scorecard is
			# there are a couple of others, ignore them
			elif not field_indices[i]:
				if i == len(field_indices) - 1:
					scorecard_a_tag = match_td.find('a')
					match_stats_obj.scorecard_url_path = str(scorecard_a_tag['href'])
					m = Player.id_from_detail_url_path_re.match(match_stats_obj.scorecard_url_path)

					if not m:
						raise ValueError(f"Unable to extract match ID from URL path:{match_stats_obj.scorecard_url_path}")

					match_stats_obj.id = m.groups(1)

			else:
				raise ValueError(f"Unknown match list column header: {field_indices[i]}")

		self.match_list_stats_dict[match_selector].append(match_stats_obj) 

	def get_match_summaries_career_stats(self, match_selector='senior-international'):
		asyncio.run(self.coro_get_match_summaries_career_stats(match_selector))

	@staticmethod
	def bulk_get_match_summaries_career_stats(player_obj_list):
		_bulk_obj_method_coro_wrapper(player_obj_list, 'coro_get_match_summaries_career_stats')