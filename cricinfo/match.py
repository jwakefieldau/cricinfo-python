from cricinfo import CricinfoGeneric

class Match(CricinfoGeneric):

	#TODO - endpoint(s) for grabbing match scorecards with
	# url base for scorecard path to be appended to

	def __init__(self, *args, **kwargs):
		#TODO - attributes

		super()._set_attrs_from_kwarg_d(kwargs)

	#TODO - coro for grabbing single match scorecard

	#TODO - coro for grabbing player's scorecards in bulk
	# using bulk coro wrapper
