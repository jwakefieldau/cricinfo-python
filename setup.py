from distutils.core import setup

setup(
	name='cricinfo-python',
	version='0.1',
	description='Asynchronous scraper for cricinfo.',
	requires=[
		'aiohttp (>=3.7.4)',
		'aiodns (>=3.0.0)',
		'beautifulsoup4 (>=4.9.3)',
	],
	packages=['cricinfo']
)