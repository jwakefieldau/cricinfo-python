Scrape cricinfo for stats.  

**Not officially supported by or affiliated with ESPNCricinfo in any way.  Use at own risk.  Don't be stupid with the rate limit**

Uses aiohttp and asyncio to speed up bulk requests.

```
>>> from cricinfo import Player
>>> from datetime import datetime
>>> datetime.now() ; search_l = Player.player_search('hobbs') ; datetime.now()
datetime.datetime(2021, 7, 31, 21, 34, 17, 713965)
datetime.datetime(2021, 7, 31, 21, 34, 18, 908795)
>>> datetime.now() ; search_d = Player.bulk_player_search(['hobbs', 'richards', 'bradman', 'pollock', 'sobers', 'gilchrist', 'warne', 'akram', 'marshall', 'lillee']) ; datetime.now()
datetime.datetime(2021, 7, 31, 21, 34, 50, 763356)
datetime.datetime(2021, 7, 31, 21, 34, 52, 682726)
```

TODO:
* expand on description
* provide more examples
* implement full match scorecards retrieval
* implement search/enumeration of teams, series