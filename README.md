Scrape cricinfo for stats.  

**Not officially supported by or affiliated with ESPNCricinfo in any way.  Use at own risk.  Don't be stupid with the rate limit**

Uses aiohttp and asyncio to speed up bulk requests.

```
>>> from cricinfo import Player
>>> from datetime import datetime
>>> datetime.now() ; search_d = Player.bulk_player_search(['hobbs', 'richards', 'bradman', 'pollock', 'sobers', 'gilchrist', 'warne', 'akram', 'marshall', 'lillee']) ; datetime.now()
datetime.datetime(2021, 7, 30, 21, 2, 44, 526993)
datetime.datetime(2021, 7, 30, 21, 3, 6, 153498)
>>> datetime.now() ; search_l = Player.player_search('hobbs') ; datetime.now()
datetime.datetime(2021, 7, 30, 21, 3, 54, 575114)
datetime.datetime(2021, 7, 30, 21, 4, 10, 843830)
>>> 
```

TODO:
* expand on description
* provide more examples
* get player stats - Player has a PlayerStats instance?
* get player matches - Matches staticmethod returns a dict of Matches, Player gets a list of Match keys/IDs set