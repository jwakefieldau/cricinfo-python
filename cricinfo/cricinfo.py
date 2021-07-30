import asyncio
import aiohttp
import aiodns

class CricinfoGeneric(object):

	rate_limit = float(1/20)	# 20 per second

	@classmethod
	def _prep_endpoint(cls, endpoint_k, param_d=None, url_suffix=None):
		endpoint = cls.endpoints.get(endpoint_k)

		if not endpoint:
			raise ValueError(f'Unknown endpoint: {endpoint_k}')

		endpoint_params = endpoint.get('params')
		if param_d:
			if endpoint_params:
				param_k_set = set(param_d.keys())
				endpoint_params_set = set(endpoint_params)
				if param_k_set != endpoint_params_set:
					raise ValueError(f'Param mismatch, endpoint {endpoint_k} expects {endpoint_params} but params supplied were {param_d.keys()}') 
			else:
				raise ValueError(f'Endpoint {endpoint_k} has no params but params were supplied')
		else:
			if endpoint_params:
				raise ValueError(f'Endpoint {endpoint_k} has params but none supplied')

		url_base = endpoint.get('url_base')
		if url_base:
			if url_suffix:
				# prevent double slashes
				if url_base.endswith('/'):
					url_base = url_base[:-1]
				if url_suffix.startswith('/'):
					url_suffix = url_suffix[1:]
				url = f"{url_base}/{url_suffix}"
			else:
				raise ValueError(f"Endpoint {endpoint_k} has a URL base but no suffix specified")
		else:
			if url_suffix:
				raise ValueError(f"Endpoint {endpoint_k} has a suffix but no URL base")
			else:
				url = endpoint.get('url')
				if not url:
					raise ValueError(f"Endpoint {endpoint_k} has no URL")

		# if necessary, we could do some processing of parameters here
		ret_param_d = dict(param_d) if param_d else None

		return (url, ret_param_d,)

	@classmethod
	async def _single_req(cls, url, out_param_d=None):
		async with aiohttp.ClientSession() as session:
			async with session.get(url, params=out_param_d) as http_resp:
				http_resp.raise_for_status()
				http_resp_text = await http_resp.text()
				return http_resp_text

	@classmethod
	def _wrap_single_req(cls, endpoint_k, param_d=None, url_suffix=None):
		(url, out_param_d,) = cls._prep_endpoint(endpoint_k, param_d, url_suffix)
		return asyncio.run(cls._single_req(url, out_param_d))
