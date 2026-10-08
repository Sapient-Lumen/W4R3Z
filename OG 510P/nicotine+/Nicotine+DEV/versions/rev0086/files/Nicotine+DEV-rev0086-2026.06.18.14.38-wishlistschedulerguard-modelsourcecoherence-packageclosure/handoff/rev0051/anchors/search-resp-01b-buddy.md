# Source-anchor capsule — SEARCH-RESP-01B-BUDDY

These anchors were generated from the external rev0003 source bundle. They support source review of the existing production-gated packet and do not promote a new packet.

|lane|anchor|file:line|role|matched text|
|---|---|---|---|---|
|github-tag-3.3.10|sr01b-request-state-mode-users|pynicotine/search.py:46|SearchRequest source-mode state reused by buddy-source snapshot fix|`"mode", "room", "users", "is_ignored")`|
|github-branch-3.3.x|sr01b-request-state-mode-users|pynicotine/search.py:46|SearchRequest source-mode state reused by buddy-source snapshot fix|`"mode", "room", "users", "is_ignored")`|
|github-branch-master|sr01b-request-state-mode-users|pynicotine/search.py:46|SearchRequest source-mode state reused by buddy-source snapshot fix|`"mode", "room", "users")`|
|github-tag-3.3.10|sr01b-add-search-state|pynicotine/search.py:153|search token state creation point for snapshot storage|`self.searches[self.token] = search = SearchRequest(`|
|github-branch-3.3.x|sr01b-add-search-state|pynicotine/search.py:153|search token state creation point for snapshot storage|`self.searches[self.token] = search = SearchRequest(`|
|github-branch-master|sr01b-add-search-state|pynicotine/search.py:366|search token state creation point for snapshot storage|`self.searches[token] = search = SearchRequest(`|
|github-tag-3.3.10|sr01b-buddy-fanout-entry|pynicotine/search.py:349|buddy-mode fanout path|`def do_buddies_search(self, text):`|
|github-branch-3.3.x|sr01b-buddy-fanout-entry|pynicotine/search.py:349|buddy-mode fanout path|`def do_buddies_search(self, text):`|
|github-branch-master|sr01b-buddy-fanout-entry|pynicotine/search.py:510|buddy-mode fanout path|`def _send_buddies_search_request(self, search):`|
|github-tag-3.3.10|sr01b-buddy-current-users|pynicotine/search.py:350|archived source fans out over current buddy map rather than request-time snapshot|`for username in core.buddies.users:`|
|github-branch-3.3.x|sr01b-buddy-current-users|pynicotine/search.py:350|archived source fans out over current buddy map rather than request-time snapshot|`for username in core.buddies.users:`|
|github-branch-master|sr01b-buddy-current-users|pynicotine/search.py:511|archived source fans out over current buddy map rather than request-time snapshot|`for username in core.buddies.users:`|
|github-tag-3.3.10|sr01b-response-token-lookup|pynicotine/search.py:459|buddy response admission shares token lookup path|`search = self.searches.get(msg.token)`|
|github-branch-3.3.x|sr01b-response-token-lookup|pynicotine/search.py:459|buddy response admission shares token lookup path|`search = self.searches.get(msg.token)`|
|github-branch-master|sr01b-response-token-lookup|pynicotine/search.py:623|buddy response admission shares token lookup path|`search = self.searches.get(msg.token)`|
|github-tag-3.3.10|sr01b-response-username-read|pynicotine/search.py:465|response username available for buddy-source gating|`username = msg.username`|
|github-branch-3.3.x|sr01b-response-username-read|pynicotine/search.py:465|response username available for buddy-source gating|`username = msg.username`|
|github-branch-master|sr01b-response-username-read|pynicotine/search.py:624|response username available for buddy-source gating|`username = msg.username`|

## Filing guardrail

Use these anchors with the rev0050 minimum-claim capsule. Do not broaden the claim based on file proximity or shared modules.
