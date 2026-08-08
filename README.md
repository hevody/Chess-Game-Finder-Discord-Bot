trivia: if you reach 2100 Rapid, you'll be in the Top 1000 in the Philippines

resource for feat_FindPageOfEloUsingBinarySearchv2.py: https://github.com/TheAlgorithms/Python/blob/master/searches/binary_search.py

constraints:
The code currently supports Filipino players only for simplicity, it can easily be fixed in the following versions
also only discover rapid games but can easily be fixed in the future updates

plan: port to termux, so the bot can run even on mobile (port the program using `requests`)

does not work with bughouse

MAJOR BUG: Rate limited 
`requests.exceptions.ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))`

made cache usernames database just in case we got rate limited

you can also use the  `./cache/cache_usernames.db`, just move it into the databases and rename it
for example, `cache_username.db` to `1500-1600 PH Range Usernames.db`
