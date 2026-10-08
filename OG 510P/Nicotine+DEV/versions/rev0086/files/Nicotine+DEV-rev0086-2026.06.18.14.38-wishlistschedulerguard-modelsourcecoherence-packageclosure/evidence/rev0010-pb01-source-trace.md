# rev0010 PB-01 source trace
Compact excerpts from the external rev0003 source lanes. The full source bundle is intentionally not embedded.

## github-tag-3.3.10 — _replace_existing_connection
`pynicotine/slskproto.py:863-898`

```text
863:         self._process_conn_messages(init)
864: 
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
884: 
885:     @staticmethod
886:     def _close_socket(sock):
887: 
888:         try:
889:             log.add_conn("Shutting down socket %s", sock)
890:             sock.shutdown(socket.SHUT_RDWR)
891: 
892:         except OSError as error:
893:             # Can't call shutdown if connection wasn't established, ignore error
894:             if error.errno != errno.ENOTCONN:
895:                 log.add_conn("Failed to shut down socket %s: %s", (sock, error))
896: 
897:         log.add_conn("Closing socket %s", sock)
898:         sock.close()
```

## github-tag-3.3.10 — _process_peer_init_input
`pynicotine/slskproto.py:1581-1634`

```text
1581:         return init
1582: 
1583:     def _process_peer_init_input(self, conn):
1584:         """Reads peer init messages from the input buffer of a peer connection."""
1585: 
1586:         init = None
1587:         in_buffer = conn.in_buffer
1588:         buffer_len = len(in_buffer)
1589:         msg_content_offset = 5
1590:         idx = 0
1591: 
1592:         # Peer init messages are 5 bytes or greater in length
1593:         while buffer_len >= msg_content_offset and init is None:
1594:             msg_size, = UINT32_UNPACK(in_buffer, idx)
1595: 
1596:             if msg_size > self.MAX_INCOMING_MESSAGE_SIZE:
1597:                 log.add_conn("Received message larger than maximum size %s from peer %s. "
1598:                              "Closing connection.", (self.MAX_INCOMING_MESSAGE_SIZE, conn.addr))
1599:                 break
1600: 
1601:             msg_size_total = msg_size + 4
1602: 
1603:             if msg_size_total > buffer_len:
1604:                 # Buffer is being filled
1605:                 conn.has_post_init_activity = True
1606:                 break
1607: 
1608:             # Unpack peer init messages
1609:             msg_type = in_buffer[idx + 4]
1610: 
1611:             if msg_type in PEER_INIT_MESSAGE_CLASSES:
1612:                 init = self._process_peer_init_message(
1613:                     conn, msg_type, msg_size, in_buffer, idx + msg_content_offset, idx + msg_size_total)
1614:             else:
1615:                 msg_content = in_buffer[idx + msg_content_offset:idx + min(50, msg_size_total)]
1616:                 log.add_debug("Peer init message type %s size %s contents %s unknown",
1617:                               (msg_type, msg_size, msg_content))
1618: 
1619:             if init is None:
1620:                 break
1621: 
1622:             idx += msg_size_total
1623:             buffer_len -= msg_size_total
1624: 
1625:         if init is None:
1626:             self._close_connection(conn)
1627:             return None
1628: 
1629:         if idx:
1630:             del in_buffer[:idx]
1631: 
1632:         conn.init = init
1633: 
1634:         self._add_init_message(init)
```

## github-tag-3.3.10 — _process_conn_incoming_messages promotion
`pynicotine/slskproto.py:2519-2568`

```text
2519:                 self._process_ready_output_socket(sock, current_time)
2520: 
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
2551: 
2552:     def _process_outgoing_messages(self, msgs):
2553: 
2554:         for msg in msgs:
2555:             if not self._should_process_queue:
2556:                 return
2557: 
2558:             msg_type = msg.msg_type
2559:             process_func = None
2560: 
2561:             if msg_type == MessageType.INIT:
2562:                 process_func = self._process_peer_init_output
2563:                 sock = msg.sock
2564: 
2565:             elif msg_type == MessageType.INTERNAL:
2566:                 process_func = self._process_internal_messages
2567:                 sock = None
2568: 
```

## github-tag-3.3.10 — _process_file_init_message
`pynicotine/slskproto.py:1864-1889`

```text
1864:         self._download_limit_split = int(limit)
1865: 
1866:     def _process_file_init_message(self, conn, in_buffer):
1867: 
1868:         msg_size = idx = 4
1869:         msg = self._unpack_network_message(
1870:             FileTransferInit,
1871:             memoryview(in_buffer)[:msg_size],
1872:             msg_size,
1873:             conn_type="file",
1874:             sock=conn.sock,
1875:             username=conn.init.target_user
1876:         )
1877: 
1878:         if msg is not None and msg.token is not None:
1879:             self._file_init_msgs[conn] = msg
1880:             self._emit_network_message_event(msg)
1881: 
1882:         return idx
1883: 
1884:     def _process_file_offset_message(self, conn, in_buffer):
1885: 
1886:         file_upload = self._file_upload_msgs[conn]
1887: 
1888:         if file_upload.offset is not None:
1889:             # No more incoming messages on this connection after receiving the
```

## github-tag-3.3.10 — PeerInit class
`pynicotine/slskmessages.py:2985-3024`

```text
2985: 
2986: 
2987: class PeerInitMessage(SlskMessage):
2988:     __slots__ = ()
2989:     msg_type = MessageType.INIT
2990: 
2991: 
2992: class PierceFireWall(PeerInitMessage):
2993:     """Peer init code 0.
2994: 
2995:     This message is sent in response to an indirect connection request
2996:     from another user. If the message goes through to the user, the
2997:     connection is ready. The token is taken from the ConnectToPeer
2998:     server message.
2999:     """
3000: 
3001:     __slots__ = ("sock", "token")
3002: 
3003:     def __init__(self, sock=None, token=None):
3004:         self.sock = sock
3005:         self.token = token
3006: 
3007:     def make_network_message(self):
3008:         return self.pack_uint32(self.token)
3009: 
3010:     def parse_network_message(self, message):
3011:         _pos, self.token = self.unpack_uint32(message)
3012: 
3013: 
3014: class PeerInit(PeerInitMessage):
3015:     """Peer init code 1.
3016: 
3017:     This message is sent to initiate a direct connection to another
3018:     peer. The token is apparently always 0 and ignored.
3019:     """
3020: 
3021:     __slots__ = ("sock", "init_user", "target_user", "conn_type", "outgoing_msgs", "token")
3022: 
3023:     def __init__(self, sock=None, init_user=None, target_user=None, conn_type=None):
3024:         self.sock = sock
```

## github-tag-3.3.10 — PierceFireWall class
`pynicotine/slskmessages.py:2990-3023`

```text
2990: 
2991: 
2992: class PierceFireWall(PeerInitMessage):
2993:     """Peer init code 0.
2994: 
2995:     This message is sent in response to an indirect connection request
2996:     from another user. If the message goes through to the user, the
2997:     connection is ready. The token is taken from the ConnectToPeer
2998:     server message.
2999:     """
3000: 
3001:     __slots__ = ("sock", "token")
3002: 
3003:     def __init__(self, sock=None, token=None):
3004:         self.sock = sock
3005:         self.token = token
3006: 
3007:     def make_network_message(self):
3008:         return self.pack_uint32(self.token)
3009: 
3010:     def parse_network_message(self, message):
3011:         _pos, self.token = self.unpack_uint32(message)
3012: 
3013: 
3014: class PeerInit(PeerInitMessage):
3015:     """Peer init code 1.
3016: 
3017:     This message is sent to initiate a direct connection to another
3018:     peer. The token is apparently always 0 and ignored.
3019:     """
3020: 
3021:     __slots__ = ("sock", "init_user", "target_user", "conn_type", "outgoing_msgs", "token")
3022: 
3023:     def __init__(self, sock=None, init_user=None, target_user=None, conn_type=None):
```

## github-branch-3.3.x — _replace_existing_connection
`pynicotine/slskproto.py:915-950`

```text
915:         self._process_conn_messages(init)
916: 
917:     def _replace_existing_connection(self, init):
918: 
919:         username = init.target_user
920:         conn_type = init.conn_type
921: 
922:         if username == self._server_username:
923:             return
924: 
925:         prev_init = self._username_init_msgs.pop(username + conn_type, None)
926: 
927:         if prev_init is None or prev_init.sock is None:
928:             return
929: 
930:         log.add_conn("Discarding existing connection of type %s to user %s", (init.conn_type, username))
931: 
932:         init.outgoing_msgs = prev_init.outgoing_msgs
933:         prev_init.outgoing_msgs = []
934: 
935:         self._close_connection(self._conns[prev_init.sock])
936: 
937:     @staticmethod
938:     def _close_socket(sock):
939: 
940:         try:
941:             log.add_conn("Shutting down socket %s", sock)
942:             sock.shutdown(socket.SHUT_RDWR)
943: 
944:         except OSError as error:
945:             # Can't call shutdown if connection wasn't established, ignore error
946:             if error.errno != errno.ENOTCONN:
947:                 log.add_conn("Failed to shut down socket %s: %s", (sock, error))
948: 
949:         try:
950:             log.add_conn("Closing socket %s", sock)
```

## github-branch-3.3.x — _process_peer_init_input
`pynicotine/slskproto.py:1664-1717`

```text
1664:         return init
1665: 
1666:     def _process_peer_init_input(self, conn):
1667:         """Reads peer init messages from the input buffer of a peer connection."""
1668: 
1669:         init = None
1670:         in_buffer = conn.in_buffer
1671:         buffer_len = len(in_buffer)
1672:         msg_content_offset = 5
1673:         idx = 0
1674: 
1675:         # Peer init messages are 5 bytes or greater in length
1676:         while buffer_len >= msg_content_offset and init is None:
1677:             msg_size, = UINT32_UNPACK(in_buffer, idx)
1678: 
1679:             if msg_size > self.MAX_INCOMING_MESSAGE_SIZE_SMALL:
1680:                 log.add_conn("Received message larger than maximum size %s from peer %s. "
1681:                              "Closing connection.", (self.MAX_INCOMING_MESSAGE_SIZE_SMALL, conn.addr))
1682:                 break
1683: 
1684:             msg_size_total = msg_size + 4
1685: 
1686:             if msg_size_total > buffer_len:
1687:                 # Buffer is being filled
1688:                 conn.has_post_init_activity = True
1689:                 break
1690: 
1691:             # Unpack peer init messages
1692:             msg_type = in_buffer[idx + 4]
1693: 
1694:             if msg_type in PEER_INIT_MESSAGE_CLASSES:
1695:                 init = self._process_peer_init_message(
1696:                     conn, msg_type, msg_size, in_buffer, idx + msg_content_offset, idx + msg_size_total)
1697:             else:
1698:                 msg_content = in_buffer[idx + msg_content_offset:idx + min(50, msg_size_total)]
1699:                 log.add_debug("Peer init message type %s size %s contents %s unknown",
1700:                               (msg_type, msg_size, msg_content))
1701: 
1702:             if init is None:
1703:                 break
1704: 
1705:             idx += msg_size_total
1706:             buffer_len -= msg_size_total
1707: 
1708:         if init is None:
1709:             self._close_connection(conn)
1710:             return None
1711: 
1712:         if idx:
1713:             del in_buffer[:idx]
1714: 
1715:         conn.init = init
1716: 
1717:         self._add_init_message(init)
```

## github-branch-3.3.x — _process_conn_incoming_messages promotion
`pynicotine/slskproto.py:2576-2625`

```text
2576:                 self._process_ready_output_socket(sock, current_time)
2577: 
2578:     def _process_conn_incoming_messages(self, conn):
2579: 
2580:         if not conn.in_buffer:
2581:             return
2582: 
2583:         if conn is self._server_conn:
2584:             self._process_server_input(conn)
2585:             return
2586: 
2587:         init = conn.init
2588: 
2589:         if init is None:
2590:             conn.init = init = self._process_peer_init_input(conn)
2591: 
2592:             if init is None or not conn.in_buffer:
2593:                 return
2594: 
2595:         if init.conn_type == ConnectionType.PEER:
2596:             self._process_peer_input(conn)
2597: 
2598:         elif init.conn_type == ConnectionType.FILE:
2599:             self._process_file_input(conn)
2600: 
2601:         elif init.conn_type == ConnectionType.DISTRIBUTED:
2602:             self._process_distrib_input(conn)
2603: 
2604:         if conn.sock is not None and init.sock is not conn.sock:
2605:             log.add_conn("Received message on secondary connection of type %s to user %s, "
2606:                          "promoting to primary connection", (init.conn_type, init.target_user))
2607:             init.sock = conn.sock
2608: 
2609:     def _process_outgoing_messages(self, msgs):
2610: 
2611:         for msg in msgs:
2612:             if not self._should_process_queue:
2613:                 return
2614: 
2615:             msg_type = msg.msg_type
2616:             process_func = None
2617: 
2618:             if msg_type == MessageType.INIT:
2619:                 process_func = self._process_peer_init_output
2620:                 sock = msg.sock
2621: 
2622:             elif msg_type == MessageType.INTERNAL:
2623:                 process_func = self._process_internal_messages
2624:                 sock = None
2625: 
```

## github-branch-3.3.x — _process_file_init_message
`pynicotine/slskproto.py:1949-1974`

```text
1949:         self._download_limit_split = int(limit)
1950: 
1951:     def _process_file_init_message(self, conn, in_buffer):
1952: 
1953:         msg_size = idx = 4
1954:         msg = self._unpack_network_message(
1955:             FileTransferInit,
1956:             memoryview(in_buffer)[:msg_size],
1957:             msg_size,
1958:             conn_type="file",
1959:             sock=conn.sock,
1960:             username=conn.init.target_user
1961:         )
1962: 
1963:         if msg is not None and msg.token is not None:
1964:             self._file_init_msgs[conn] = msg
1965:             self._emit_network_message_event(msg)
1966: 
1967:         return idx
1968: 
1969:     def _process_file_offset_message(self, conn, in_buffer):
1970: 
1971:         file_upload = self._file_upload_msgs[conn]
1972: 
1973:         if file_upload.offset is not None:
1974:             # No more incoming messages on this connection after receiving the
```

## github-branch-3.3.x — PeerInit class
`pynicotine/slskmessages.py:3008-3047`

```text
3008: 
3009: 
3010: class PeerInitMessage(SlskMessage):
3011:     __slots__ = ()
3012:     msg_type = MessageType.INIT
3013: 
3014: 
3015: class PierceFireWall(PeerInitMessage):
3016:     """Peer init code 0.
3017: 
3018:     This message is sent in response to an indirect connection request
3019:     from another user. If the message goes through to the user, the
3020:     connection is ready. The token is taken from the ConnectToPeer
3021:     server message.
3022:     """
3023: 
3024:     __slots__ = ("sock", "token")
3025: 
3026:     def __init__(self, sock=None, token=None):
3027:         self.sock = sock
3028:         self.token = token
3029: 
3030:     def make_network_message(self):
3031:         return self.pack_uint32(self.token)
3032: 
3033:     def parse_network_message(self, message):
3034:         _pos, self.token = self.unpack_uint32(message)
3035: 
3036: 
3037: class PeerInit(PeerInitMessage):
3038:     """Peer init code 1.
3039: 
3040:     This message is sent to initiate a direct connection to another
3041:     peer. The token is apparently always 0 and ignored.
3042:     """
3043: 
3044:     __slots__ = ("sock", "init_user", "target_user", "conn_type", "outgoing_msgs", "token")
3045: 
3046:     def __init__(self, sock=None, init_user=None, target_user=None, conn_type=None):
3047:         self.sock = sock
```

## github-branch-3.3.x — PierceFireWall class
`pynicotine/slskmessages.py:3013-3046`

```text
3013: 
3014: 
3015: class PierceFireWall(PeerInitMessage):
3016:     """Peer init code 0.
3017: 
3018:     This message is sent in response to an indirect connection request
3019:     from another user. If the message goes through to the user, the
3020:     connection is ready. The token is taken from the ConnectToPeer
3021:     server message.
3022:     """
3023: 
3024:     __slots__ = ("sock", "token")
3025: 
3026:     def __init__(self, sock=None, token=None):
3027:         self.sock = sock
3028:         self.token = token
3029: 
3030:     def make_network_message(self):
3031:         return self.pack_uint32(self.token)
3032: 
3033:     def parse_network_message(self, message):
3034:         _pos, self.token = self.unpack_uint32(message)
3035: 
3036: 
3037: class PeerInit(PeerInitMessage):
3038:     """Peer init code 1.
3039: 
3040:     This message is sent to initiate a direct connection to another
3041:     peer. The token is apparently always 0 and ignored.
3042:     """
3043: 
3044:     __slots__ = ("sock", "init_user", "target_user", "conn_type", "outgoing_msgs", "token")
3045: 
3046:     def __init__(self, sock=None, init_user=None, target_user=None, conn_type=None):
```

## github-branch-master — _replace_existing_connection
`pynicotine/slskproto.py:933-968`

```text
933:         self._process_conn_messages(init)
934: 
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
954: 
955:     @staticmethod
956:     def _close_socket(sock):
957: 
958:         try:
959:             log.add_conn("Shutting down socket %s", sock)
960:             sock.shutdown(socket.SHUT_RDWR)
961: 
962:         except OSError as error:
963:             # Can't call shutdown if connection wasn't established, ignore error
964:             if error.errno != errno.ENOTCONN:
965:                 log.add_conn("Failed to shut down socket %s: %s", (sock, error))
966: 
967:         try:
968:             log.add_conn("Closing socket %s", sock)
```

## github-branch-master — _process_peer_init_input
`pynicotine/slskproto.py:1706-1759`

```text
1706:         return init
1707: 
1708:     def _process_peer_init_input(self, conn):
1709:         """Reads peer init messages from the input buffer of a peer connection."""
1710: 
1711:         init = None
1712:         in_buffer = conn.in_buffer
1713:         buffer_len = len(in_buffer)
1714:         msg_content_offset = 5
1715:         idx = 0
1716: 
1717:         # Peer init messages are 5 bytes or greater in length
1718:         while buffer_len >= msg_content_offset and init is None:
1719:             msg_size, = UINT32_UNPACK(in_buffer, idx)
1720: 
1721:             if msg_size > self.MAX_INCOMING_MESSAGE_SIZE_SMALL:
1722:                 log.add_conn("Received message larger than maximum size %s from peer %s. "
1723:                              "Closing connection.", (self.MAX_INCOMING_MESSAGE_SIZE_SMALL, conn.addr))
1724:                 break
1725: 
1726:             msg_size_total = msg_size + 4
1727: 
1728:             if msg_size_total > buffer_len:
1729:                 # Buffer is being filled
1730:                 conn.has_post_init_activity = True
1731:                 break
1732: 
1733:             # Unpack peer init messages
1734:             msg_type = in_buffer[idx + 4]
1735: 
1736:             if msg_type in PEER_INIT_MESSAGE_CLASSES:
1737:                 init = self._process_peer_init_message(
1738:                     conn, msg_type, msg_size, memoryview(in_buffer)[idx + msg_content_offset:idx + msg_size_total])
1739:             else:
1740:                 msg_content = in_buffer[idx + msg_content_offset:idx + min(50, msg_size_total)]
1741:                 log.add_debug("Peer init message type %s size %s contents %s unknown",
1742:                               (msg_type, msg_size, msg_content))
1743: 
1744:             if init is None:
1745:                 break
1746: 
1747:             idx += msg_size_total
1748:             buffer_len -= msg_size_total
1749: 
1750:         if init is None:
1751:             self._close_connection(conn)
1752:             return None
1753: 
1754:         if idx:
1755:             del in_buffer[:idx]
1756: 
1757:         conn.init = init
1758: 
1759:         self._add_init_message(init)
```

## github-branch-master — _process_conn_incoming_messages promotion
`pynicotine/slskproto.py:2700-2749`

```text
2700:                 self._process_ready_output_socket(sock, current_time)
2701: 
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
2732: 
2733:     def _process_outgoing_messages(self, msgs):
2734: 
2735:         for msg in msgs:
2736:             if not self._should_process_queue:
2737:                 return
2738: 
2739:             msg_type = msg.msg_type
2740:             process_func = None
2741: 
2742:             if msg_type == MessageType.INIT:
2743:                 process_func = self._process_peer_init_output
2744:                 sock = msg.sock
2745: 
2746:             elif msg_type == MessageType.INTERNAL:
2747:                 process_func = self._process_internal_messages
2748:                 sock = None
2749: 
```

## github-branch-master — _process_file_init_message
`pynicotine/slskproto.py:1991-2016`

```text
1991:         self._download_limit_split = int(limit)
1992: 
1993:     def _process_file_init_message(self, conn, in_buffer):
1994: 
1995:         msg_size = idx = 4
1996:         msg = self._unpack_network_message(
1997:             FileTransferInit,
1998:             memoryview(in_buffer)[:msg_size],
1999:             msg_size,
2000:             conn_type="file",
2001:             sock=conn.sock,
2002:             username=conn.init.target_user
2003:         )
2004: 
2005:         if msg is not None and msg.token is not None:
2006:             self._file_init_msgs[conn] = msg
2007:             self._emit_network_message_event(msg)
2008: 
2009:         return idx
2010: 
2011:     def _process_file_offset_message(self, conn, in_buffer):
2012: 
2013:         file_upload = self._file_upload_msgs[conn]
2014: 
2015:         if file_upload.offset is not None:
2016:             # No more incoming messages on this connection after receiving the
```

## github-branch-master — PeerInit class
`pynicotine/slskmessages.py:3128-3167`

```text
3128: 
3129: 
3130: class PeerInitMessage(SlskMessage):
3131:     __slots__ = ()
3132:     msg_type = MessageType.INIT
3133: 
3134: 
3135: class PierceFireWall(PeerInitMessage):
3136:     """Peer init code 0.
3137: 
3138:     This message is sent in response to an indirect connection request
3139:     from another user. If the message goes through to the user, the
3140:     connection is ready. The token is taken from the ConnectToPeer
3141:     server message.
3142:     """
3143: 
3144:     __slots__ = ("sock", "token")
3145: 
3146:     def __init__(self, sock=None, token=None, *, msg_content=None):
3147:         PeerInitMessage.__init__(self, msg_content)
3148:         self.sock = sock
3149:         self.token = token
3150: 
3151:     def make_network_message(self):
3152:         return self.pack_uint32(self.token)
3153: 
3154:     def parse_network_message(self):
3155:         self.token = self.unpack_uint32()
3156: 
3157: 
3158: class PeerInit(PeerInitMessage):
3159:     """Peer init code 1.
3160: 
3161:     This message is sent to initiate a direct connection to another peer. The
3162:     token is always zero and ignored today, but used to be non-zero and
3163:     included in a concurrent SendConnectToken server message for connection
3164:     verification.
3165:     """
3166: 
3167:     __slots__ = ("sock", "init_user", "target_user", "conn_type", "indirect_token", "created_time", "outgoing_msgs")
```

## github-branch-master — PierceFireWall class
`pynicotine/slskmessages.py:3133-3166`

```text
3133: 
3134: 
3135: class PierceFireWall(PeerInitMessage):
3136:     """Peer init code 0.
3137: 
3138:     This message is sent in response to an indirect connection request
3139:     from another user. If the message goes through to the user, the
3140:     connection is ready. The token is taken from the ConnectToPeer
3141:     server message.
3142:     """
3143: 
3144:     __slots__ = ("sock", "token")
3145: 
3146:     def __init__(self, sock=None, token=None, *, msg_content=None):
3147:         PeerInitMessage.__init__(self, msg_content)
3148:         self.sock = sock
3149:         self.token = token
3150: 
3151:     def make_network_message(self):
3152:         return self.pack_uint32(self.token)
3153: 
3154:     def parse_network_message(self):
3155:         self.token = self.unpack_uint32()
3156: 
3157: 
3158: class PeerInit(PeerInitMessage):
3159:     """Peer init code 1.
3160: 
3161:     This message is sent to initiate a direct connection to another peer. The
3162:     token is always zero and ignored today, but used to be non-zero and
3163:     included in a concurrent SendConnectToken server message for connection
3164:     verification.
3165:     """
3166: 
```
