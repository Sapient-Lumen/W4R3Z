# rev0017 source trace: PENDING-CONN-BUDGET-01 / U-181

This trace records the source-shape evidence used for the no-network pending-connection budget witness. The cube does not embed full source trees; these snippets are copied from the external rev0003 source bundle kept in workspace inventory.

## github-tag-3.3.10: `pynicotine/slskproto.py`

### lines 380-386

```python
  380: 
  381:         self._message_queue = deque()
  382:         self._pending_peer_conns = {}
  383:         self._pending_init_msgs = defaultdict(list)
  384:         self._token_init_msgs = {}
  385:         self._username_init_msgs = {}
  386:         self._user_addresses = {}
```

### lines 715-750

```python
  715:     def _send_message_to_peer(self, username, msg):
  716: 
  717:         conn_type = msg.msg_type
  718: 
  719:         if conn_type not in self.ALLOWED_PEER_CONN_TYPES:
  720:             log.add_conn("Unknown connection type %s", conn_type)
  721:             return
  722: 
  723:         init = None
  724:         init_key = username + conn_type
  725: 
  726:         # Check if there's already a connection for the specified username
  727:         if init_key in self._username_init_msgs:
  728:             init = self._username_init_msgs[init_key]
  729: 
  730:         if init is None and conn_type != ConnectionType.FILE and username in self._pending_init_msgs:
  731:             # Check if we have a pending PeerInit message (currently requesting user IP address)
  732:             for pending_init in self._pending_init_msgs[username]:
  733:                 if pending_init.conn_type == conn_type:
  734:                     init = pending_init
  735:                     break
  736: 
  737:         if init is not None:
  738:             log.add_conn("Sending message of type %s to user %s on existing connection",
  739:                          (msg.__class__, username))
  740: 
  741:             init.outgoing_msgs.append(msg)
  742: 
  743:             if init.sock is not None and self._conns[init.sock].is_established:
  744:                 # We have initiated a connection previously, and it's ready
  745:                 self._process_conn_messages(init)
  746: 
  747:         else:
  748:             log.add_conn("Sending message of type %s to user %s on new connection",
  749:                          (msg.__class__, username))
  750: 
```

### lines 754-780

```python
  754:     def _initiate_connection_to_peer(self, username, conn_type, msg=None, in_address=None):
  755:         """Prepare to initiate a connection with a peer."""
  756: 
  757:         init = PeerInit(init_user=self._server_username, target_user=username, conn_type=conn_type)
  758:         user_address = self._user_addresses.get(username)
  759: 
  760:         if in_address is not None:
  761:             user_address = in_address
  762: 
  763:         elif user_address is not None:
  764:             _ip_address, port = user_address
  765: 
  766:             if not port:
  767:                 # Port 0 means the user is likely bugged, ask the server for a new address
  768:                 user_address = None
  769: 
  770:         if msg is not None:
  771:             init.outgoing_msgs.append(msg)
  772: 
  773:         if user_address is None:
  774:             self._pending_init_msgs[username].append(init)
  775:             self._send_message_to_server(GetPeerAddress(username))
  776: 
  777:             log.add_conn("Requesting address for user %s", username)
  778:         else:
  779:             self._connect_to_peer(username, user_address, init)
  780: 
```

### lines 1300-1316

```python
 1300:         elif msg_class is GetPeerAddress:
 1301:             username = msg.user
 1302:             pending_init_msgs = self._pending_init_msgs.pop(msg.user, [])
 1303: 
 1304:             if not msg.port:
 1305:                 log.add_conn("Server reported port 0 for user %s", username)
 1306: 
 1307:             addr = (msg.ip_address, msg.port)
 1308:             user_offline = (msg.ip_address == "0.0.0.0")
 1309: 
 1310:             for init in pending_init_msgs:
 1311:                 # We now have the IP address for a user we previously didn't know,
 1312:                 # attempt a connection with the peer/user
 1313:                 if user_offline:
 1314:                     events.emit_main_thread(
 1315:                         "peer-connection-error", username=username, conn_type=init.conn_type,
 1316:                         msgs=init.outgoing_msgs[:], is_offline=True)
```

### lines 1694-1713

```python
 1694:     def _init_peer_connection(self, addr, init, response_token=None):
 1695: 
 1696:         if self._num_sockets >= self.MAX_SOCKETS:
 1697:             # Connection limit reached, re-queue
 1698:             self._pending_peer_conns[addr] = init
 1699:             return
 1700: 
 1701:         request_token = None
 1702:         _ip_address, port = addr
 1703:         self._pending_peer_conns.pop(addr, None)
 1704: 
 1705:         if response_token is None:
 1706:             # No token provided, we're not responding to an indirect connection request.
 1707:             # Request indirect connection from our end in case the user's port is closed.
 1708:             request_token = self._connect_to_peer_indirect(init)
 1709: 
 1710:         if port <= 0 or port > 65535:
 1711:             log.add_conn("Skipping direct connection attempt of type %s to user %s "
 1712:                          "due to invalid address %s", (init.conn_type, init.target_user, addr))
 1713:             return
```

## github-branch-3.3.x: `pynicotine/slskproto.py`

### lines 383-389

```python
  383: 
  384:         self._message_queue = deque()
  385:         self._pending_peer_conns = {}
  386:         self._pending_init_msgs = defaultdict(list)
  387:         self._token_init_msgs = {}
  388:         self._username_init_msgs = {}
  389:         self._user_addresses = {}
```

### lines 767-802

```python
  767:     def _send_message_to_peer(self, username, msg):
  768: 
  769:         conn_type = msg.msg_type
  770: 
  771:         if conn_type not in self.ALLOWED_PEER_CONN_TYPES:
  772:             log.add_conn("Unknown connection type %s", conn_type)
  773:             return
  774: 
  775:         init = None
  776:         init_key = username + conn_type
  777: 
  778:         # Check if there's already a connection for the specified username
  779:         if init_key in self._username_init_msgs:
  780:             init = self._username_init_msgs[init_key]
  781: 
  782:         if init is None and conn_type != ConnectionType.FILE and username in self._pending_init_msgs:
  783:             # Check if we have a pending PeerInit message (currently requesting user IP address)
  784:             for pending_init in self._pending_init_msgs[username]:
  785:                 if pending_init.conn_type == conn_type:
  786:                     init = pending_init
  787:                     break
  788: 
  789:         if init is not None:
  790:             log.add_conn("Sending message of type %s to user %s on existing connection",
  791:                          (msg.__class__, username))
  792: 
  793:             init.outgoing_msgs.append(msg)
  794: 
  795:             if init.sock is not None and self._conns[init.sock].is_established:
  796:                 # We have initiated a connection previously, and it's ready
  797:                 self._process_conn_messages(init)
  798: 
  799:         else:
  800:             log.add_conn("Sending message of type %s to user %s on new connection",
  801:                          (msg.__class__, username))
  802: 
```

### lines 806-832

```python
  806:     def _initiate_connection_to_peer(self, username, conn_type, msg=None, in_address=None):
  807:         """Prepare to initiate a connection with a peer."""
  808: 
  809:         init = PeerInit(init_user=self._server_username, target_user=username, conn_type=conn_type)
  810:         user_address = self._user_addresses.get(username)
  811: 
  812:         if in_address is not None:
  813:             user_address = in_address
  814: 
  815:         elif user_address is not None:
  816:             _ip_address, port = user_address
  817: 
  818:             if not port:
  819:                 # Port 0 means the user is likely bugged, ask the server for a new address
  820:                 user_address = None
  821: 
  822:         if msg is not None:
  823:             init.outgoing_msgs.append(msg)
  824: 
  825:         if user_address is None:
  826:             self._pending_init_msgs[username].append(init)
  827:             self._send_message_to_server(GetPeerAddress(username))
  828: 
  829:             log.add_conn("Requesting address for user %s", username)
  830:         else:
  831:             self._connect_to_peer(username, user_address, init)
  832: 
```

### lines 1380-1396

```python
 1380:         elif msg_class is GetPeerAddress:
 1381:             username = msg.user
 1382:             pending_init_msgs = self._pending_init_msgs.pop(msg.user, [])
 1383: 
 1384:             if not msg.port:
 1385:                 log.add_conn("Server reported port 0 for user %s", username)
 1386: 
 1387:             addr = (msg.ip_address, msg.port)
 1388:             user_offline = (msg.ip_address == "0.0.0.0")
 1389: 
 1390:             for init in pending_init_msgs:
 1391:                 # We now have the IP address for a user we previously didn't know,
 1392:                 # attempt a connection with the peer/user
 1393:                 if user_offline:
 1394:                     events.emit_main_thread(
 1395:                         "peer-connection-error", username=username, conn_type=init.conn_type,
 1396:                         msgs=init.outgoing_msgs[:], is_offline=True)
```

### lines 1776-1795

```python
 1776:     def _init_peer_connection(self, addr, init, response_token=None):
 1777: 
 1778:         if self._num_sockets >= self.MAX_SOCKETS:
 1779:             # Connection limit reached, re-queue
 1780:             self._pending_peer_conns[init] = (addr, response_token)
 1781:             return
 1782: 
 1783:         request_token = None
 1784:         _ip_address, port = addr
 1785:         self._pending_peer_conns.pop(init, None)
 1786: 
 1787:         if response_token is None:
 1788:             # No token provided, we're not responding to an indirect connection request.
 1789:             # Request indirect connection from our end in case the user's port is closed.
 1790:             request_token = self._connect_to_peer_indirect(init)
 1791: 
 1792:         if port <= 0 or port > 65535:
 1793:             log.add_conn("Skipping direct connection attempt of type %s to user %s "
 1794:                          "due to invalid address %s", (init.conn_type, init.target_user, addr))
 1795:             return
```

## github-branch-master: `pynicotine/slskproto.py`

### lines 383-389

```python
  383: 
  384:         self._message_queue = SimpleQueue()
  385:         self._pending_peer_conns = {}
  386:         self._pending_init_msgs = defaultdict(list)
  387:         self._indirect_token_init_msgs = {}
  388:         self._username_init_msgs = {}
  389:         self._user_addresses = {}
```

### lines 788-818

```python
  788:     def _send_message_to_peer(self, username, msg):
  789: 
  790:         init = None
  791:         conn_type = msg.msg_type
  792:         init_key = username + conn_type
  793: 
  794:         # Check if there's already a connection for the specified username
  795:         if init_key in self._username_init_msgs:
  796:             init = self._username_init_msgs[init_key]
  797: 
  798:         if init is None and conn_type != ConnectionType.FILE and username in self._pending_init_msgs:
  799:             # Check if we have a pending PeerInit message (currently requesting user IP address)
  800:             for pending_init in self._pending_init_msgs[username]:
  801:                 if pending_init.conn_type == conn_type:
  802:                     init = pending_init
  803:                     break
  804: 
  805:         if init is not None:
  806:             log.add_conn("Sending message of type %s to user %s on existing connection",
  807:                          (msg.__class__, username))
  808: 
  809:             init.outgoing_msgs.append(msg)
  810: 
  811:             if init.sock is not None and self._conns[init.sock].is_established:
  812:                 # We have initiated a connection previously, and it's ready
  813:                 self._process_conn_messages(init)
  814: 
  815:         else:
  816:             log.add_conn("Sending message of type %s to user %s on new connection",
  817:                          (msg.__class__, username))
  818: 
```

### lines 822-868

```python
  822:     def _initiate_connection_to_peer(self, username, conn_type, msg=None, in_address=None):
  823:         """Prepare to initiate a connection with a peer."""
  824: 
  825:         indirect_token = self._indirect_token = increment_token(self._indirect_token)
  826:         init = PeerInit(
  827:             init_user=self._server_username, target_user=username, conn_type=conn_type,
  828:             indirect_token=indirect_token
  829:         )
  830:         addr = None
  831: 
  832:         if in_address is not None:
  833:             addr = in_address
  834: 
  835:         elif username in self._user_addresses:
  836:             user_address = self._user_addresses[username]
  837: 
  838:             if user_address is not None:
  839:                 addr = user_address.addr
  840:                 _ip_address, port = addr
  841: 
  842:                 if not port:
  843:                     # Port 0 likely means the server hasn't received the user's port yet.
  844:                     # Ask the server for a new address.
  845:                     addr = None
  846: 
  847:                 elif (username != self._server_username
  848:                         and (time.monotonic() - user_address.last_update) > self.USER_ADDRESS_TTL):
  849:                     # Certain clients may prefer sending a listening port update to the server without
  850:                     # reconnecting. Make sure we request the user's port again every now and then.
  851:                     log.add_conn("User %s's address expired, requesting new one", username)
  852:                     addr = None
  853: 
  854:         if msg is not None:
  855:             init.outgoing_msgs.append(msg)
  856: 
  857:         self._indirect_token_init_msgs[indirect_token] = init
  858:         self._send_message_to_server(ConnectToPeer(indirect_token, username, conn_type))
  859: 
  860:         log.add_conn("Requesting indirect connection to user %s with token %s", (username, indirect_token))
  861: 
  862:         if addr is None:
  863:             self._pending_init_msgs[username].append(init)
  864:             self._send_message_to_server(GetPeerAddress(username))
  865: 
  866:             log.add_conn("Requesting address for user %s", username)
  867:         else:
  868:             self._connect_to_peer(username, addr, init)
```

### lines 1416-1432

```python
 1416:         elif msg_class is GetPeerAddress:
 1417:             username = msg.user
 1418:             pending_init_msgs = self._pending_init_msgs.pop(msg.user, [])
 1419: 
 1420:             if not msg.port:
 1421:                 log.add_conn("Server reported port 0 for user %s", username)
 1422: 
 1423:             addr = (msg.ip_address, msg.port)
 1424:             user_offline = (msg.ip_address == "0.0.0.0")
 1425: 
 1426:             for init in pending_init_msgs:
 1427:                 # We now have the IP address for a user we previously didn't know,
 1428:                 # attempt a connection with the peer/user
 1429:                 if user_offline:
 1430:                     events.emit_main_thread(
 1431:                         "peer-connection-error", username=username, conn_type=init.conn_type,
 1432:                         msgs=init.outgoing_msgs[:], is_offline=True)
```

### lines 1818-1831

```python
 1818:     def _init_peer_connection(self, addr, init, pierce_token=None):
 1819: 
 1820:         if self._num_sockets >= self.MAX_SOCKETS:
 1821:             # Connection limit reached, re-queue
 1822:             self._pending_peer_conns[init] = (addr, pierce_token)
 1823:             return
 1824: 
 1825:         _ip_address, port = addr
 1826:         self._pending_peer_conns.pop(init, None)
 1827: 
 1828:         if port <= 0 or port > 65535:
 1829:             log.add_conn("Skipping direct connection attempt of type %s to user %s "
 1830:                          "due to invalid address %s", (init.conn_type, init.target_user, addr))
 1831:             return
```
