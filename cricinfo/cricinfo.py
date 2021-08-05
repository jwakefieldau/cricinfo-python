import asyncio
import aiohttp
import aiodns
import random

class CricinfoGeneric(object):

	rate_limit = {
		'avg': float(1/10),	# 10 per second
		'variance': float(1/5) # +/- 1/5
	}

	def _set_attrs_from_kwarg_d(self, kwarg_d):
		# set attribute values for attributes we already know about
		for (k, v,) in kwarg_d.items():
			if hasattr(self, k):
				setattr(self, k, v)

	@classmethod
	def _prep_endpoint(cls, endpoint_k, param_d=None, url_base=None, url_suffix=None):
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

		url_base = url_base if url_base else endpoint.get('url_base')
		url_suffix = url_suffix if url_suffix else endpoint.get('url_suffix')
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
	async def _rate_limit_sleep(cls):
		rl_d = cls.rate_limit
		rl_min = rl_d['avg'] - (rl_d['avg'] * rl_d['variance'])
		rl_max = rl_d['avg'] + (rl_d['avg'] * rl_d['variance'])
		rl_sleep_interval = random.uniform(rl_min, rl_max)

		await asyncio.sleep(rl_sleep_interval)

	@classmethod
	async def _coro_req(cls, endpoint_k, param_d=None, url_base=None, url_suffix=None):
		(url, out_param_d,) = cls._prep_endpoint(endpoint_k, param_d, url_base, url_suffix)
		async with aiohttp.ClientSession() as session:
			await cls._rate_limit_sleep()
			async with session.get(url, params=out_param_d) as http_resp:
				http_resp.raise_for_status()
				# text must be read within session context
				http_resp_text = await http_resp.text()
				return (http_resp, http_resp_text,)


def _bulk_coro_wrapper(f, per_task_arg_list):

	async def inner(f, per_task_arg_list):
		try:
			tasks = [
				asyncio.create_task(f(arg)) for arg in per_task_arg_list
			]
			return await asyncio.gather(*tasks)
		except:
			for task in asyncio.all_tasks():
				if task != asyncio.current_task():
					task.cancel()
			raise

	inner_result_list = asyncio.run(inner(f, per_task_arg_list))
	ret_d = {}
	for (arg, inner_result,) in zip(per_task_arg_list, inner_result_list,):
		ret_d[arg] = inner_result

	return ret_d

def _bulk_obj_method_coro_wrapper(obj_list, coro_str, per_task_kwargs_list=None):

	async def inner(obj_list, coro_str, per_task_kwargs_list):
		try:
			tasks = []
			for (obj, kwargs,) in zip(obj_list, per_task_kwargs_list):
				obj_coro = getattr(obj, coro_str)
				tasks.append(
					asyncio.create_task(obj_coro(**kwargs))
				)
			return await asyncio.gather(*tasks)
		except:
			for task in asyncio.all_tasks():
				if task != asyncio.current_task():
					task.cancel()
			raise

	inner_kwargs_list = per_task_kwargs_list if per_task_kwargs_list else [{} for _ in obj_list]		
	inner_ret_list = asyncio.run(inner(obj_list, coro_str, inner_kwargs_list))
	ret_d = {}
	for (inner_ret, obj,) in zip(inner_ret_list, obj_list):
		k = str(id(obj))
		ret_d[k] = inner_ret

	return ret_d

