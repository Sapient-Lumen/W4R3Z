# rev0006 source trace — peer/request binding and transfer lifecycle

External source policy: rev0006 continues to **reference** the rev0003 upstream source bundle and does not embed it.

Source bundle lanes used locally:

```text
[
  {
    "lane": "github-tag-3.3.10",
    "purpose": "current stable tag/source baseline",
    "commit": "caf9e101a841ff2e0a96aebc8e07bbf7ff1b2026",
    "source_tree_path_in_external_bundle": "Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z/source-trees/github-tag-3.3.10/",
    "local_analysis_workspace_path": "/mnt/data/nicotine_dev_external_source_inventory/Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z/source-trees/github-tag-3.3.10",
    "file_count": "678",
    "python_file_count": "142",
    "ui_file_count": "37",
    "total_bytes": "14577303",
    "tree_content_sha256": "8a46f2332b5285661c1e84b39734f92c1059779f5db71ca9c22fd0d165e08266",
    "included_in_rev0004_zip": "no - external source reference only"
  },
  {
    "lane": "github-branch-3.3.x",
    "purpose": "supported 3.3.x / release-candidate maintenance lane",
    "commit": "98089ac233aa57786e8dbdc48123f6ac1c4767d8",
    "source_tree_path_in_external_bundle": "Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z/source-trees/github-branch-3.3.x/",
    "local_analysis_workspace_path": "/mnt/data/nicotine_dev_external_source_inventory/Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z/source-trees/github-branch-3.3.x",
    "file_count": "684",
    "python_file_count": "145",
    "ui_file_count": "37",
    "total_bytes": "14625090",
    "tree_content_sha256": "21ee9f6d66274eb4d34358a0d9a544df2e63a4944f1cef922a8a8ba69f7935d9",
    "included_in_rev0004_zip": "no - external source reference only"
  },
  {
    "lane": "github-branch-master",
    "purpose": "future/default development lane",
    "commit": "f4e17d59783dbc48ea31d2e899a681e2dd1ed500",
    "source_tree_path_in_external_bundle": "Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z/source-trees/github-branch-master/",
    "local_analysis_workspace_path": "/mnt/data/nicotine_dev_external_source_inventory/Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z/source-trees/github-branch-master",
    "file_count": "777",
    "python_file_count": "152",
    "ui_file_count": "38",
    "total_bytes": "17403157",
    "tree_content_sha256": "f6ec307a5249191220b4f1c7b904c35e5d9cc37fc5969ec52675d90f07c30432",
    "included_in_rev0004_zip": "no - external source reference only"
  }
]
```

## U-123 — duplicate transfer token overwrite

### 3.3.10 transfer activation sink

`github-tag-3.3.10/pynicotine/transfers.py:527-547`

```text
  527:     def _activate_transfer(self, transfer, token):
  528: 
  529:         core.users.watch_user(transfer.username, context=self._name)
  530: 
  531:         transfer.status = TransferStatus.GETTING_STATUS
  532:         transfer.token = token
  533:         transfer.speed = transfer.avg_speed = 0
  534:         transfer.queue_position = 0
  535: 
  536:         # When our port is closed, certain clients can take up to ~30 seconds before they
  537:         # initiate a 'F' connection, since they only send an indirect connection request after
  538:         # attempting to connect to our port for a certain time period.
  539:         # Known clients: Nicotine+ 2.2.0 - 3.2.0, 2 s; Soulseek NS, ~20 s; soulseeX, ~30 s.
  540:         # To account for potential delays while initializing the connection, add 15 seconds
  541:         # to the timeout value.
  542: 
  543:         transfer.request_timer_id = events.schedule(
  544:             delay=45, callback=self._transfer_timeout, callback_args=(transfer,))
  545: 
  546:         self.active_users[transfer.username][token] = transfer
  547: 
```

`github-tag-3.3.10/pynicotine/downloads.py:1063-1097`

```text
 1063:     def _transfer_request_downloads(self, msg):
 1064: 
 1065:         username = msg.username
 1066:         virtual_path = msg.file
 1067:         size = msg.filesize
 1068:         token = msg.token
 1069: 
 1070:         log.add_transfer("Received download request with token %s for file %s from user %s",
 1071:                          (token, virtual_path, username))
 1072: 
 1073:         download = (self.queued_users.get(username, {}).get(virtual_path)
 1074:                     or self.failed_users.get(username, {}).get(virtual_path))
 1075: 
 1076:         if download is not None:
 1077:             # Remote peer is signaling a transfer is ready, attempting to download it
 1078: 
 1079:             # If the file is larger than 2GB, the SoulseekQt client seems to
 1080:             # send a malformed file size (0 bytes) in the TransferRequest response.
 1081:             # In that case, we rely on the cached, correct file size we received when
 1082:             # we initially added the download.
 1083: 
 1084:             self._unfail_transfer(download)
 1085:             self._dequeue_transfer(download)
 1086: 
 1087:             if size > 0:
 1088:                 if download.size != size:
 1089:                     # The remote user's file contents have changed since we queued the download
 1090:                     download.size_changed = True
 1091: 
 1092:                 download.size = size
 1093: 
 1094:             self._activate_transfer(download, token)
 1095:             self._update_transfer(download)
 1096: 
 1097:             return TransferResponse(allowed=True, token=token)
```

### master still has the same active-user/token assignment shape

`github-branch-master/pynicotine/transfers.py:528-547`

```text
  528:     def _activate_transfer(self, transfer, token):
  529: 
  530:         core.users.watch_user(transfer.username, context=self._name)
  531: 
  532:         transfer.status = TransferStatus.GETTING_STATUS
  533:         transfer.token = token
  534:         transfer.speed = transfer.avg_speed = 0
  535:         transfer.queue_position = 0
  536: 
  537:         # When our port is closed, certain clients can take up to ~30 seconds before they
  538:         # initiate a 'F' connection, since they only send an indirect connection request after
  539:         # attempting to connect to our port for a certain time period.
  540:         # Known clients: Nicotine+ 2.2.0 - 3.2.0, 2 s; Soulseek NS, ~20 s; soulseeX, ~30 s.
  541:         # To account for potential delays while initializing the connection, add 15 seconds
  542:         # to the timeout value.
  543: 
  544:         transfer.request_timer_id = events.schedule(
  545:             delay=45, callback=self._transfer_timeout, callback_args=(transfer,))
  546: 
  547:         self.active_users[transfer.username][token] = transfer
```

Minimal microprobe output is stored in `evidence/rev0006-u123-duplicate-token-microprobe.jsonl`. It activates two transfers for the same user with token `4242`; in all three source lanes the second transfer replaces the first in `active_users["alice"][4242]`, while the first retains a token and timer but is no longer indexed.

## U-168 / U-176 — PeerInit replacement and secondary promotion

`github-tag-3.3.10/pynicotine/slskproto.py:865-883`

```text
  865:     def _replace_existing_connection(self, init):
  866: 
  867:         username = init.target_user
  868:         conn_type = init.conn_type
  869: 
  870:         if username == self._server_username:
  871:             return
  872: 
  873:         prev_init = self._username_init_msgs.pop(username + conn_type, None)
  874: 
  875:         if prev_init is None or prev_init.sock is None:
  876:             return
  877: 
  878:         log.add_conn("Discarding existing connection of type %s to user %s", (init.conn_type, username))
  879: 
  880:         init.outgoing_msgs = prev_init.outgoing_msgs
  881:         prev_init.outgoing_msgs = []
  882: 
  883:         self._close_connection(self._conns[prev_init.sock])
```

`github-tag-3.3.10/pynicotine/slskproto.py:1565-1580`

```text
 1565:         elif msg_class is PeerInit:
 1566:             username = msg.target_user
 1567:             conn_type = msg.conn_type
 1568:             addr = conn.addr
 1569: 
 1570:             log.add_conn("Received incoming direct connection of type %s from user "
 1571:                          "%s, address %s", (conn_type, username, addr))
 1572: 
 1573:             if conn_type not in self.ALLOWED_PEER_CONN_TYPES:
 1574:                 log.add_conn("Unknown connection type %s", conn_type)
 1575:                 return None
 1576: 
 1577:             init = msg
 1578:             self._replace_existing_connection(init)
 1579: 
 1580:         self._emit_network_message_event(msg)
```

`github-tag-3.3.10/pynicotine/slskproto.py:2521-2550`

```text
 2521:     def _process_conn_incoming_messages(self, conn):
 2522: 
 2523:         if not conn.in_buffer:
 2524:             return
 2525: 
 2526:         if conn is self._server_conn:
 2527:             self._process_server_input(conn)
 2528:             return
 2529: 
 2530:         init = conn.init
 2531: 
 2532:         if init is None:
 2533:             conn.init = init = self._process_peer_init_input(conn)
 2534: 
 2535:             if init is None or not conn.in_buffer:
 2536:                 return
 2537: 
 2538:         if init.conn_type == ConnectionType.PEER:
 2539:             self._process_peer_input(conn)
 2540: 
 2541:         elif init.conn_type == ConnectionType.FILE:
 2542:             self._process_file_input(conn)
 2543: 
 2544:         elif init.conn_type == ConnectionType.DISTRIBUTED:
 2545:             self._process_distrib_input(conn)
 2546: 
 2547:         if conn.sock is not None and init.sock is not conn.sock:
 2548:             log.add_conn("Received message on secondary connection of type %s to user %s, "
 2549:                          "promoting to primary connection", (init.conn_type, init.target_user))
 2550:             init.sock = conn.sock
```

`github-branch-master/pynicotine/slskproto.py:935-953`

```text
  935:     def _replace_existing_connection(self, init):
  936: 
  937:         username = init.target_user
  938:         conn_type = init.conn_type
  939: 
  940:         if username == self._server_username:
  941:             return
  942: 
  943:         prev_init = self._username_init_msgs.pop(username + conn_type, None)
  944: 
  945:         if prev_init is None or prev_init.sock is None:
  946:             return
  947: 
  948:         log.add_conn("Discarding existing connection of type %s to user %s", (init.conn_type, username))
  949: 
  950:         init.outgoing_msgs = prev_init.outgoing_msgs
  951:         prev_init.outgoing_msgs = []
  952: 
  953:         self._close_connection(self._conns[prev_init.sock])
```

`github-branch-master/pynicotine/slskproto.py:2702-2731`

```text
 2702:     def _process_conn_incoming_messages(self, conn):
 2703: 
 2704:         if not conn.in_buffer:
 2705:             return
 2706: 
 2707:         if conn is self._server_conn:
 2708:             self._process_server_input(conn)
 2709:             return
 2710: 
 2711:         init = conn.init
 2712: 
 2713:         if init is None:
 2714:             conn.init = init = self._process_peer_init_input(conn)
 2715: 
 2716:             if init is None or not conn.in_buffer:
 2717:                 return
 2718: 
 2719:         if init.conn_type == ConnectionType.PEER:
 2720:             self._process_peer_input(conn)
 2721: 
 2722:         elif init.conn_type == ConnectionType.FILE:
 2723:             self._process_file_input(conn)
 2724: 
 2725:         elif init.conn_type == ConnectionType.DISTRIBUTED:
 2726:             self._process_distrib_input(conn)
 2727: 
 2728:         if conn.sock is not None and init.sock is not conn.sock:
 2729:             log.add_conn("Received message on secondary connection of type %s to user %s, "
 2730:                          "promoting to primary connection", (init.conn_type, init.target_user))
 2731:             init.sock = conn.sock
```

Observation: replacement and secondary-promotion primitives remain visible in the future lane, so the issue family deserves a dynamic state-machine test. However, public/upstream spoofed-user fixes overlap the broad theme, so strict-document promotion remains blocked.

## U-165 — indirect PierceFireWall token bearer shape

`github-tag-3.3.10/pynicotine/slskproto.py:827-840`

```text
  827:     def _connect_to_peer_indirect(self, init):
  828:         """Send a message to the server to ask the peer to connect to us
  829:         (indirect connection)"""
  830: 
  831:         username = init.target_user
  832:         conn_type = init.conn_type
  833:         token = self._token = increment_token(self._token)
  834:         request_time = time.monotonic()
  835: 
  836:         self._token_init_msgs[token] = (init, request_time)
  837:         self._send_message_to_server(ConnectToPeer(token, username, conn_type))
  838: 
  839:         log.add_conn("Requesting indirect connection to user %s with token %s", (username, token))
  840:         return token
```

`github-tag-3.3.10/pynicotine/slskproto.py:1532-1555`

```text
 1532:         if msg_class is PierceFireWall:
 1533:             token = msg.token
 1534:             log.add_conn("Received indirect connection response (PierceFireWall) with token "
 1535:                          "%s, address %s", (token, conn.addr))
 1536: 
 1537:             log.add_conn("Number of stored peer init message tokens: %s", len(self._token_init_msgs))
 1538: 
 1539:             if token not in self._token_init_msgs:
 1540:                 log.add_conn("Indirect connection attempt with token %s previously expired, "
 1541:                              "closing connection", token)
 1542:                 return None
 1543: 
 1544:             init, _request_time = self._token_init_msgs.pop(token)
 1545:             previous_sock = init.sock
 1546:             is_direct_conn_in_progress = (
 1547:                 previous_sock is not None and not self._conns[previous_sock].is_established
 1548:             )
 1549: 
 1550:             log.add_conn("Indirect connection to user %s with token %s established",
 1551:                          (init.target_user, token))
 1552: 
 1553:             if previous_sock is None or is_direct_conn_in_progress:
 1554:                 init.sock = conn.sock
 1555:                 log.add_conn("Using as primary connection, since no direct connection is established")
```

`github-branch-master/pynicotine/slskproto.py:1653-1666`

```text
 1653:         if msg_class is PierceFireWall:
 1654:             pierce_token = msg.token
 1655:             log.add_conn("Received indirect connection response (PierceFireWall) with token "
 1656:                          "%s, address %s", (pierce_token, conn.addr))
 1657: 
 1658:             log.add_conn("Number of stored peer init message tokens: %s", len(self._indirect_token_init_msgs))
 1659: 
 1660:             if pierce_token not in self._indirect_token_init_msgs:
 1661:                 log.add_conn("Indirect connection attempt with token %s previously expired, "
 1662:                              "closing connection", pierce_token)
 1663:                 return None
 1664: 
 1665:             init = self._indirect_token_init_msgs.pop(pierce_token)
 1666:             previous_sock = init.sock
```

Observation: master refactors the storage name/shape, but the token still functions as the central bearer claim. This is not enough by itself for a strict finding because timing, reachability, and public-overlap need proof.

## U-171 / U-181 — server-driven address and pending-message buffers

`github-tag-3.3.10/pynicotine/slskproto.py:715-779`

```text
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
  751:             # This is a new peer, initiate a connection
  752:             self._initiate_connection_to_peer(username, conn_type, msg)
  753: 
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
```

`github-tag-3.3.10/pynicotine/slskproto.py:1276-1286`

```text
 1276:         elif msg_class is ConnectToPeer:
 1277:             username = msg.user
 1278:             addr = (msg.ip_address, msg.port)
 1279:             conn_type = msg.conn_type
 1280:             token = msg.token
 1281:             init = PeerInit(init_user=username, target_user=username, conn_type=conn_type)
 1282: 
 1283:             log.add_conn("Received indirect connection request of type %s from user %s, "
 1284:                          "token %s, address %s", (conn_type, username, token, addr))
 1285: 
 1286:             self._connect_to_peer(username, addr, init, response_token=token)
```

`github-tag-3.3.10/pynicotine/slskproto.py:1694-1735`

```text
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
 1714: 
 1715:         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 1716:         io_events = selectors.EVENT_READ | selectors.EVENT_WRITE
 1717:         conn = PeerConnection(
 1718:             sock=sock, addr=addr, io_events=io_events,
 1719:             init=init, request_token=request_token, response_token=response_token
 1720:         )
 1721: 
 1722:         sock.setblocking(False)
 1723:         sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
 1724: 
 1725:         try:
 1726:             self._bind_socket_interface(sock)
 1727:             sock.connect_ex(addr)
 1728: 
 1729:         except OSError as error:
 1730:             self._connect_error(error, conn)
 1731:             self._close_socket(sock)
 1732:             return
 1733: 
 1734:         init.sock = sock
 1735:         self._conns[sock] = conn
```

`github-branch-master/pynicotine/slskproto.py:1389-1400`

```text
 1389:         elif msg_class is ConnectToPeer:
 1390:             username = msg.user
 1391:             addr = (msg.ip_address, msg.port)
 1392:             conn_type = msg.conn_type
 1393:             pierce_token = msg.token
 1394: 
 1395:             log.add_conn("Received indirect connection request of type %s from user %s, "
 1396:                          "token %s, address %s", (conn_type, username, pierce_token, addr))
 1397: 
 1398:             if conn_type in self.ALLOWED_PEER_CONN_TYPES:
 1399:                 init = PeerInit(target_user=username, conn_type=conn_type)
 1400:                 self._connect_to_peer(username, addr, init, pierce_token=pierce_token)
```

`github-branch-master/pynicotine/slskproto.py:1818-1831`

```text
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

Observation: port validation exists, but the sampled source does not show a reserved/internal address-class policy or per-user/global pending-message cap in these paths. This remains malicious-server/MITM scoped and therefore lower disclosure urgency than peer-only issues.

## U-217 — UserInfoResponse allowed-response gate changed in master

`github-branch-master/pynicotine/slskmessages.py:246-268`

```text
  246: class AddAllowedResponse(InternalMessage):
  247:     """Sent to the networking thread to indicate that we're expecting a message response
  248:     with a certain ID (username, token, etc). More heavy tasks can be performed for allowed
  249:     responses, such as decompression.
  250:     """
  251: 
  252:     __slots__ = ("msg_class", "response_id")
  253: 
  254:     def __init__(self, msg_class, response_id):
  255:         self.msg_class = msg_class
  256:         self.response_id = response_id
  257: 
  258: 
  259: class RemoveAllowedResponse(InternalMessage):
  260:     """Sent to the networking thread to indicate that we're no longer expecting a message
  261:     response with a certain ID (username, token, etc).
  262:     """
  263: 
  264:     __slots__ = ("msg_class", "response_id")
  265: 
  266:     def __init__(self, msg_class, response_id):
  267:         self.msg_class = msg_class
  268:         self.response_id = response_id
```

`github-branch-master/pynicotine/userinfo.py:125-137`

```text
  125:         if username == local_username:
  126:             msg = self._get_user_info_response()
  127:             events.emit("user-info-response", msg)
  128:         else:
  129:             # Request user description, picture and queue information
  130:             core.send_message_to_network_thread(AddAllowedResponse(UserInfoResponse, username))
  131:             core.send_message_to_peer(username, UserInfoRequest())
  132: 
  133:     def remove_user(self, username):
  134: 
  135:         self.users.remove(username)
  136:         core.send_message_to_network_thread(RemoveAllowedResponse(UserInfoResponse, username))
  137:         core.users.unwatch_user(username, context="userinfo")
```

`github-branch-master/pynicotine/slskproto.py:1873-1883`

```text
 1873:             if msg_type in PEER_MESSAGE_CLASSES:
 1874:                 msg_class = PEER_MESSAGE_CLASSES[msg_type]
 1875: 
 1876:             if msg_class is SharedFileListResponse or msg_class is UserInfoResponse:
 1877:                 max_msg_size = self.MAX_INCOMING_MESSAGE_SIZE_LARGE
 1878: 
 1879:                 if conn.init.target_user not in self._allowed_message_responses[msg_class]:
 1880:                     # Since these responses tend to be large, close the connection when receiving
 1881:                     # unsolicited messages to save bandwidth.
 1882:                     self._close_connection(conn)
 1883:                     return
```

Observation: U-217 is not a clean current/future finding as originally phrased. Master added an allowed-response gate for large UserInfoResponse handling keyed by username. A narrower residual source/generation-binding question may remain, but it needs a new proof and should not be reported as “no gate in master.”
