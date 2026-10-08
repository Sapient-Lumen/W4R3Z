# rev0013 SEARCH-RESP-01 source trace

The source bundle remains external to keep the cube compact. This trace records the line-level shape used by the current-behavior probe.

## github-tag-3.3.10

- `pynicotine/slskmessages.py` SHA-256: `152fba05c9ac127c9eb46c3aad834659e076744315fe034fc93d836b47f86fab`
- `pynicotine/search.py` SHA-256: `f511b700fe46374c2dd8d2efc1dbf3c0226f5a98b981b1add2490c174f0dc6b5`
- `pynicotine/gtkgui/search.py` SHA-256: `ac60fc08bf78e73be4c88790178ba31bcad28403dac7b52ea457a0a8046bae20`

### Token creation/increment

`pynicotine/slskmessages.py:57-72`

```text
   57: def initial_token():
   58:     """Return a random token in a large enough range to effectively prevent
   59:     conflicting tokens between sessions."""
   60:     return randint(0, UINT32_LIMIT // 1000)
   61: 
   62: 
   63: def increment_token(token):
   64:     """Increment a token used by file search, transfer and connection
   65:     requests."""
   66: 
   67:     if token < 0 or token >= UINT32_LIMIT:
   68:         # Protocol messages use unsigned integers for tokens
   69:         token = 0
   70: 
   71:     token += 1
   72:     return token
```

### Search request state and allowed-token gate

`pynicotine/search.py:149-162`

```text
  149:     def add_search(self, search_term, mode, room=None, users=None, is_ignored=False):
  150: 
  151:         term_sanitized, term_transmitted, included_words, excluded_words = self.sanitize_search_term(search_term)
  152: 
  153:         self.searches[self.token] = search = SearchRequest(
  154:             token=self.token, term=search_term, term_sanitized=term_sanitized, term_transmitted=term_transmitted,
  155:             included_words=included_words, excluded_words=excluded_words, mode=mode, room=room, users=users,
  156:             is_ignored=is_ignored
  157:         )
  158: 
  159:         if not is_ignored:
  160:             self.add_allowed_token(self.token)
  161: 
  162:         return search
```

### Search send paths

`pynicotine/search.py:303-360`

```text
  303:     def do_search(self, search_term, mode, room=None, users=None, switch_page=True):
  304: 
  305:         # Validate search term and run it through plugins
  306:         search_term, room, users = self.process_search_term(search_term, mode, room, users)
  307: 
  308:         # Get a new search token
  309:         self.token = increment_token(self.token)
  310:         search = self.add_search(search_term, mode, room, users)
  311: 
  312:         if config.sections["searches"]["enable_history"]:
  313:             items = config.sections["searches"]["history"]
  314: 
  315:             if search.term_sanitized in items:
  316:                 items.remove(search.term_sanitized)
  317: 
  318:             items.insert(0, search.term_sanitized)
  319: 
  320:             # Clear old items
  321:             del items[self.SEARCH_HISTORY_LIMIT:]
  322:             config.write_configuration()
  323: 
  324:         if mode == "global":
  325:             self.do_global_search(search.term_transmitted)
  326: 
  327:         elif mode == "rooms":
  328:             self.do_rooms_search(search.term_transmitted, room)
  329: 
  330:         elif mode == "buddies":
  331:             self.do_buddies_search(search.term_transmitted)
  332: 
  333:         elif mode == "user":
  334:             self.do_peer_search(search.term_transmitted, users)
  335: 
  336:         events.emit("add-search", search.token, search, switch_page)
  337: 
  338:     def do_global_search(self, text):
  339:         core.send_message_to_server(FileSearch(self.token, text))
  340: 
  341:         # Request a list of related searches from the server.
  342:         # Seemingly non-functional since 2018 (always receiving empty lists).
  343: 
  344:         # core.send_message_to_server(RelatedSearch(text))
  345: 
  346:     def do_rooms_search(self, text, room):
  347:         core.send_message_to_server(RoomSearch(room, self.token, text))
  348: 
  349:     def do_buddies_search(self, text):
  350:         for username in core.buddies.users:
  351:             core.send_message_to_server(UserSearch(username, self.token, text))
  352: 
  353:     def do_peer_search(self, text, users):
  354: 
  355:         for username in users:
  356:             if username == core.users.login_username:
  357:                 self._own_tokens.add(self.token)
  358: 
  359:             core.send_message_to_server(UserSearch(username, self.token, text))
  360: 
```

### FileSearchResponse parser token gate

`pynicotine/slskmessages.py:3280-3294`

```text
 3280:     def parse_network_message(self, message):
 3281:         decompressor = zlib.decompressobj()
 3282:         _pos, username_len = self.unpack_uint32(decompressor.decompress(message, 4))
 3283:         _pos, self.token = self.unpack_uint32(
 3284:             decompressor.decompress(decompressor.unconsumed_tail, username_len + 4), username_len)
 3285: 
 3286:         if self.token not in SEARCH_TOKENS_ALLOWED:
 3287:             # Results are no longer accepted for this search token, stop parsing message
 3288:             self.list = []
 3289:             return
 3290: 
 3291:         # Optimization: only decompress the rest of the message when needed
 3292:         self._parse_remaining_network_message(
 3293:             memoryview(decompressor.decompress(decompressor.unconsumed_tail))
 3294:         )
```

### FileSearchResponse handler gate

`pynicotine/search.py:452-474`

```text
  452:     def _file_search_response(self, msg):
  453:         """Peer code 9."""
  454: 
  455:         if msg.token not in SEARCH_TOKENS_ALLOWED:
  456:             msg.token = None
  457:             return
  458: 
  459:         search = self.searches.get(msg.token)
  460: 
  461:         if search is None or search.is_ignored:
  462:             msg.token = None
  463:             return
  464: 
  465:         username = msg.username
  466:         ip_address, _port = msg.addr
  467: 
  468:         if core.network_filter.is_user_ignored(username):
  469:             msg.token = None
  470:             return
  471: 
  472:         if core.network_filter.is_user_ip_ignored(username, ip_address):
  473:             msg.token = None
  474: 
```

### Private/public UI materialization order

`pynicotine/gtkgui/search.py:869-930`

```text
  869:     def file_search_response(self, msg):
  870: 
  871:         user = msg.username
  872: 
  873:         if user in self.users:
  874:             return
  875: 
  876:         self.initialized = True
  877: 
  878:         ip_address, _port = msg.addr
  879:         country_code = (
  880:             core.network_filter.get_country_code(ip_address)
  881:             or core.users.countries.get(user)
  882:         )
  883:         has_free_slots = msg.freeulslots
  884: 
  885:         if has_free_slots:
  886:             inqueue = 0
  887:             h_queue = ""
  888:         else:
  889:             inqueue = msg.inqueue or 1  # Ensure value is always >= 1
  890:             h_queue = humanize(inqueue)
  891: 
  892:         h_speed = ""
  893:         ulspeed = msg.ulspeed or 0
  894: 
  895:         if ulspeed > 0:
  896:             h_speed = human_speed(ulspeed)
  897: 
  898:         update_ui = self.add_result_list(msg.list, user, country_code, inqueue, ulspeed, h_speed,
  899:                                          h_queue, has_free_slots)
  900: 
  901:         if msg.privatelist and config.sections["searches"]["private_search_results"]:
  902:             update_ui_private = self.add_result_list(
  903:                 msg.privatelist, user, country_code, inqueue, ulspeed, h_speed, h_queue,
  904:                 has_free_slots, private=True
  905:             )
  906: 
  907:             if not update_ui and update_ui_private:
  908:                 update_ui = True
  909: 
  910:         if update_ui:
  911:             # If this search wasn't initiated by us (e.g. wishlist), and the results aren't spoofed, show tab
  912:             is_wish = (self.mode == "wishlist")
  913: 
  914:             if not self.show_page:
  915:                 self.searches.create_page(self.token, self.text)
  916:                 self.show_page = True
  917: 
  918:             tab_changed = self.searches.request_tab_changed(self.container, is_important=is_wish)
  919: 
  920:             if tab_changed and is_wish:
  921:                 self.window.update_title()
  922: 
  923:                 if config.sections["notifications"]["notification_popup_wish"]:
  924:                     core.notifications.show_search_notification(
  925:                         str(self.token), self.text,
  926:                         title=_("Wishlist Results Found")
  927:                     )
  928: 
  929:         # Update number of results, even if they are all filtered
  930:         self.update_result_counter()
```

## github-branch-3.3.x

- `pynicotine/slskmessages.py` SHA-256: `c0c237898334447a2ecb9d8d921586e35a7c1a399dedcb3ba038834657bf9e2e`
- `pynicotine/search.py` SHA-256: `ce1713545fc1ced95a48985635a2956d4e707575bc9ce467f12d0cdeb8c638f8`
- `pynicotine/gtkgui/search.py` SHA-256: `fb328feee5c776594a9e0350fc285a47f5df6c8c3f9bf009819bbd642b264b51`

### Token creation/increment

`pynicotine/slskmessages.py:57-72`

```text
   57: def initial_token():
   58:     """Return a random token in a large enough range to effectively prevent
   59:     conflicting tokens between sessions."""
   60:     return randint(0, UINT32_LIMIT // 1000)
   61: 
   62: 
   63: def increment_token(token):
   64:     """Increment a token used by file search, transfer and connection
   65:     requests."""
   66: 
   67:     if token < 0 or token >= UINT32_LIMIT:
   68:         # Protocol messages use unsigned integers for tokens
   69:         token = 0
   70: 
   71:     token += 1
   72:     return token
```

### Search request state and allowed-token gate

`pynicotine/search.py:149-162`

```text
  149:     def add_search(self, search_term, mode, room=None, users=None, is_ignored=False):
  150: 
  151:         term_sanitized, term_transmitted, included_words, excluded_words = self.sanitize_search_term(search_term)
  152: 
  153:         self.searches[self.token] = search = SearchRequest(
  154:             token=self.token, term=search_term, term_sanitized=term_sanitized, term_transmitted=term_transmitted,
  155:             included_words=included_words, excluded_words=excluded_words, mode=mode, room=room, users=users,
  156:             is_ignored=is_ignored
  157:         )
  158: 
  159:         if not is_ignored:
  160:             self.add_allowed_token(self.token)
  161: 
  162:         return search
```

### Search send paths

`pynicotine/search.py:303-360`

```text
  303:     def do_search(self, search_term, mode, room=None, users=None, switch_page=True):
  304: 
  305:         # Validate search term and run it through plugins
  306:         search_term, room, users = self.process_search_term(search_term, mode, room, users)
  307: 
  308:         # Get a new search token
  309:         self.token = increment_token(self.token)
  310:         search = self.add_search(search_term, mode, room, users)
  311: 
  312:         if config.sections["searches"]["enable_history"]:
  313:             items = config.sections["searches"]["history"]
  314: 
  315:             if search.term_sanitized in items:
  316:                 items.remove(search.term_sanitized)
  317: 
  318:             items.insert(0, search.term_sanitized)
  319: 
  320:             # Clear old items
  321:             del items[self.SEARCH_HISTORY_LIMIT:]
  322:             config.write_configuration()
  323: 
  324:         if mode == "global":
  325:             self.do_global_search(search.term_transmitted)
  326: 
  327:         elif mode == "rooms":
  328:             self.do_rooms_search(search.term_transmitted, room)
  329: 
  330:         elif mode == "buddies":
  331:             self.do_buddies_search(search.term_transmitted)
  332: 
  333:         elif mode == "user":
  334:             self.do_peer_search(search.term_transmitted, users)
  335: 
  336:         events.emit("add-search", search.token, search, switch_page)
  337: 
  338:     def do_global_search(self, text):
  339:         core.send_message_to_server(FileSearch(self.token, text))
  340: 
  341:         # Request a list of related searches from the server.
  342:         # Seemingly non-functional since 2018 (always receiving empty lists).
  343: 
  344:         # core.send_message_to_server(RelatedSearch(text))
  345: 
  346:     def do_rooms_search(self, text, room):
  347:         core.send_message_to_server(RoomSearch(room, self.token, text))
  348: 
  349:     def do_buddies_search(self, text):
  350:         for username in core.buddies.users:
  351:             core.send_message_to_server(UserSearch(username, self.token, text))
  352: 
  353:     def do_peer_search(self, text, users):
  354: 
  355:         for username in users:
  356:             if username == core.users.login_username:
  357:                 self._own_tokens.add(self.token)
  358: 
  359:             core.send_message_to_server(UserSearch(username, self.token, text))
  360: 
```

### FileSearchResponse parser token gate

`pynicotine/slskmessages.py:3308-3326`

```text
 3308:     def parse_network_message(self, message):
 3309:         decompressor = zlib.decompressobj()
 3310:         max_uncompressed_size = 134217728  # 128 MiB
 3311: 
 3312:         _pos, username_len = self.unpack_uint32(decompressor.decompress(message, 4))
 3313:         _pos, self.token = self.unpack_uint32(
 3314:             decompressor.decompress(decompressor.unconsumed_tail, username_len + 4), username_len)
 3315: 
 3316:         if self.token not in SEARCH_TOKENS_ALLOWED:
 3317:             # Results are no longer accepted for this search token, stop parsing message
 3318:             self.list = []
 3319:             return
 3320: 
 3321:         # Optimization: only decompress the rest of the message when needed
 3322:         decompressed_message = decompressor.decompress(decompressor.unconsumed_tail, max_uncompressed_size)
 3323: 
 3324:         if not decompressor.unconsumed_tail:
 3325:             self._parse_remaining_network_message(memoryview(decompressed_message))
 3326: 
```

### FileSearchResponse handler gate

`pynicotine/search.py:452-474`

```text
  452:     def _file_search_response(self, msg):
  453:         """Peer code 9."""
  454: 
  455:         if msg.token not in SEARCH_TOKENS_ALLOWED:
  456:             msg.token = None
  457:             return
  458: 
  459:         search = self.searches.get(msg.token)
  460: 
  461:         if search is None or search.is_ignored:
  462:             msg.token = None
  463:             return
  464: 
  465:         username = msg.username
  466:         ip_address, _port = msg.addr
  467: 
  468:         if core.network_filter.is_user_ignored(username):
  469:             msg.token = None
  470:             return
  471: 
  472:         if core.network_filter.is_user_ip_ignored(username, ip_address):
  473:             msg.token = None
  474: 
```

### Private/public UI materialization order

`pynicotine/gtkgui/search.py:872-933`

```text
  872:     def file_search_response(self, msg):
  873: 
  874:         user = msg.username
  875: 
  876:         if user in self.users:
  877:             return
  878: 
  879:         self.initialized = True
  880: 
  881:         ip_address, _port = msg.addr
  882:         country_code = (
  883:             core.network_filter.get_country_code(ip_address)
  884:             or core.users.countries.get(user)
  885:         )
  886:         has_free_slots = msg.freeulslots
  887: 
  888:         if has_free_slots:
  889:             inqueue = 0
  890:             h_queue = ""
  891:         else:
  892:             inqueue = msg.inqueue or 1  # Ensure value is always >= 1
  893:             h_queue = humanize(inqueue)
  894: 
  895:         h_speed = ""
  896:         ulspeed = msg.ulspeed or 0
  897: 
  898:         if ulspeed > 0:
  899:             h_speed = human_speed(ulspeed)
  900: 
  901:         update_ui = self.add_result_list(msg.list, user, country_code, inqueue, ulspeed, h_speed,
  902:                                          h_queue, has_free_slots)
  903: 
  904:         if msg.privatelist and config.sections["searches"]["private_search_results"]:
  905:             update_ui_private = self.add_result_list(
  906:                 msg.privatelist, user, country_code, inqueue, ulspeed, h_speed, h_queue,
  907:                 has_free_slots, private=True
  908:             )
  909: 
  910:             if not update_ui and update_ui_private:
  911:                 update_ui = True
  912: 
  913:         if update_ui:
  914:             # If this search wasn't initiated by us (e.g. wishlist), and the results aren't spoofed, show tab
  915:             is_wish = (self.mode == "wishlist")
  916: 
  917:             if not self.show_page:
  918:                 self.searches.create_page(self.token, self.text)
  919:                 self.show_page = True
  920: 
  921:             tab_changed = self.searches.request_tab_changed(self.container, is_important=is_wish)
  922: 
  923:             if tab_changed and is_wish:
  924:                 self.window.update_title()
  925: 
  926:                 if config.sections["notifications"]["notification_popup_wish"]:
  927:                     core.notifications.show_search_notification(
  928:                         str(self.token), self.text,
  929:                         title=_("Wishlist Results Found")
  930:                     )
  931: 
  932:         # Update number of results, even if they are all filtered
  933:         self.update_result_counter()
```

## github-branch-master

- `pynicotine/slskmessages.py` SHA-256: `43787bef158d35b27c7720ac19e89fa8e221f43df515cd73ce05ef494c1dfd78`
- `pynicotine/search.py` SHA-256: `b1210c415fc7a8a28e54d6ac424468a94509e87dfbd8c90d9c367d6d10b0f8d5`
- `pynicotine/gtkgui/search.py` SHA-256: `a30c2a83ca98fa8af88509298c1e2e56b4674fd6696e71da9d23175202c89db1`

### Token creation/increment

`pynicotine/slskmessages.py:46-61`

```text
   46: def initial_token():
   47:     """Return a random token in a large enough range to effectively prevent
   48:     conflicting tokens between sessions."""
   49:     return randint(0, UINT32_LIMIT // 1000)
   50: 
   51: 
   52: def increment_token(token):
   53:     """Increment a token used by file search, transfer and connection
   54:     requests."""
   55: 
   56:     if token < 0 or token >= UINT32_LIMIT:
   57:         # Protocol messages use unsigned integers for tokens
   58:         token = 0
   59: 
   60:     token += 1
   61:     return token
```

### Search request state and send gate

`pynicotine/search.py:220-276`

```text
  220:     # Outgoing Search Requests #
  221: 
  222:     @staticmethod
  223:     def add_allowed_token(token):
  224:         """Allow parsing search result messages for a search ID."""
  225:         core.send_message_to_network_thread(AddAllowedResponse(FileSearchResponse, token))
  226: 
  227:     @staticmethod
  228:     def remove_allowed_token(token):
  229:         """Disallow parsing search result messages for a search ID."""
  230:         core.send_message_to_network_thread(RemoveAllowedResponse(FileSearchResponse, token))
  231: 
  232:     def do_search(self, search_term, mode, room=None, users=None, switch_page=True):
  233: 
  234:         # Validate search term and run it through plugins
  235:         search_term, room, users = self._process_search_term(search_term, mode, room, users)
  236: 
  237:         # Get a new search token
  238:         self.token = increment_token(self.token)
  239:         search = self._add_search(self.token, search_term, mode, room, users)
  240: 
  241:         if config.sections["searches"]["enable_history"]:
  242:             items = config.sections["searches"]["history"]
  243: 
  244:             if search.term_sanitized in items:
  245:                 items.remove(search.term_sanitized)
  246: 
  247:             items.insert(0, search.term_sanitized)
  248: 
  249:             # Clear old items
  250:             del items[self.SEARCH_HISTORY_LIMIT:]
  251:             config.write_configuration()
  252: 
  253:         self.send_search_request(search.token)
  254:         events.emit("add-search", search.token, search, switch_page)
  255: 
  256:     def send_search_request(self, token):
  257: 
  258:         search = self.searches.get(token)
  259: 
  260:         if search is None:
  261:             return
  262: 
  263:         self.add_allowed_token(token)
  264: 
  265:         if search.mode in {"global", "wishlist"}:
  266:             self._send_global_search_request(search)
  267: 
  268:         elif search.mode == "rooms":
  269:             self._send_rooms_search_request(search)
  270: 
  271:         elif search.mode == "buddies":
  272:             self._send_buddies_search_request(search)
  273: 
  274:         elif search.mode == "user":
  275:             self._send_peer_search_request(search)
  276: 
```

### FileSearchResponse parser token gate

`pynicotine/slskmessages.py:3481-3500`

```text
 3481:     def parse_network_message(self):
 3482:         decompressor = zlib.decompressobj()
 3483:         max_uncompressed_size = 134217728  # 128 MiB
 3484: 
 3485:         self._offset = 0
 3486:         self._message = memoryview(decompressor.decompress(self._message, 4))
 3487:         self._offset = username_len = self.unpack_uint32()
 3488:         self._message = memoryview(decompressor.decompress(decompressor.unconsumed_tail, username_len + 4))
 3489:         self.token = self.unpack_uint32()
 3490: 
 3491:         if self.token not in self.allowed_responses:
 3492:             # Results are no longer accepted for this search token, stop parsing message
 3493:             return
 3494: 
 3495:         # Optimization: only decompress the rest of the message when needed
 3496:         self._offset = 0
 3497:         self._message = memoryview(decompressor.decompress(decompressor.unconsumed_tail, max_uncompressed_size))
 3498: 
 3499:         if not decompressor.unconsumed_tail:
 3500:             self._parse_remaining_network_message()
```

### FileSearchResponse handler gate

`pynicotine/search.py:615-642`

```text
  615:     def _file_search_response(self, msg):
  616:         """Peer code 9."""
  617: 
  618:         if msg.list is None:
  619:             # Response was rejected
  620:             msg.token = None
  621:             return
  622: 
  623:         search = self.searches.get(msg.token)
  624:         username = msg.username
  625: 
  626:         if search is None:
  627:             msg.token = None
  628:             return
  629: 
  630:         if isinstance(search, WishSearchRequest) and (search.is_ignored or username in search.ignored_users):
  631:             msg.token = None
  632:             return
  633: 
  634:         ip_address, _port = msg.addr
  635: 
  636:         if core.network_filter.is_user_ignored(username):
  637:             msg.token = None
  638:             return
  639: 
  640:         if core.network_filter.is_user_ip_ignored(username, ip_address):
  641:             msg.token = None
  642: 
```

### Private/public UI materialization order

`pynicotine/gtkgui/search.py:921-980`

```text
  921:     def file_search_response(self, msg):
  922: 
  923:         user = msg.username
  924: 
  925:         if user in self.users:
  926:             return
  927: 
  928:         self.initialized = True
  929: 
  930:         ip_address, _port = msg.addr
  931:         country_code = (
  932:             core.network_filter.get_country_code(ip_address)
  933:             or core.users.countries.get(user)
  934:         )
  935: 
  936:         if msg.freeulslots:
  937:             inqueue = 0
  938:             h_queue = ""
  939:         else:
  940:             inqueue = msg.inqueue or 1  # Ensure value is always >= 1
  941:             h_queue = humanize(inqueue)
  942: 
  943:         h_speed = ""
  944:         ulspeed = msg.ulspeed or 0
  945: 
  946:         if ulspeed > 0:
  947:             h_speed = human_speed(ulspeed)
  948: 
  949:         update_ui_private = False
  950: 
  951:         if msg.privatelist and config.sections["searches"]["private_search_results"]:
  952:             update_ui_private = self.add_result_list(
  953:                 msg.privatelist, user, country_code, inqueue, ulspeed, h_speed, h_queue,
  954:                 is_private=True
  955:             )
  956: 
  957:         update_ui = self.add_result_list(
  958:             msg.list, user, country_code, inqueue, ulspeed, h_speed, h_queue) or update_ui_private
  959: 
  960:         if update_ui:
  961:             # If this search wasn't initiated by us (e.g. wishlist), and the results aren't spoofed, show tab
  962:             is_wish = (self.mode == "wishlist")
  963: 
  964:             if not self.show_page:
  965:                 self.searches.create_page(self.token, self.text)
  966:                 self.show_page = True
  967: 
  968:             tab_changed = self.searches.request_tab_changed(self.container, is_important=is_wish)
  969: 
  970:             if tab_changed and is_wish:
  971:                 self.window.update_title()
  972: 
  973:                 if config.sections["notifications"]["notification_popup_wish"]:
  974:                     core.notifications.show_search_notification(
  975:                         str(self.token), self.text,
  976:                         title=_("Wishlist Results Found")
  977:                     )
  978: 
  979:         # Update number of results, even if they are all filtered
  980:         self.update_result_counter()
```
