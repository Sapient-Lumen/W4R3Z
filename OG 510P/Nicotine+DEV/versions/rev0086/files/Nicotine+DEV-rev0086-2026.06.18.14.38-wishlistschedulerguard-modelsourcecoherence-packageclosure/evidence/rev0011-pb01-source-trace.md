# rev0011 PB-01 source trace — peer primary-election and promotion points

This trace is compact and references external source trees from the rev0003 source bundle; it does not embed source directories. Line numbers are from the local archived source lanes.

## github-tag-3.3.10

### replace_existing_connection: `pynicotine/slskproto.py:865-909`

```python
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
  899: 
  900:     def _close_connection(self, conn):
  901: 
  902:         if conn is None:
  903:             return
  904: 
  905:         sock = conn.sock
  906:         del self._conns[sock]
  907: 
  908:         if conn is self._server_conn:
  909:             # Disconnecting from server, clean up connections and queue
```

### process_peer_init_message: `pynicotine/slskproto.py:1518-1622`

```python
 1518:     def _process_peer_init_message(self, conn, msg_type, msg_size, in_buffer, start_offset, end_offset):
 1519: 
 1520:         msg_class = PEER_INIT_MESSAGE_CLASSES[msg_type]
 1521:         msg = self._unpack_network_message(
 1522:             msg_class,
 1523:             memoryview(in_buffer)[start_offset:end_offset],
 1524:             msg_size,
 1525:             conn_type="peer init",
 1526:             sock=conn.sock
 1527:         )
 1528: 
 1529:         if msg is None:
 1530:             return None
 1531: 
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
 1556:             else:
 1557:                 # We already have a direct connection, but some clients may send a message over
 1558:                 # the indirect connection. Keep it open.
 1559:                 log.add_conn("Direct connection was already established, keeping it as primary connection")
 1560: 
 1561:             if is_direct_conn_in_progress:
 1562:                 log.add_conn("Stopping direct connection attempt to user %s", init.target_user)
 1563:                 self._close_connection(self._conns[previous_sock])
 1564: 
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
```

### process_peer_init_input_tail: `pynicotine/slskproto.py:1583-1652`

```python
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
 1635:         self._process_conn_messages(init)
 1636:         self._accept_child_peer_connection(conn)
 1637:         return init
 1638: 
 1639:     def _process_peer_init_output(self, msg):
 1640: 
 1641:         # Pack peer init messages
 1642:         conn = self._conns[msg.sock]
 1643:         msg_content = self._pack_network_message(msg)
 1644: 
 1645:         if msg_content is None:
 1646:             return
 1647: 
 1648:         out_buffer = conn.out_buffer
 1649: 
 1650:         out_buffer += msg.pack_uint32(len(msg_content) + 1)
 1651:         out_buffer += msg.pack_uint8(PEER_INIT_MESSAGE_CODES[msg.__class__])
 1652:         out_buffer += msg_content
```

### process_conn_incoming_messages: `pynicotine/slskproto.py:2521-2565`

```python
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
```

## github-branch-3.3.x

### replace_existing_connection: `pynicotine/slskproto.py:917-961`

```python
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
  951:             sock.close()
  952: 
  953:         except OSError as error:
  954:             log.add_conn("Failed to close socket %s: %s", (sock, error))
  955: 
  956:     def _close_connection(self, conn):
  957: 
  958:         if conn is None:
  959:             return
  960: 
  961:         sock = conn.sock
```

### process_peer_init_message: `pynicotine/slskproto.py:1597-1701`

```python
 1597:     def _process_peer_init_message(self, conn, msg_type, msg_size, in_buffer, start_offset, end_offset):
 1598: 
 1599:         msg_class = PEER_INIT_MESSAGE_CLASSES[msg_type]
 1600:         msg = self._unpack_network_message(
 1601:             msg_class,
 1602:             memoryview(in_buffer)[start_offset:end_offset],
 1603:             msg_size,
 1604:             conn_type="peer init",
 1605:             sock=conn.sock
 1606:         )
 1607: 
 1608:         if msg is None:
 1609:             return None
 1610: 
 1611:         if msg_class is PierceFireWall:
 1612:             token = msg.token
 1613:             log.add_conn("Received indirect connection response (PierceFireWall) with token "
 1614:                          "%s, address %s", (token, conn.addr))
 1615: 
 1616:             log.add_conn("Number of stored peer init message tokens: %s", len(self._token_init_msgs))
 1617: 
 1618:             if token not in self._token_init_msgs:
 1619:                 log.add_conn("Indirect connection attempt with token %s previously expired, "
 1620:                              "closing connection", token)
 1621:                 return None
 1622: 
 1623:             init, _request_time = self._token_init_msgs.pop(token)
 1624:             previous_sock = init.sock
 1625:             is_direct_conn_in_progress = (
 1626:                 previous_sock is not None and not self._conns[previous_sock].is_established
 1627:             )
 1628: 
 1629:             log.add_conn("Indirect connection to user %s with token %s established",
 1630:                          (init.target_user, token))
 1631: 
 1632:             self._set_tcp_buffer_size(conn.sock, init.conn_type)
 1633: 
 1634:             if previous_sock is None or is_direct_conn_in_progress:
 1635:                 init.sock = conn.sock
 1636:                 log.add_conn("Using as primary connection, since no direct connection is established")
 1637:             else:
 1638:                 # We already have a direct connection, but some clients may send a message over
 1639:                 # the indirect connection. Keep it open.
 1640:                 log.add_conn("Direct connection was already established, keeping it as primary connection")
 1641: 
 1642:             if is_direct_conn_in_progress:
 1643:                 log.add_conn("Stopping direct connection attempt to user %s", init.target_user)
 1644:                 self._close_connection(self._conns[previous_sock])
 1645: 
 1646:         elif msg_class is PeerInit:
 1647:             username = msg.target_user
 1648:             conn_type = msg.conn_type
 1649:             addr = conn.addr
 1650: 
 1651:             log.add_conn("Received incoming direct connection of type %s from user "
 1652:                          "%s, address %s", (conn_type, username, addr))
 1653: 
 1654:             if conn_type not in self.ALLOWED_PEER_CONN_TYPES:
 1655:                 log.add_conn("Unknown connection type %s", conn_type)
 1656:                 return None
 1657: 
 1658:             self._set_tcp_buffer_size(conn.sock, conn_type)
 1659: 
 1660:             init = msg
 1661:             self._replace_existing_connection(init)
 1662: 
 1663:         self._emit_network_message_event(msg)
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
```

### process_peer_init_input_tail: `pynicotine/slskproto.py:1666-1735`

```python
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
 1718:         self._process_conn_messages(init)
 1719:         self._accept_child_peer_connection(conn)
 1720:         return init
 1721: 
 1722:     def _process_peer_init_output(self, conn, msg):
 1723: 
 1724:         # Pack peer init messages
 1725:         msg_content = self._pack_network_message(msg)
 1726: 
 1727:         if msg_content is None:
 1728:             return
 1729: 
 1730:         out_buffer = conn.out_buffer
 1731: 
 1732:         out_buffer += msg.pack_uint32(len(msg_content) + 1)
 1733:         out_buffer += msg.pack_uint8(PEER_INIT_MESSAGE_CODES[msg.__class__])
 1734:         out_buffer += msg_content
 1735: 
```

### process_conn_incoming_messages: `pynicotine/slskproto.py:2578-2622`

```python
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
```

## github-branch-master

### replace_existing_connection: `pynicotine/slskproto.py:935-979`

```python
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
  969:             sock.close()
  970: 
  971:         except OSError as error:
  972:             log.add_conn("Failed to close socket %s: %s", (sock, error))
  973: 
  974:     def _close_connection(self, conn):
  975: 
  976:         if conn is None:
  977:             return
  978: 
  979:         sock = conn.sock
```

### process_peer_init_message: `pynicotine/slskproto.py:1639-1743`

```python
 1639:     def _process_peer_init_message(self, conn, msg_type, msg_size, msg_content):
 1640: 
 1641:         msg_class = PEER_INIT_MESSAGE_CLASSES[msg_type]
 1642:         msg = self._unpack_network_message(
 1643:             msg_class,
 1644:             msg_content,
 1645:             msg_size,
 1646:             conn_type="peer init",
 1647:             sock=conn.sock
 1648:         )
 1649: 
 1650:         if msg is None:
 1651:             return None
 1652: 
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
 1667:             is_direct_conn_in_progress = (
 1668:                 previous_sock is not None and not self._conns[previous_sock].is_established
 1669:             )
 1670: 
 1671:             log.add_conn("Indirect connection to user %s with token %s established",
 1672:                          (init.target_user, pierce_token))
 1673: 
 1674:             self._set_tcp_buffer_size(conn.sock, init.conn_type)
 1675: 
 1676:             if previous_sock is None or is_direct_conn_in_progress:
 1677:                 init.sock = conn.sock
 1678:                 log.add_conn("Using as primary connection, since no direct connection is established")
 1679:             else:
 1680:                 # We already have a direct connection, but some clients may send a message over
 1681:                 # the indirect connection. Keep it open.
 1682:                 log.add_conn("Direct connection was already established, keeping it as primary connection")
 1683: 
 1684:             if is_direct_conn_in_progress:
 1685:                 log.add_conn("Stopping direct connection attempt to user %s", init.target_user)
 1686:                 self._close_connection(self._conns[previous_sock])
 1687: 
 1688:         elif msg_class is PeerInit:
 1689:             username = msg.target_user
 1690:             conn_type = msg.conn_type
 1691:             addr = conn.addr
 1692: 
 1693:             log.add_conn("Received incoming direct connection of type %s from user "
 1694:                          "%s, address %s", (conn_type, username, addr))
 1695: 
 1696:             if conn_type not in self.ALLOWED_PEER_CONN_TYPES:
 1697:                 log.add_conn("Unknown connection type %s", conn_type)
 1698:                 return None
 1699: 
 1700:             self._set_tcp_buffer_size(conn.sock, conn_type)
 1701: 
 1702:             init = msg
 1703:             self._replace_existing_connection(init)
 1704: 
 1705:         self._emit_network_message_event(msg)
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
```

### process_peer_init_input_tail: `pynicotine/slskproto.py:1708-1777`

```python
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
 1760:         self._process_conn_messages(init)
 1761:         self._accept_child_peer_connection(conn)
 1762:         return init
 1763: 
 1764:     def _process_peer_init_output(self, conn, msg):
 1765: 
 1766:         # Pack peer init messages
 1767:         msg_content = self._pack_network_message(msg)
 1768: 
 1769:         if msg_content is None:
 1770:             return
 1771: 
 1772:         out_buffer = conn.out_buffer
 1773: 
 1774:         out_buffer += msg.pack_uint32(len(msg_content) + 1)
 1775:         out_buffer += msg.pack_uint8(PEER_INIT_MESSAGE_CODES[msg.__class__])
 1776:         out_buffer += msg_content
 1777: 
```

### process_conn_incoming_messages: `pynicotine/slskproto.py:2702-2746`

```python
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
```
