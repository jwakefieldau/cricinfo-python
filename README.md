Scrape cricinfo for stats.

Uses aiohttp and asyncio to speed up bulk requests.

TODO:
* refactor slightly so that each data retrieval method can either be run for one input
wrapped in a function, in bulk asynchronously with one task per input wrapped in a function,
or directly asynchronously from within the developer's own event loop.
* expand on description
* provide an example
* get player stats - Player has a PlayerStats instance?
* get player matches - Matches staticmethod returns a dict of Matches, Player gets a list of Match keys/IDs set