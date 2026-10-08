# rev0035 strict/front source trace

The source trace rechecked line-level anchors for the three strict/front candidates across the archived lanes. It is intentionally an anchor map, not a full source copy.

## U-123 — github-tag-3.3.10 — `pynicotine/transfers.py`

sha256: `78e864766dd96a33a790b571eb44a8f052c9ee1064fcb99f98c798900ba29db7`

- line 527: `def _activate_transfer(self, transfer, token):`
- line 546: `self.active_users[transfer.username][token] = transfer`
- line 548: `def _deactivate_transfer(self, transfer):`
- line 556: `del self.active_users[username][token]`

## U-123 — github-tag-3.3.10 — `pynicotine/downloads.py`

sha256: `d4cf926ce5d24b8dc8bfd394edf83c9a9386844c41ee3a768622818cd73e6ddd`

- line 1131: `def _transfer_timeout(self, transfer):`
- line 1152: `def _file_transfer_init(self, msg):`
- line 1144: `download = self.active_users.get(username, {}).get(token)`

## PB-01 — github-tag-3.3.10 — `pynicotine/slskproto.py`

sha256: `7faf9082bd41593ec1c85dd0b876c44f17ae89a12d49b337413b937798b0350c`

- line 865: `def _replace_existing_connection(self, init):`
- line 873: `prev_init = self._username_init_msgs.pop(username + conn_type, None)`
- line 883: `self._close_connection(self._conns[prev_init.sock])`
- line 2549: `"promoting to primary connection", (init.conn_type, init.target_user))`
- line 846: `sock = init.sock = conn.sock`

## SEARCH-RESP-01 — github-tag-3.3.10 — `pynicotine/search.py`

sha256: `f511b700fe46374c2dd8d2efc1dbf3c0226f5a98b981b1add2490c174f0dc6b5`

- line 452: `def _file_search_response(self, msg):`
- line 459: `search = self.searches.get(msg.token)`
- line 468: `if core.network_filter.is_user_ignored(username):`
- line 472: `if core.network_filter.is_user_ip_ignored(username, ip_address):`

## SEARCH-RESP-01 — github-tag-3.3.10 — `pynicotine/slskmessages.py`

sha256: `152fba05c9ac127c9eb46c3aad834659e076744315fe034fc93d836b47f86fab`

- line 3234: `class FileSearchResponse(PeerMessage):`
- line 687: `def parse_network_message(self, message):`
- line 205: `self.token = token`
- line 166: `self.listen_port = listen_port`

## U-123 — github-branch-3.3.x — `pynicotine/transfers.py`

sha256: `61e3c42c9f761d171c716892cd4832ef98fd6fd05cb45d553c0d7c3f132a4e55`

- line 530: `def _activate_transfer(self, transfer, token):`
- line 549: `self.active_users[transfer.username][token] = transfer`
- line 551: `def _deactivate_transfer(self, transfer):`
- line 559: `del self.active_users[username][token]`

## U-123 — github-branch-3.3.x — `pynicotine/downloads.py`

sha256: `e1d6697fde4b520d7aed76f9e565857abfe8d2a9edd87e1eed2bb2ef7cda01d4`

- line 1142: `def _transfer_timeout(self, transfer):`
- line 1163: `def _file_transfer_init(self, msg):`
- line 1155: `download = self.active_users.get(username, {}).get(token)`
- line 1176: `core.send_message_to_network_thread(CloseConnection(msg.sock))`

## PB-01 — github-branch-3.3.x — `pynicotine/slskproto.py`

sha256: `b468bf99f3c035830ab0b0694220b84e35b03a70d92a49337dc11c7693a15bec`

- line 917: `def _replace_existing_connection(self, init):`
- line 925: `prev_init = self._username_init_msgs.pop(username + conn_type, None)`
- line 935: `self._close_connection(self._conns[prev_init.sock])`
- line 2606: `"promoting to primary connection", (init.conn_type, init.target_user))`
- line 898: `sock = init.sock = conn.sock`

## SEARCH-RESP-01 — github-branch-3.3.x — `pynicotine/search.py`

sha256: `ce1713545fc1ced95a48985635a2956d4e707575bc9ce467f12d0cdeb8c638f8`

- line 452: `def _file_search_response(self, msg):`
- line 459: `search = self.searches.get(msg.token)`
- line 468: `if core.network_filter.is_user_ignored(username):`
- line 472: `if core.network_filter.is_user_ip_ignored(username, ip_address):`

## SEARCH-RESP-01 — github-branch-3.3.x — `pynicotine/slskmessages.py`

sha256: `c0c237898334447a2ecb9d8d921586e35a7c1a399dedcb3ba038834657bf9e2e`

- line 3262: `class FileSearchResponse(PeerMessage):`
- line 698: `def parse_network_message(self, message):`
- line 205: `self.token = token`
- line 166: `self.listen_port = listen_port`

## U-123 — github-branch-master — `pynicotine/transfers.py`

sha256: `e8f04ede0635635f4eaf3445afa5ae417677af3489f3c306f9d1e43bc7e0a2cd`

- line 528: `def _activate_transfer(self, transfer, token):`
- line 547: `self.active_users[transfer.username][token] = transfer`
- line 549: `def _deactivate_transfer(self, transfer):`
- line 557: `del self.active_users[username][token]`

## U-123 — github-branch-master — `pynicotine/downloads.py`

sha256: `0638a8dbcdef278baa4ccc3f81ff2438834d93501f4f845d8aa91f786b8aa2ca`

- line 1113: `def _transfer_timeout(self, transfer):`
- line 1134: `def _file_transfer_init(self, msg):`
- line 1126: `download = self.active_users.get(username, {}).get(token)`
- line 1147: `core.send_message_to_network_thread(CloseConnection(msg.sock))`

## PB-01 — github-branch-master — `pynicotine/slskproto.py`

sha256: `46addf59c69e2b2ede74ccc99657d1df2a78aaedba07861b7ea1a41ad58dbb7e`

- line 935: `def _replace_existing_connection(self, init):`
- line 943: `prev_init = self._username_init_msgs.pop(username + conn_type, None)`
- line 953: `self._close_connection(self._conns[prev_init.sock])`
- line 2730: `"promoting to primary connection", (init.conn_type, init.target_user))`
- line 916: `sock = init.sock = conn.sock`

## SEARCH-RESP-01 — github-branch-master — `pynicotine/search.py`

sha256: `b1210c415fc7a8a28e54d6ac424468a94509e87dfbd8c90d9c367d6d10b0f8d5`

- line 615: `def _file_search_response(self, msg):`
- line 623: `search = self.searches.get(msg.token)`
- line 636: `if core.network_filter.is_user_ignored(username):`
- line 640: `if core.network_filter.is_user_ip_ignored(username, ip_address):`

## SEARCH-RESP-01 — github-branch-master — `pynicotine/slskmessages.py`

sha256: `43787bef158d35b27c7720ac19e89fa8e221f43df515cd73ce05ef494c1dfd78`

- line 3435: `class FileSearchResponse(PeerMessage):`
- line 692: `def parse_network_message(self):`
- line 208: `self.token = token`
- line 169: `self.listen_port = listen_port`
