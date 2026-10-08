# Source-anchor capsule — SEARCH-RESP-01C-ROOM

These anchors were generated from the external rev0003 source bundle. They support source review of the existing production-gated packet and do not promote a new packet.

|lane|anchor|file:line|role|matched text|
|---|---|---|---|---|
|github-tag-3.3.10|sr01c-request-state-mode-room|pynicotine/search.py:46|SearchRequest stores room/mode state for room-source gating|`"mode", "room", "users", "is_ignored")`|
|github-branch-3.3.x|sr01c-request-state-mode-room|pynicotine/search.py:46|SearchRequest stores room/mode state for room-source gating|`"mode", "room", "users", "is_ignored")`|
|github-branch-master|sr01c-request-state-mode-room|pynicotine/search.py:46|SearchRequest stores room/mode state for room-source gating|`"mode", "room", "users")`|
|github-tag-3.3.10|sr01c-add-search-state|pynicotine/search.py:153|room search token state creation point|`self.searches[self.token] = search = SearchRequest(`|
|github-branch-3.3.x|sr01c-add-search-state|pynicotine/search.py:153|room search token state creation point|`self.searches[self.token] = search = SearchRequest(`|
|github-branch-master|sr01c-add-search-state|pynicotine/search.py:366|room search token state creation point|`self.searches[token] = search = SearchRequest(`|
|github-tag-3.3.10|sr01c-room-fanout-entry|pynicotine/search.py:346|room-mode search request path|`def do_rooms_search(self, text, room):`|
|github-branch-3.3.x|sr01c-room-fanout-entry|pynicotine/search.py:346|room-mode search request path|`def do_rooms_search(self, text, room):`|
|github-branch-master|sr01c-room-fanout-entry|pynicotine/search.py:507|room-mode search request path|`def _send_rooms_search_request(self, search):`|
|github-tag-3.3.10|sr01c-room-message-send|pynicotine/search.py:347|RoomSearch is sent through server-mediated room path|`core.send_message_to_server(RoomSearch(room, self.token, text))`|
|github-branch-3.3.x|sr01c-room-message-send|pynicotine/search.py:347|RoomSearch is sent through server-mediated room path|`core.send_message_to_server(RoomSearch(room, self.token, text))`|
|github-branch-master|sr01c-room-message-send|pynicotine/search.py:508|RoomSearch is sent through server-mediated room path|`core.send_message_to_server(RoomSearch(search.room, search.token, search.term_transmitted))`|
|github-tag-3.3.10|sr01c-response-token-lookup|pynicotine/search.py:459|room response admission shares token lookup path|`search = self.searches.get(msg.token)`|
|github-branch-3.3.x|sr01c-response-token-lookup|pynicotine/search.py:459|room response admission shares token lookup path|`search = self.searches.get(msg.token)`|
|github-branch-master|sr01c-response-token-lookup|pynicotine/search.py:623|room response admission shares token lookup path|`search = self.searches.get(msg.token)`|
|github-tag-3.3.10|sr01c-response-username-read|pynicotine/search.py:465|response username available for room-source gating|`username = msg.username`|
|github-branch-3.3.x|sr01c-response-username-read|pynicotine/search.py:465|response username available for room-source gating|`username = msg.username`|
|github-branch-master|sr01c-response-username-read|pynicotine/search.py:624|response username available for room-source gating|`username = msg.username`|

## Filing guardrail

Use these anchors with the rev0050 minimum-claim capsule. Do not broaden the claim based on file proximity or shared modules.
