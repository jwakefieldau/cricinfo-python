from cricinfo import CricinfoGeneric

class Match(CricinfoGeneric):

	endpoints = {
		'from_player_match_list': {
			'url_base': 'https://stats.espncricinfo.com/'
		}
	}

	#TODO - endpoint(s) for grabbing match scorecards with
	# url base for scorecard path to be appended to

	def __init__(self, *args, **kwargs):
		#TODO - attributes

		#super()._set_attrs_from_kwarg_d(kwargs)
		pass

	#TODO - coro for grabbing single match scorecard
	# either from a URL suffix from a match list summary or
	# a full URL
	async def get_match_from_url(player_match_url_suffix=None, url=None):
		pass

	#TODO - coro for grabbing player's scorecards in bulk
	# using bulk coro wrapper
