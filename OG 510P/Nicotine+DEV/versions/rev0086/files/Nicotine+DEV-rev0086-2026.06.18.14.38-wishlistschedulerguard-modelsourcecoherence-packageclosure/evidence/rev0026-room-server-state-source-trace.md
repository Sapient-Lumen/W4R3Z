# rev0026 source trace — ROOM-SERVER-STATE-01 / U-111 + U-92
This trace is from the archived rev0003 source bundle extracted in the analysis workspace. The cube stores only snippets and hashes, not the large source bundle.
## Interpretation
- `parse_users()` indexes the already-created user list while consuming separately counted statuses/stats/slot/country arrays. Larger count arrays can raise `IndexError`; smaller arrays leave later users with default `None` fields.
- `RoomList` parses room names and user-count arrays as separate counted lists. Larger count arrays can raise `IndexError`; smaller count arrays leave room counts as `None`.
- The room-list UI path formats room counts with `humanize(user_count)`, so a surviving `None` count is not an acceptable normalized value.
- The network message unpacker catches generic parser exceptions, logs the failure, and drops the message instead of proving a fatal connection/client crash for high-count cases.

## github-tag-3.3.10

### pynicotine/slskmessages.py:600-640 — UsersMessage.parse_users parallel-array parser
```python
  600:         self.dirs = dirs
  601:         self.slotsfull = slotsfull
  602:         self.country = country
  603: 
  604: 
  605: class UsersMessage(SlskMessage):
  606:     __slots__ = ()
  607: 
  608:     @classmethod
  609:     def parse_users(cls, message, pos=0):
  610:         pos, numusers = cls.unpack_uint32(message, pos)
  611: 
  612:         users = []
  613:         for i in range(numusers):
  614:             users.append(UserData())
  615:             pos, users[i].username = cls.unpack_string(message, pos)
  616: 
  617:         pos, statuslen = cls.unpack_uint32(message, pos)
  618:         for i in range(statuslen):
  619:             pos, users[i].status = cls.unpack_uint32(message, pos)
  620: 
  621:         pos, statslen = cls.unpack_uint32(message, pos)
  622:         for i in range(statslen):
  623:             pos, users[i].avgspeed = cls.unpack_uint32(message, pos)
  624:             pos, users[i].uploadnum = cls.unpack_uint32(message, pos)
  625:             pos, users[i].unknown = cls.unpack_uint32(message, pos)
  626:             pos, users[i].files = cls.unpack_uint32(message, pos)
  627:             pos, users[i].dirs = cls.unpack_uint32(message, pos)
  628: 
  629:         pos, slotslen = cls.unpack_uint32(message, pos)
  630:         for i in range(slotslen):
  631:             pos, users[i].slotsfull = cls.unpack_uint32(message, pos)
  632: 
  633:         pos, countrylen = cls.unpack_uint32(message, pos)
  634:         for i in range(countrylen):
  635:             pos, users[i].country = cls.unpack_string(message, pos)
  636: 
  637:         return pos, users
  638: 
  639: 
  640: # Server Messages #
```

### pynicotine/slskmessages.py:900-965 — JoinRoom parser
```python
  900:         pos, self.room = self.unpack_string(message)
  901:         pos, self.user = self.unpack_string(message, pos)
  902:         pos, self.message = self.unpack_string(message, pos)
  903: 
  904: 
  905: class JoinRoom(ServerMessage):
  906:     """Server code 14.
  907: 
  908:     We send this message to the server when we want to join a room. If
  909:     the room doesn't exist, it is created.
  910: 
  911:     Server responds with this message when we join a room. Contains
  912:     users list with data on everyone.
  913: 
  914:     As long as we're in the room, the server will automatically send us
  915:     status/stat updates for room users, including ourselves, in the form
  916:     of GetUserStatus and GetUserStats messages.
  917: 
  918:     Room names must meet certain requirements, otherwise the server will
  919:     send a MessageUser message containing an error message. Requirements
  920:     include:
  921: 
  922:       - Non-empty string
  923:       - Only ASCII characters
  924:       - 24 characters or fewer
  925:       - No leading or trailing spaces
  926:       - No consecutive spaces
  927:     """
  928: 
  929:     __slots__ = ("room", "private", "owner", "users", "operators")
  930: 
  931:     def __init__(self, room=None, private=False):
  932:         self.room = room
  933:         self.private = private
  934:         self.owner = None
  935:         self.users = []
  936:         self.operators = []
  937: 
  938:     def make_network_message(self):
  939:         msg = bytearray()
  940:         msg += self.pack_string(self.room)
  941:         msg += self.pack_uint32(1 if self.private else 0)
  942: 
  943:         return msg
  944: 
  945:     def parse_network_message(self, message):
  946:         pos, self.room = self.unpack_string(message)
  947:         pos, self.users = UsersMessage.parse_users(message, pos)
  948: 
  949:         if message[pos:]:
  950:             self.private = True
  951:             pos, self.owner = self.unpack_string(message, pos)
  952: 
  953:         if message[pos:] and self.private:
  954:             pos, numops = self.unpack_uint32(message, pos)
  955: 
  956:             for _ in range(numops):
  957:                 pos, operator = self.unpack_string(message, pos)
  958: 
  959:                 self.operators.append(operator)
  960: 
  961: 
  962: class LeaveRoom(ServerMessage):
  963:     """Server code 15.
  964: 
  965:     We send this to the server when we want to leave a room.
```

### pynicotine/slskmessages.py:1650-1710 — RoomList parser
```python
 1650: class RoomList(ServerMessage):
 1651:     """Server code 64.
 1652: 
 1653:     The server tells us a list of rooms and the number of users in them.
 1654:     When connecting to the server, the server only sends us rooms with
 1655:     at least 5 users. A few select rooms are also excluded, such as
 1656:     nicotine and The Lobby. Requesting the room list yields a response
 1657:     containing the missing rooms.
 1658:     """
 1659: 
 1660:     __slots__ = ("rooms", "ownedprivaterooms", "otherprivaterooms", "operatedprivaterooms")
 1661: 
 1662:     def __init__(self):
 1663:         self.rooms = []
 1664:         self.ownedprivaterooms = []
 1665:         self.otherprivaterooms = []
 1666:         self.operatedprivaterooms = []
 1667: 
 1668:     def make_network_message(self):
 1669:         return b""
 1670: 
 1671:     def parse_network_message(self, message):
 1672:         pos, self.rooms = self.parse_rooms(message)
 1673:         pos, self.ownedprivaterooms = self.parse_rooms(message, pos)
 1674:         pos, self.otherprivaterooms = self.parse_rooms(message, pos)
 1675:         pos, self.operatedprivaterooms = self.parse_rooms(message, pos, has_count=False)
 1676: 
 1677:     def parse_rooms(self, message, pos=0, has_count=True):
 1678:         pos, numrooms = self.unpack_uint32(message, pos)
 1679: 
 1680:         rooms = []
 1681:         for i in range(numrooms):
 1682:             pos, room = self.unpack_string(message, pos)
 1683: 
 1684:             if has_count:
 1685:                 rooms.append([room, None])
 1686:             else:
 1687:                 rooms.append(room)
 1688: 
 1689:         if not has_count:
 1690:             return pos, rooms
 1691: 
 1692:         pos, numusers = self.unpack_uint32(message, pos)
 1693: 
 1694:         for i in range(numusers):
 1695:             pos, usercount = self.unpack_uint32(message, pos)
 1696: 
 1697:             rooms[i][1] = usercount
 1698: 
 1699:         return pos, rooms
 1700: 
 1701: 
 1702: class ExactFileSearch(ServerMessage):
 1703:     """Server code 65.
 1704: 
 1705:     We send this to search for an exact file name and folder, to find
 1706:     other sources.
 1707: 
 1708:     OBSOLETE, no results even with official client
 1709:     """
 1710: 
```

### pynicotine/gtkgui/popovers/roomlist.py:145-205 — RoomList add_room / update_room count formatting
```python
  145: 
  146:         return None
  147: 
  148:     def toggle_accept_private_room(self, active):
  149:         self.private_room_toggle.set_active(active)
  150: 
  151:     def add_room(self, room, user_count=0, is_private=False, is_owned=False):
  152: 
  153:         h_user_count = humanize(user_count)
  154: 
  155:         if is_private:
  156:             # Large internal value to sort private rooms first
  157:             user_count += self.PRIVATE_USERS_OFFSET
  158: 
  159:         text_weight = Pango.Weight.BOLD if is_private else Pango.Weight.NORMAL
  160:         text_underline = Pango.Underline.SINGLE if is_owned else Pango.Underline.NONE
  161: 
  162:         self.list_view.add_row([
  163:             room,
  164:             h_user_count,
  165:             user_count,
  166:             is_private,
  167:             text_weight,
  168:             text_underline
  169:         ], select_row=False)
  170: 
  171:     def update_room_user_count(self, room, user_count=None, decrement=False):
  172: 
  173:         iterator = self.list_view.iterators.get(room)
  174: 
  175:         if iterator is None:
  176:             return
  177: 
  178:         is_private = self.list_view.get_row_value(iterator, "is_private_data")
  179: 
  180:         if user_count is None:
  181:             user_count = self.list_view.get_row_value(iterator, "users_data")
  182: 
  183:             if decrement:
  184:                 if user_count > 0:
  185:                     user_count -= 1
  186:             else:
  187:                 user_count += 1
  188: 
  189:         elif is_private:
  190:             # Large internal value to sort private rooms first
  191:             user_count += self.PRIVATE_USERS_OFFSET
  192: 
  193:         h_user_count = humanize(user_count - self.PRIVATE_USERS_OFFSET) if is_private else humanize(user_count)
  194: 
  195:         self.list_view.set_row_values(
  196:             iterator,
  197:             column_ids=["users", "users_data"],
  198:             values=[h_user_count, user_count]
  199:         )
  200: 
  201:     def clear(self, *_args):
  202:         self.list_view.clear()
  203: 
  204:     def private_room_added(self, msg):
  205:         self.add_room(msg.room, is_private=True)
```

### pynicotine/gtkgui/popovers/roomlist.py:238-270 — RoomList event handler consumes parsed counts
```python
  238: 
  239:     def user_left_room(self, msg):
  240:         if msg.username != core.users.login_username:
  241:             self.update_room_user_count(msg.room, decrement=True)
  242: 
  243:     def room_list(self, msg):
  244: 
  245:         self.list_view.freeze()
  246:         self.clear()
  247: 
  248:         for room, user_count in msg.ownedprivaterooms:
  249:             self.add_room(room, user_count, is_private=True, is_owned=True)
  250: 
  251:         for room, user_count in msg.otherprivaterooms:
  252:             self.add_room(room, user_count, is_private=True)
  253: 
  254:         for room, user_count in msg.rooms:
  255:             self.add_room(room, user_count)
  256: 
  257:         self.list_view.unfreeze()
  258: 
  259:     def on_row_activated(self, *_args):
  260: 
  261:         room = self.get_selected_room()
  262: 
  263:         if room is not None:
  264:             self.popup_room = room
  265:             self.on_popup_join()
  266: 
  267:     def on_popup_menu(self, menu, _widget):
  268: 
  269:         room = self.get_selected_room()
  270:         self.popup_room = room
```

### pynicotine/slskproto.py:640-670 — NetworkThread message-unpack exception handling
```python
  640:     def _unpack_network_message(msg_class, msg_content, msg_size, conn_type, sock=None, addr=None, username=None):
  641: 
  642:         try:
  643:             msg = msg_class()
  644: 
  645:             if sock is not None:
  646:                 msg.sock = sock
  647: 
  648:             if addr is not None:
  649:                 msg.addr = addr
  650: 
  651:             if username is not None:
  652:                 msg.username = username
  653: 
  654:             msg.parse_network_message(msg_content)
  655:             return msg
  656: 
  657:         except Exception as error:
  658:             log.add_debug("Unable to parse %s message type %s, size %s, contents %s. Error: %s",
  659:                           (conn_type, msg_class, msg_size, msg_content, error))
  660: 
  661:         return None
  662: 
  663:     @staticmethod
  664:     def _unpack_embedded_message(msg):
  665:         """This message embeds a distributed message.
  666: 
  667:         We unpack the distributed message and process it.
  668:         """
  669: 
  670:         msg_type = msg.distrib_code
```

## github-branch-3.3.x

### pynicotine/slskmessages.py:611-651 — UsersMessage.parse_users parallel-array parser
```python
  611:         self.dirs = dirs
  612:         self.slotsfull = slotsfull
  613:         self.country = country
  614: 
  615: 
  616: class UsersMessage(SlskMessage):
  617:     __slots__ = ()
  618: 
  619:     @classmethod
  620:     def parse_users(cls, message, pos=0):
  621:         pos, numusers = cls.unpack_uint32(message, pos)
  622: 
  623:         users = []
  624:         for i in range(numusers):
  625:             users.append(UserData())
  626:             pos, users[i].username = cls.unpack_string(message, pos)
  627: 
  628:         pos, statuslen = cls.unpack_uint32(message, pos)
  629:         for i in range(statuslen):
  630:             pos, users[i].status = cls.unpack_uint32(message, pos)
  631: 
  632:         pos, statslen = cls.unpack_uint32(message, pos)
  633:         for i in range(statslen):
  634:             pos, users[i].avgspeed = cls.unpack_uint32(message, pos)
  635:             pos, users[i].uploadnum = cls.unpack_uint32(message, pos)
  636:             pos, users[i].unknown = cls.unpack_uint32(message, pos)
  637:             pos, users[i].files = cls.unpack_uint32(message, pos)
  638:             pos, users[i].dirs = cls.unpack_uint32(message, pos)
  639: 
  640:         pos, slotslen = cls.unpack_uint32(message, pos)
  641:         for i in range(slotslen):
  642:             pos, users[i].slotsfull = cls.unpack_uint32(message, pos)
  643: 
  644:         pos, countrylen = cls.unpack_uint32(message, pos)
  645:         for i in range(countrylen):
  646:             pos, users[i].country = cls.unpack_string(message, pos)
  647: 
  648:         return pos, users
  649: 
  650: 
  651: # Server Messages #
```

### pynicotine/slskmessages.py:911-976 — JoinRoom parser
```python
  911:         pos, self.room = self.unpack_string(message)
  912:         pos, self.user = self.unpack_string(message, pos)
  913:         pos, self.message = self.unpack_string(message, pos)
  914: 
  915: 
  916: class JoinRoom(ServerMessage):
  917:     """Server code 14.
  918: 
  919:     We send this message to the server when we want to join a room. If
  920:     the room doesn't exist, it is created.
  921: 
  922:     Server responds with this message when we join a room. Contains
  923:     users list with data on everyone.
  924: 
  925:     As long as we're in the room, the server will automatically send us
  926:     status/stat updates for room users, including ourselves, in the form
  927:     of GetUserStatus and GetUserStats messages.
  928: 
  929:     Room names must meet certain requirements, otherwise the server will
  930:     send a MessageUser message containing an error message. Requirements
  931:     include:
  932: 
  933:       - Non-empty string
  934:       - Only ASCII characters
  935:       - 24 characters or fewer
  936:       - No leading or trailing spaces
  937:       - No consecutive spaces
  938:     """
  939: 
  940:     __slots__ = ("room", "private", "owner", "users", "operators")
  941: 
  942:     def __init__(self, room=None, private=False):
  943:         self.room = room
  944:         self.private = private
  945:         self.owner = None
  946:         self.users = []
  947:         self.operators = []
  948: 
  949:     def make_network_message(self):
  950:         msg = bytearray()
  951:         msg += self.pack_string(self.room)
  952:         msg += self.pack_uint32(1 if self.private else 0)
  953: 
  954:         return msg
  955: 
  956:     def parse_network_message(self, message):
  957:         pos, self.room = self.unpack_string(message)
  958:         pos, self.users = UsersMessage.parse_users(message, pos)
  959: 
  960:         if message[pos:]:
  961:             self.private = True
  962:             pos, self.owner = self.unpack_string(message, pos)
  963: 
  964:         if message[pos:] and self.private:
  965:             pos, numops = self.unpack_uint32(message, pos)
  966: 
  967:             for _ in range(numops):
  968:                 pos, operator = self.unpack_string(message, pos)
  969: 
  970:                 self.operators.append(operator)
  971: 
  972: 
  973: class LeaveRoom(ServerMessage):
  974:     """Server code 15.
  975: 
  976:     We send this to the server when we want to leave a room.
```

### pynicotine/slskmessages.py:1661-1721 — RoomList parser
```python
 1661: class RoomList(ServerMessage):
 1662:     """Server code 64.
 1663: 
 1664:     The server tells us a list of rooms and the number of users in them.
 1665:     When connecting to the server, the server only sends us rooms with
 1666:     at least 5 users. A few select rooms are also excluded, such as
 1667:     nicotine and The Lobby. Requesting the room list yields a response
 1668:     containing the missing rooms.
 1669:     """
 1670: 
 1671:     __slots__ = ("rooms", "ownedprivaterooms", "otherprivaterooms", "operatedprivaterooms")
 1672: 
 1673:     def __init__(self):
 1674:         self.rooms = []
 1675:         self.ownedprivaterooms = []
 1676:         self.otherprivaterooms = []
 1677:         self.operatedprivaterooms = []
 1678: 
 1679:     def make_network_message(self):
 1680:         return b""
 1681: 
 1682:     def parse_network_message(self, message):
 1683:         pos, self.rooms = self.parse_rooms(message)
 1684:         pos, self.ownedprivaterooms = self.parse_rooms(message, pos)
 1685:         pos, self.otherprivaterooms = self.parse_rooms(message, pos)
 1686:         pos, self.operatedprivaterooms = self.parse_rooms(message, pos, has_count=False)
 1687: 
 1688:     def parse_rooms(self, message, pos=0, has_count=True):
 1689:         pos, numrooms = self.unpack_uint32(message, pos)
 1690: 
 1691:         rooms = []
 1692:         for i in range(numrooms):
 1693:             pos, room = self.unpack_string(message, pos)
 1694: 
 1695:             if has_count:
 1696:                 rooms.append([room, None])
 1697:             else:
 1698:                 rooms.append(room)
 1699: 
 1700:         if not has_count:
 1701:             return pos, rooms
 1702: 
 1703:         pos, numusers = self.unpack_uint32(message, pos)
 1704: 
 1705:         for i in range(numusers):
 1706:             pos, usercount = self.unpack_uint32(message, pos)
 1707: 
 1708:             rooms[i][1] = usercount
 1709: 
 1710:         return pos, rooms
 1711: 
 1712: 
 1713: class ExactFileSearch(ServerMessage):
 1714:     """Server code 65.
 1715: 
 1716:     We send this to search for an exact file name and folder, to find
 1717:     other sources.
 1718: 
 1719:     OBSOLETE, no results even with official client
 1720:     """
 1721: 
```

### pynicotine/gtkgui/popovers/roomlist.py:145-205 — RoomList add_room / update_room count formatting
```python
  145: 
  146:         return None
  147: 
  148:     def toggle_accept_private_room(self, active):
  149:         self.private_room_toggle.set_active(active)
  150: 
  151:     def add_room(self, room, user_count=0, is_private=False, is_owned=False):
  152: 
  153:         h_user_count = humanize(user_count)
  154: 
  155:         if is_private:
  156:             # Large internal value to sort private rooms first
  157:             user_count += self.PRIVATE_USERS_OFFSET
  158: 
  159:         text_weight = Pango.Weight.BOLD if is_private else Pango.Weight.NORMAL
  160:         text_underline = Pango.Underline.SINGLE if is_owned else Pango.Underline.NONE
  161: 
  162:         self.list_view.add_row([
  163:             room,
  164:             h_user_count,
  165:             user_count,
  166:             is_private,
  167:             text_weight,
  168:             text_underline
  169:         ], select_row=False)
  170: 
  171:     def update_room_user_count(self, room, user_count=None, decrement=False):
  172: 
  173:         iterator = self.list_view.iterators.get(room)
  174: 
  175:         if iterator is None:
  176:             return
  177: 
  178:         is_private = self.list_view.get_row_value(iterator, "is_private_data")
  179: 
  180:         if user_count is None:
  181:             user_count = self.list_view.get_row_value(iterator, "users_data")
  182: 
  183:             if decrement:
  184:                 if user_count > 0:
  185:                     user_count -= 1
  186:             else:
  187:                 user_count += 1
  188: 
  189:         elif is_private:
  190:             # Large internal value to sort private rooms first
  191:             user_count += self.PRIVATE_USERS_OFFSET
  192: 
  193:         h_user_count = humanize(user_count - self.PRIVATE_USERS_OFFSET) if is_private else humanize(user_count)
  194: 
  195:         self.list_view.set_row_values(
  196:             iterator,
  197:             column_ids=["users", "users_data"],
  198:             values=[h_user_count, user_count]
  199:         )
  200: 
  201:     def clear(self, *_args):
  202:         self.list_view.clear()
  203: 
  204:     def private_room_added(self, msg):
  205:         self.add_room(msg.room, is_private=True)
```

### pynicotine/gtkgui/popovers/roomlist.py:238-270 — RoomList event handler consumes parsed counts
```python
  238: 
  239:     def user_left_room(self, msg):
  240:         if msg.username != core.users.login_username:
  241:             self.update_room_user_count(msg.room, decrement=True)
  242: 
  243:     def room_list(self, msg):
  244: 
  245:         self.list_view.freeze()
  246:         self.clear()
  247: 
  248:         for room, user_count in msg.ownedprivaterooms:
  249:             self.add_room(room, user_count, is_private=True, is_owned=True)
  250: 
  251:         for room, user_count in msg.otherprivaterooms:
  252:             self.add_room(room, user_count, is_private=True)
  253: 
  254:         for room, user_count in msg.rooms:
  255:             self.add_room(room, user_count)
  256: 
  257:         self.list_view.unfreeze()
  258: 
  259:     def on_row_activated(self, *_args):
  260: 
  261:         room = self.get_selected_room()
  262: 
  263:         if room is not None:
  264:             self.popup_room = room
  265:             self.on_popup_join()
  266: 
  267:     def on_popup_menu(self, menu, _widget):
  268: 
  269:         room = self.get_selected_room()
  270:         self.popup_room = room
```

### pynicotine/slskproto.py:640-670 — NetworkThread message-unpack exception handling
```python
  640: 
  641:         return False
  642: 
  643:     def _find_local_ip_address(self):
  644: 
  645:         # Create a UDP socket
  646:         with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as local_socket:
  647: 
  648:             # Send a broadcast packet on a local address (doesn't need to be reachable,
  649:             # but MacOS requires port to be non-zero)
  650:             local_socket.connect_ex(("10.255.255.255", 1))
  651: 
  652:             # This returns the "primary" IP on the local box, even if that IP is a NAT/private/internal IP
  653:             ip_address = local_socket.getsockname()[0]
  654: 
  655:         return ip_address
  656: 
  657:     def _add_init_message(self, init):
  658: 
  659:         conn_type = init.conn_type
  660: 
  661:         if conn_type == ConnectionType.FILE:
  662:             # File transfer connections are not unique or reused later
  663:             return True
  664: 
  665:         init_key = init.target_user + conn_type
  666: 
  667:         if init_key not in self._username_init_msgs:
  668:             self._username_init_msgs[init_key] = init
  669:             return True
  670: 
```

## github-branch-master

### pynicotine/slskmessages.py:580-620 — UsersMessage.parse_users parallel-array parser
```python
  580: 
  581: 
  582: # Server Messages #
  583: 
  584: 
  585: class ServerMessage(SlskMessage):
  586:     __slots__ = ()
  587:     msg_type = MessageType.SERVER
  588: 
  589:     def parse_users(self):
  590:         numusers = self.unpack_uint32()
  591: 
  592:         users = []
  593:         for i in range(numusers):
  594:             users.append(UserData())
  595:             users[i].username = self.unpack_string()
  596: 
  597:         statuslen = self.unpack_uint32()
  598:         for i in range(statuslen):
  599:             users[i].status = self.unpack_uint32()
  600: 
  601:         statslen = self.unpack_uint32()
  602:         for i in range(statslen):
  603:             users[i].avgspeed = self.unpack_uint32()
  604:             users[i].uploadnum = self.unpack_uint32()
  605:             users[i].unknown = self.unpack_uint32()
  606:             users[i].files = self.unpack_uint32()
  607:             users[i].dirs = self.unpack_uint32()
  608: 
  609:         slotslen = self.unpack_uint32()
  610:         for i in range(slotslen):
  611:             users[i].slotsfull = self.unpack_uint32()
  612: 
  613:         countrylen = self.unpack_uint32()
  614:         for i in range(countrylen):
  615:             users[i].country = self.unpack_string()
  616: 
  617:         return users
  618: 
  619:     def populate_recommendations(self, recommendations, unrecommendations):
  620:         num = self.unpack_uint32()
```

### pynicotine/slskmessages.py:924-990 — JoinRoom parser
```python
  924:         self.room = self.unpack_string()
  925:         self.user = self.unpack_string()
  926:         self.message = self.unpack_string()
  927: 
  928: 
  929: class JoinRoom(ServerMessage):
  930:     """Server code 14.
  931: 
  932:     We send this message to the server when we want to join a room. If
  933:     the room doesn't exist, it is created.
  934: 
  935:     Server responds with this message when we join a room. Contains
  936:     users list with data on everyone.
  937: 
  938:     As long as we're in the room, the server will automatically send us
  939:     status/stat updates for room users, including ourselves, in the form
  940:     of GetUserStatus and GetUserStats messages.
  941: 
  942:     Room names must meet certain requirements, otherwise the server will
  943:     send a MessageUser message containing an error message. Requirements
  944:     include:
  945: 
  946:       - Non-empty string
  947:       - Only ASCII characters
  948:       - 24 characters or fewer
  949:       - No leading or trailing spaces
  950:       - No consecutive spaces
  951:     """
  952: 
  953:     __slots__ = ("room", "private", "owner", "users", "operators")
  954: 
  955:     def __init__(self, room=None, private=False, *, msg_content=None):
  956:         ServerMessage.__init__(self, msg_content)
  957:         self.room = room
  958:         self.private = private
  959:         self.owner = None
  960:         self.users = []
  961:         self.operators = []
  962: 
  963:     def make_network_message(self):
  964:         msg = bytearray()
  965:         msg += self.pack_string(self.room)
  966:         msg += self.pack_uint32(1 if self.private else 0)
  967: 
  968:         return msg
  969: 
  970:     def parse_network_message(self):
  971:         self.room = self.unpack_string()
  972:         self.users = self.parse_users()
  973: 
  974:         if not self.has_remaining_content():
  975:             return
  976: 
  977:         self.private = True
  978:         self.owner = self.unpack_string()
  979:         numops = self.unpack_uint32()
  980: 
  981:         for _ in range(numops):
  982:             operator = self.unpack_string()
  983:             self.operators.append(operator)
  984: 
  985: 
  986: class LeaveRoom(ServerMessage):
  987:     """Server code 15.
  988: 
  989:     We send this to the server when we want to leave a room.
  990:     """
```

### pynicotine/slskmessages.py:1724-1785 — RoomList parser
```python
 1724: class RoomList(ServerMessage):
 1725:     """Server code 64.
 1726: 
 1727:     The server tells us a list of rooms and the number of users in them.
 1728:     When connecting to the server, the server only sends us rooms with
 1729:     at least 5 users. A few select rooms are also excluded, such as
 1730:     nicotine and The Lobby. Requesting the room list yields a response
 1731:     containing the missing rooms.
 1732:     """
 1733: 
 1734:     __slots__ = ("rooms", "rooms_owner", "rooms_member", "rooms_operator")
 1735: 
 1736:     def __init__(self, *, msg_content=None):
 1737:         ServerMessage.__init__(self, msg_content)
 1738:         self.rooms = []
 1739:         self.rooms_owner = []
 1740:         self.rooms_member = []
 1741:         self.rooms_operator = []
 1742: 
 1743:     def make_network_message(self):
 1744:         return b""
 1745: 
 1746:     def parse_network_message(self):
 1747:         self.rooms = self.parse_rooms()
 1748:         self.rooms_owner = self.parse_rooms()
 1749:         self.rooms_member = self.parse_rooms()
 1750:         self.rooms_operator = self.parse_rooms(has_count=False)
 1751: 
 1752:     def parse_rooms(self, has_count=True):
 1753:         numrooms = self.unpack_uint32()
 1754: 
 1755:         rooms = []
 1756:         for i in range(numrooms):
 1757:             room = self.unpack_string()
 1758: 
 1759:             if has_count:
 1760:                 rooms.append([room, None])
 1761:             else:
 1762:                 rooms.append(room)
 1763: 
 1764:         if not has_count:
 1765:             return rooms
 1766: 
 1767:         numusers = self.unpack_uint32()
 1768: 
 1769:         for i in range(numusers):
 1770:             rooms[i][1] = self.unpack_uint32()
 1771: 
 1772:         return rooms
 1773: 
 1774: 
 1775: class ExactFileSearch(ServerMessage):
 1776:     """Server code 65.
 1777: 
 1778:     We send this to search for an exact file name and folder, to find
 1779:     other sources.
 1780: 
 1781:     OBSOLETE, no results even with official client
 1782:     """
 1783: 
 1784:     __slots__ = ("token", "file", "folder", "size", "checksum", "user", "unknown")
 1785: 
```

### pynicotine/gtkgui/dialogs/roomlist.py:128-185 — RoomList add_room / update_room count formatting
```python
  128: 
  129:         return None
  130: 
  131:     def toggle_room_invitations(self, active):
  132:         self.room_invitations_toggle.set_active(active)
  133: 
  134:     def add_room(self, room, user_count=0, is_private=False, is_owner=False):
  135: 
  136:         h_user_count = humanize(user_count)
  137: 
  138:         if is_private:
  139:             # Large internal value to sort private rooms first
  140:             user_count += self.PRIVATE_USERS_OFFSET
  141: 
  142:         text_weight = Pango.Weight.BOLD if is_private else Pango.Weight.NORMAL
  143:         text_underline = Pango.Underline.SINGLE if is_owner else Pango.Underline.NONE
  144: 
  145:         self.list_view.add_row([
  146:             room,
  147:             h_user_count,
  148:             user_count,
  149:             is_private,
  150:             text_weight,
  151:             text_underline
  152:         ], select_row=False)
  153: 
  154:         if not self.list_container.get_visible():
  155:             self.list_container.set_visible(True)
  156: 
  157:     def update_room_user_count(self, room, user_count=None, decrement=False):
  158: 
  159:         iterator = self.list_view.iterators.get(room)
  160: 
  161:         if iterator is None:
  162:             return
  163: 
  164:         is_private = self.list_view.get_row_value(iterator, "is_private_data")
  165: 
  166:         if user_count is None:
  167:             user_count = self.list_view.get_row_value(iterator, "users_data")
  168: 
  169:             if decrement:
  170:                 if user_count > 0:
  171:                     user_count -= 1
  172:             else:
  173:                 user_count += 1
  174: 
  175:         elif is_private:
  176:             # Large internal value to sort private rooms first
  177:             user_count += self.PRIVATE_USERS_OFFSET
  178: 
  179:         h_user_count = humanize(user_count - self.PRIVATE_USERS_OFFSET) if is_private else humanize(user_count)
  180: 
  181:         self.list_view.set_row_values(
  182:             iterator,
  183:             column_ids=["users", "users_data"],
  184:             values=[h_user_count, user_count]
  185:         )
```

### pynicotine/gtkgui/dialogs/roomlist.py:232-255 — RoomList event handler consumes parsed counts
```python
  232: 
  233:     def user_left_room(self, msg):
  234:         if msg.username != core.users.login_username:
  235:             self.update_room_user_count(msg.room, decrement=True)
  236: 
  237:     def room_list(self, msg):
  238: 
  239:         self.list_view.freeze()
  240:         self.clear()
  241: 
  242:         for room, user_count in msg.rooms_owner:
  243:             self.add_room(room, user_count, is_private=True, is_owner=True)
  244: 
  245:         for room, user_count in msg.rooms_member:
  246:             self.add_room(room, user_count, is_private=True)
  247: 
  248:         for room, user_count in msg.rooms:
  249:             self.add_room(room, user_count)
  250: 
  251:         self.list_view.unfreeze()
  252: 
  253:     def server_login(self, *_args):
  254:         self.create_room_button.set_sensitive(True)
  255: 
```

### pynicotine/slskproto.py:696-723 — NetworkThread message-unpack exception handling
```python
  696:     def _unpack_network_message(msg_class, msg_content, msg_size, conn_type, sock=None, addr=None, username=None,
  697:                                 allowed_responses=None):
  698: 
  699:         try:
  700:             msg = msg_class(msg_content=msg_content)
  701: 
  702:             if sock is not None:
  703:                 msg.sock = sock
  704: 
  705:             if addr is not None:
  706:                 msg.addr = addr
  707: 
  708:             if username is not None:
  709:                 msg.username = username
  710: 
  711:             if allowed_responses is not None:
  712:                 msg.allowed_responses = allowed_responses
  713: 
  714:             msg.parse_network_message()
  715:             return msg
  716: 
  717:         except Exception as error:
  718:             log.add_debug("Unable to parse %s message type %s, size %s, contents %s. Error: %s",
  719:                           (conn_type, msg_class, msg_size, msg_content, error))
  720: 
  721:         finally:
  722:             msg.finish_parsing()
  723: 
```
