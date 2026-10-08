# Source-anchor capsule — SEARCH-RESP-01A

These anchors were generated from the external rev0003 source bundle. They support source review of the existing production-gated packet and do not promote a new packet.

|lane|anchor|file:line|role|matched text|
|---|---|---|---|---|
|github-tag-3.3.10|sr01a-request-state-mode-users|pynicotine/search.py:46|SearchRequest stores source-mode and user/room fields|`"mode", "room", "users", "is_ignored")`|
|github-branch-3.3.x|sr01a-request-state-mode-users|pynicotine/search.py:46|SearchRequest stores source-mode and user/room fields|`"mode", "room", "users", "is_ignored")`|
|github-branch-master|sr01a-request-state-mode-users|pynicotine/search.py:46|SearchRequest stores source-mode and user/room fields|`"mode", "room", "users")`|
|github-tag-3.3.10|sr01a-add-search-state|pynicotine/search.py:153|search token is associated with mode/users state|`self.searches[self.token] = search = SearchRequest(`|
|github-branch-3.3.x|sr01a-add-search-state|pynicotine/search.py:153|search token is associated with mode/users state|`self.searches[self.token] = search = SearchRequest(`|
|github-branch-master|sr01a-add-search-state|pynicotine/search.py:366|search token is associated with mode/users state|`self.searches[token] = search = SearchRequest(`|
|github-tag-3.3.10|sr01a-user-fanout-entry|pynicotine/search.py:353|direct user-search fanout path|`def do_peer_search(self, text, users):`|
|github-branch-3.3.x|sr01a-user-fanout-entry|pynicotine/search.py:353|direct user-search fanout path|`def do_peer_search(self, text, users):`|
|github-branch-master|sr01a-user-fanout-entry|pynicotine/search.py:514|direct user-search fanout path|`def _send_peer_search_request(self, search):`|
|github-tag-3.3.10|sr01a-user-fanout-users|pynicotine/search.py:355|UserSearch fanout iterates original requested users|`for username in users:`|
|github-branch-3.3.x|sr01a-user-fanout-users|pynicotine/search.py:355|UserSearch fanout iterates original requested users|`for username in users:`|
|github-branch-master|sr01a-user-fanout-users|pynicotine/search.py:516|UserSearch fanout iterates original requested users|`for username in search.users:`|
|github-tag-3.3.10|sr01a-response-token-lookup|pynicotine/search.py:459|FileSearchResponse is admitted by token lookup before source checks|`search = self.searches.get(msg.token)`|
|github-branch-3.3.x|sr01a-response-token-lookup|pynicotine/search.py:459|FileSearchResponse is admitted by token lookup before source checks|`search = self.searches.get(msg.token)`|
|github-branch-master|sr01a-response-token-lookup|pynicotine/search.py:623|FileSearchResponse is admitted by token lookup before source checks|`search = self.searches.get(msg.token)`|
|github-tag-3.3.10|sr01a-response-username-read|pynicotine/search.py:465|response username is available for source binding|`username = msg.username`|
|github-branch-3.3.x|sr01a-response-username-read|pynicotine/search.py:465|response username is available for source binding|`username = msg.username`|
|github-branch-master|sr01a-response-username-read|pynicotine/search.py:624|response username is available for source binding|`username = msg.username`|

## Filing guardrail

Use these anchors with the rev0050 minimum-claim capsule. Do not broaden the claim based on file proximity or shared modules.
