from bs4 import BeautifulSoup

from .cricinfo import CricinfoGeneric

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
		}
	}

	def __init__(
		self, country=None, name=None, birth_year=None,
		death_year=None, detail_url_path=None
	):
		self.country = country
		self.name = name
		self.birth_year = birth_year
		self.death_year = death_year
		self.got_details = False
		self.got_stats = False
		self.got_matches = False
		self.detail_url_path = detail_url_path
		self.full_name = None
		self.batting_style = None
		self.bowling_style = None
		self.born = None
		self.teams = []

	def __str__(self):
		name_str = self.name if self.name else '[Unknown Name]'
		yob_str = self.birth_year if self.birth_year else ''
		yod_str = self.death_year if self.death_year else ''
		lifetime_str = f"{yob_str}-{yod_str}"
		country_str = self.country if self.country else '[Unknown Country]'	

		return f"{name_str}, {lifetime_str}, {country_str}"

	@staticmethod
	def player_search(search_str):

		ret_players = []

		search_resp_text = Player._wrap_single_req(endpoint_k='player_search',
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
				
				ret_players.append(player_obj)

		return ret_players

	def get_details(self):
		player_detail_text = Player._wrap_single_req('player_detail', url_suffix=self.detail_url_path)

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