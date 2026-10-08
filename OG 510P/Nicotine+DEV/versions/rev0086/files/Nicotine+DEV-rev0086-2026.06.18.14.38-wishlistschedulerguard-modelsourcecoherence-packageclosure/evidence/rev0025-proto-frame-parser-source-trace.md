# rev0025 PROTO-FRAME-PARSER-01 source trace

Scope: U-137 length-prefixed field truncation and U-175 malformed framed-message length handling. Source lanes are the archived rev0003 source trees; no full source is embedded in this cube.


## github-tag-3.3.10

### U-137 helpers: `unpack_bytes()` / `unpack_string()`

```text
  294:     def unpack_bytes(message, start=0):
  295: 
  296:         length, = UINT32_UNPACK(message, start)
  297:         start += 4
  298:         end = start + length
  299:         content = message[start:end]
  300: 
  301:         return end, content.tobytes()
  302: 
  303:     @staticmethod
  304:     def unpack_string(message, start=0):
  305: 
  306:         length, = UINT32_UNPACK(message, start)
  307:         start += 4
  308:         end = start + length
  309:         content = message[start:end].tobytes()
  310: 
  311:         try:
  312:             string = content.decode("utf-8")
  313: 
  314:         except UnicodeDecodeError:
  315:             # Legacy strings
  316:             string = content.decode("latin-1")
  317: 
```

The 3.3.x/3.3.10 static helpers compute `end = start + length`, slice `message[start:end]`, and return that `end`; Python slicing does not fail when `end` is beyond the buffer, so final fields can be accepted short.

### U-175 server frame loop

```text
 1382:         msg_content_offset = 8
 1383:         idx = 0
 1384: 
 1385:         # Server messages are 8 bytes or greater in length
 1386:         while buffer_len >= msg_content_offset:
 1387:             msg_size, msg_type = DOUBLE_UINT32_UNPACK(in_buffer, idx)
 1388: 
 1389:             if msg_size > self.MAX_INCOMING_MESSAGE_SIZE:
 1390:                 log.add_conn("Received message larger than maximum size %s from server. "
 1391:                              "Closing connection.", self.MAX_INCOMING_MESSAGE_SIZE)
 1392:                 self._manual_server_disconnect = True
 1393:                 self._close_connection(conn)
 1394:                 return
 1395: 
 1396:             msg_size_total = msg_size + 4
 1397: 
 1398:             if msg_size_total > buffer_len:
 1399:                 # Buffer is being filled
 1400:                 break
 1401: 
 1402:             # Unpack server messages
 1403:             if msg_type in SERVER_MESSAGE_CLASSES:
 1404:                 if not self._process_server_message(
 1405:                     msg_type, msg_size, in_buffer, idx + msg_content_offset, idx + msg_size_total
 1406:                 ):
 1407:                     self._manual_server_disconnect = True
 1408:                     self._close_connection(conn)
 1409:                     return
 1410:             else:
 1411:                 msg_content = in_buffer[idx + msg_content_offset:idx + min(50, msg_size_total)]
 1412:                 log.add_debug("Server message type %s size %s contents %s unknown",
 1413:                               (msg_type, msg_size, msg_content))
 1414: 
 1415:             idx += msg_size_total
 1416:             buffer_len -= msg_size_total
 1417: 
 1418:         if idx:
 1419:             del in_buffer[:idx]
```

### U-175 peer frame loop

```text
 1744:         msg_content_offset = 8
 1745:         idx = 0
 1746:         search_result_received = False
 1747: 
 1748:         # Peer messages are 8 bytes or greater in length
 1749:         while buffer_len >= msg_content_offset:
 1750:             msg_size, msg_type = DOUBLE_UINT32_UNPACK(in_buffer, idx)
 1751: 
 1752:             if msg_size > self.MAX_INCOMING_MESSAGE_SIZE:
 1753:                 log.add_conn("Received message larger than maximum size %s from user %s. "
 1754:                              "Closing connection.", (self.MAX_INCOMING_MESSAGE_SIZE, conn.init.target_user))
 1755:                 self._close_connection(conn)
 1756:                 return
 1757: 
 1758:             msg_size_total = msg_size + 4
 1759:             msg_class = None
 1760: 
 1761:             if msg_type in PEER_MESSAGE_CLASSES:
 1762:                 msg_class = PEER_MESSAGE_CLASSES[msg_type]
 1763: 
 1764:             # Send progress to the main thread
 1765:             if msg_class is SharedFileListResponse:
 1766:                 events.emit_main_thread(
 1767:                     "shared-file-list-progress", conn.init.target_user, conn.sock, buffer_len, msg_size_total)
 1768: 
 1769:             elif msg_class is UserInfoResponse:
 1770:                 events.emit_main_thread(
 1771:                     "user-info-progress", conn.init.target_user, conn.sock, buffer_len, msg_size_total)
 1772: 
 1773:             if msg_size_total > buffer_len:
 1774:                 # Buffer is being filled
 1775:                 break
 1776: 
 1777:             # Unpack peer messages
 1778:             if msg_class:
 1779:                 msg = self._unpack_network_message(
 1780:                     msg_class,
 1781:                     memoryview(in_buffer)[idx + msg_content_offset:idx + msg_size_total],
 1782:                     msg_size,
 1783:                     conn_type="peer",
 1784:                     sock=conn.sock,
 1785:                     addr=conn.addr,
 1786:                     username=conn.init.target_user
 1787:                 )
 1788: 
 1789:                 if msg_class is FileSearchResponse:
 1790:                     search_result_received = True
 1791: 
 1792:                 self._emit_network_message_event(msg)
 1793:             else:
 1794:                 msg_content = in_buffer[idx + msg_content_offset:idx + min(50, msg_size_total)]
 1795:                 log.add_debug("Peer message type %s size %s contents %s unknown, from user: %s, address %s",
 1796:                               (msg_type, msg_size, msg_content, conn.init.target_user, conn.addr))
 1797: 
 1798:             idx += msg_size_total
 1799:             buffer_len -= msg_size_total
 1800: 
 1801:         if idx:
 1802:             del in_buffer[:idx]
```

### U-175 distributed frame loop

```text
 2313:         msg_content_offset = 5
 2314:         idx = 0
 2315: 
 2316:         # Distributed messages are 5 bytes or greater in length
 2317:         while buffer_len >= msg_content_offset:
 2318:             msg_size, = UINT32_UNPACK(in_buffer, idx)
 2319: 
 2320:             if msg_size > self.MAX_INCOMING_MESSAGE_SIZE:
 2321:                 log.add_conn("Received message larger than maximum size %s from user %s. "
 2322:                              "Closing connection.", (self.MAX_INCOMING_MESSAGE_SIZE, conn.init.target_user))
 2323:                 self._close_connection(conn)
 2324:                 break
 2325: 
 2326:             msg_size_total = msg_size + 4
 2327: 
 2328:             if msg_size_total > buffer_len:
 2329:                 # Buffer is being filled
 2330:                 conn.has_post_init_activity = True
 2331:                 break
 2332: 
 2333:             # Unpack distributed messages
 2334:             msg_type = in_buffer[idx + 4]
 2335: 
 2336:             if msg_type in DISTRIBUTED_MESSAGE_CLASSES:
 2337:                 if not self._process_distrib_message(
 2338:                     conn, msg_type, msg_size, in_buffer, idx + msg_content_offset, idx + msg_size_total
 2339:                 ):
 2340:                     self._close_connection(conn)
 2341:                     return
 2342:             else:
 2343:                 msg_content = in_buffer[idx + msg_content_offset:idx + min(50, msg_size_total)]
 2344:                 log.add_debug("Distrib message type %s size %s contents %s unknown",
 2345:                               (msg_type, msg_size, msg_content))
 2346: 
 2347:             idx += msg_size_total
 2348:             buffer_len -= msg_size_total
 2349: 
```

The frame loops compute `msg_size_total = msg_size + 4` and advance by that amount. The probe demonstrates that server/peer `msg_size` values 0..3 and distributed `msg_size` 0 are not rejected as shorter than the mandatory message-code field before buffer advancement.


## github-branch-3.3.x

### U-137 helpers: `unpack_bytes()` / `unpack_string()`

```text
  294:     def unpack_bytes(message, start=0):
  295: 
  296:         length, = UINT32_UNPACK(message, start)
  297:         start += 4
  298:         end = start + length
  299:         content = message[start:end]
  300: 
  301:         return end, content.tobytes()
  302: 
  303:     @staticmethod
  304:     def unpack_string(message, start=0):
  305: 
  306:         length, = UINT32_UNPACK(message, start)
  307:         start += 4
  308:         end = start + length
  309:         content = message[start:end].tobytes()
  310: 
  311:         try:
  312:             string = content.decode("utf-8")
  313: 
  314:         except UnicodeDecodeError:
  315:             # Legacy strings
  316:             string = content.decode("latin-1")
  317: 
```

The 3.3.x/3.3.10 static helpers compute `end = start + length`, slice `message[start:end]`, and return that `end`; Python slicing does not fail when `end` is beyond the buffer, so final fields can be accepted short.

### U-175 server frame loop

```text
 1462:         msg_content_offset = 8
 1463:         idx = 0
 1464: 
 1465:         # Server messages are 8 bytes or greater in length
 1466:         while buffer_len >= msg_content_offset:
 1467:             msg_size, msg_type = DOUBLE_UINT32_UNPACK(in_buffer, idx)
 1468: 
 1469:             if msg_size > self.MAX_INCOMING_MESSAGE_SIZE_LARGE:
 1470:                 log.add_conn("Received message larger than maximum size %s from server. "
 1471:                              "Closing connection.", self.MAX_INCOMING_MESSAGE_SIZE_LARGE)
 1472:                 self._manual_server_disconnect = True
 1473:                 self._close_connection(conn)
 1474:                 return
 1475: 
 1476:             msg_size_total = msg_size + 4
 1477: 
 1478:             if msg_size_total > buffer_len:
 1479:                 # Buffer is being filled
 1480:                 break
 1481: 
 1482:             # Unpack server messages
 1483:             if msg_type in SERVER_MESSAGE_CLASSES:
 1484:                 if not self._process_server_message(
 1485:                     msg_type, msg_size, in_buffer, idx + msg_content_offset, idx + msg_size_total
 1486:                 ):
 1487:                     self._manual_server_disconnect = True
 1488:                     self._close_connection(conn)
 1489:                     return
 1490:             else:
 1491:                 msg_content = in_buffer[idx + msg_content_offset:idx + min(50, msg_size_total)]
 1492:                 log.add_debug("Server message type %s size %s contents %s unknown",
 1493:                               (msg_type, msg_size, msg_content))
 1494: 
 1495:             idx += msg_size_total
 1496:             buffer_len -= msg_size_total
 1497: 
 1498:         if idx:
 1499:             del in_buffer[:idx]
```

### U-175 peer frame loop

```text
 1827:         msg_content_offset = 8
 1828:         idx = 0
 1829:         search_result_received = False
 1830: 
 1831:         # Peer messages are 8 bytes or greater in length
 1832:         while buffer_len >= msg_content_offset:
 1833:             msg_size, msg_type = DOUBLE_UINT32_UNPACK(in_buffer, idx)
 1834:             msg_size_total = msg_size + 4
 1835:             max_msg_size = self.MAX_INCOMING_MESSAGE_SIZE_MEDIUM
 1836:             msg_class = None
 1837: 
 1838:             if msg_type in PEER_MESSAGE_CLASSES:
 1839:                 msg_class = PEER_MESSAGE_CLASSES[msg_type]
 1840: 
 1841:             if msg_class is SharedFileListResponse or msg_class is UserInfoResponse:
 1842:                 max_msg_size = self.MAX_INCOMING_MESSAGE_SIZE_LARGE
 1843: 
 1844:             if msg_size > max_msg_size:
 1845:                 log.add_conn("Received message larger than maximum size %s from user %s. "
 1846:                              "Closing connection.", (max_msg_size, conn.init.target_user))
 1847:                 self._close_connection(conn)
 1848:                 return
 1849: 
 1850:             # Send progress to the main thread
 1851:             if msg_class is SharedFileListResponse:
 1852:                 events.emit_main_thread(
 1853:                     "shared-file-list-progress", conn.init.target_user, conn.sock, buffer_len, msg_size_total)
 1854: 
 1855:             elif msg_class is UserInfoResponse:
 1856:                 events.emit_main_thread(
 1857:                     "user-info-progress", conn.init.target_user, conn.sock, buffer_len, msg_size_total)
 1858: 
 1859:             if msg_size_total > buffer_len:
 1860:                 # Buffer is being filled
 1861:                 break
 1862: 
 1863:             # Unpack peer messages
 1864:             if msg_class:
 1865:                 msg = self._unpack_network_message(
 1866:                     msg_class,
 1867:                     memoryview(in_buffer)[idx + msg_content_offset:idx + msg_size_total],
 1868:                     msg_size,
 1869:                     conn_type="peer",
 1870:                     sock=conn.sock,
 1871:                     addr=conn.addr,
 1872:                     username=conn.init.target_user
 1873:                 )
 1874: 
 1875:                 if msg_class is FileSearchResponse:
 1876:                     search_result_received = True
 1877: 
 1878:                 self._emit_network_message_event(msg)
 1879:             else:
 1880:                 msg_content = in_buffer[idx + msg_content_offset:idx + min(50, msg_size_total)]
 1881:                 log.add_debug("Peer message type %s size %s contents %s unknown, from user: %s, address %s",
 1882:                               (msg_type, msg_size, msg_content, conn.init.target_user, conn.addr))
 1883: 
 1884:             idx += msg_size_total
 1885:             buffer_len -= msg_size_total
```

### U-175 distributed frame loop

```text
 2370:         msg_content_offset = 5
 2371:         idx = 0
 2372: 
 2373:         # Distributed messages are 5 bytes or greater in length
 2374:         while buffer_len >= msg_content_offset:
 2375:             msg_size, = UINT32_UNPACK(in_buffer, idx)
 2376: 
 2377:             if msg_size > self.MAX_INCOMING_MESSAGE_SIZE_SMALL:
 2378:                 log.add_conn("Received message larger than maximum size %s from user %s. "
 2379:                              "Closing connection.", (self.MAX_INCOMING_MESSAGE_SIZE_SMALL, conn.init.target_user))
 2380:                 self._close_connection(conn)
 2381:                 break
 2382: 
 2383:             msg_size_total = msg_size + 4
 2384: 
 2385:             if msg_size_total > buffer_len:
 2386:                 # Buffer is being filled
 2387:                 conn.has_post_init_activity = True
 2388:                 break
 2389: 
 2390:             # Unpack distributed messages
 2391:             msg_type = in_buffer[idx + 4]
 2392: 
 2393:             if msg_type in DISTRIBUTED_MESSAGE_CLASSES:
 2394:                 if not self._process_distrib_message(
 2395:                     conn, msg_type, msg_size, in_buffer, idx + msg_content_offset, idx + msg_size_total
 2396:                 ):
 2397:                     self._close_connection(conn)
 2398:                     return
 2399:             else:
 2400:                 msg_content = in_buffer[idx + msg_content_offset:idx + min(50, msg_size_total)]
 2401:                 log.add_debug("Distrib message type %s size %s contents %s unknown",
 2402:                               (msg_type, msg_size, msg_content))
 2403: 
 2404:             idx += msg_size_total
 2405:             buffer_len -= msg_size_total
 2406: 
```

The frame loops compute `msg_size_total = msg_size + 4` and advance by that amount. The probe demonstrates that server/peer `msg_size` values 0..3 and distributed `msg_size` 0 are not rejected as shorter than the mandatory message-code field before buffer advancement.


## github-branch-master

### U-137 helpers: `unpack_bytes()` / `unpack_string()`

```text
  332:     def unpack_bytes(self):
  333: 
  334:         length, = UINT32_UNPACK(self._message, self._offset)
  335:         start = self._offset + 4
  336:         self._offset = start + length
  337:         content = self._message[start:self._offset]
  338: 
  339:         return content.tobytes()
  340: 
  341:     def unpack_string(self):
  342: 
  343:         length, = UINT32_UNPACK(self._message, self._offset)
  344:         start = self._offset + 4
  345:         self._offset = start + length
  346:         content = self._message[start:self._offset].tobytes()
  347: 
  348:         try:
  349:             string = content.decode("utf-8")
  350: 
```

The master helpers set `_offset = start + length` and slice `_message[start:self._offset]`; a short final payload returns the available bytes/string and leaves `_offset` beyond the actual message length unless a caller explicitly validates the final offset.

### U-175 server frame loop

```text
 1500: 
 1501:         in_buffer = conn.in_buffer
 1502:         buffer_len = len(in_buffer)
 1503:         msg_content_offset = 8
 1504:         idx = 0
 1505: 
 1506:         # Server messages are 8 bytes or greater in length
 1507:         while buffer_len >= msg_content_offset:
 1508:             msg_size, msg_type = DOUBLE_UINT32_UNPACK(in_buffer, idx)
 1509: 
 1510:             if msg_size > self.MAX_INCOMING_MESSAGE_SIZE_LARGE:
 1511:                 log.add_conn("Received message larger than maximum size %s from server. "
 1512:                              "Closing connection.", self.MAX_INCOMING_MESSAGE_SIZE_LARGE)
 1513:                 self._manual_server_disconnect = True
 1514:                 self._close_connection(conn)
 1515:                 return
 1516: 
 1517:             msg_size_total = msg_size + 4
 1518: 
 1519:             if msg_size_total > buffer_len:
 1520:                 # Buffer is being filled
 1521:                 break
 1522: 
 1523:             # Unpack server messages
 1524:             if msg_type in SERVER_MESSAGE_CLASSES:
 1525:                 if not self._process_server_message(
 1526:                     msg_type, msg_size, memoryview(in_buffer)[idx + msg_content_offset:idx + msg_size_total]
 1527:                 ):
 1528:                     self._manual_server_disconnect = True
 1529:                     self._close_connection(conn)
 1530:                     return
 1531:             else:
 1532:                 msg_content = in_buffer[idx + msg_content_offset:idx + min(50, msg_size_total)]
 1533:                 log.add_debug("Server message type %s size %s contents %s unknown",
 1534:                               (msg_type, msg_size, msg_content))
 1535: 
 1536:             idx += msg_size_total
 1537:             buffer_len -= msg_size_total
 1538: 
```

### U-175 peer frame loop

```text
 1862:         msg_content_offset = 8
 1863:         idx = 0
 1864:         search_result_received = False
 1865: 
 1866:         # Peer messages are 8 bytes or greater in length
 1867:         while buffer_len >= msg_content_offset:
 1868:             msg_size, msg_type = DOUBLE_UINT32_UNPACK(in_buffer, idx)
 1869:             msg_size_total = msg_size + 4
 1870:             max_msg_size = self.MAX_INCOMING_MESSAGE_SIZE_MEDIUM
 1871:             msg_class = None
 1872: 
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
 1884: 
 1885:             if msg_size > max_msg_size:
 1886:                 log.add_conn("Received message larger than maximum size %s from user %s. "
 1887:                              "Closing connection.", (max_msg_size, conn.init.target_user))
 1888:                 self._close_connection(conn)
 1889:                 return
 1890: 
 1891:             # Send progress to the main thread
 1892:             if msg_class is SharedFileListResponse:
 1893:                 events.emit_main_thread(
 1894:                     "shared-file-list-progress", conn.init.target_user, conn.sock, buffer_len, msg_size_total)
 1895: 
 1896:             elif msg_class is UserInfoResponse:
 1897:                 events.emit_main_thread(
 1898:                     "user-info-progress", conn.init.target_user, conn.sock, buffer_len, msg_size_total)
 1899: 
 1900:             if msg_size_total > buffer_len:
 1901:                 # Buffer is being filled
 1902:                 break
 1903: 
 1904:             # Unpack peer messages
 1905:             if msg_class:
 1906:                 msg = self._unpack_network_message(
 1907:                     msg_class,
 1908:                     memoryview(in_buffer)[idx + msg_content_offset:idx + msg_size_total],
 1909:                     msg_size,
 1910:                     conn_type="peer",
 1911:                     sock=conn.sock,
 1912:                     addr=conn.addr,
 1913:                     username=conn.init.target_user,
 1914:                     allowed_responses=self._allowed_message_responses.get(msg_class, set())
 1915:                 )
 1916: 
 1917:                 if msg_class is FileSearchResponse:
 1918:                     search_result_received = True
 1919: 
 1920:                 self._emit_network_message_event(msg)
 1921:             else:
 1922:                 msg_content = in_buffer[idx + msg_content_offset:idx + min(50, msg_size_total)]
 1923:                 log.add_debug("Peer message type %s size %s contents %s unknown, from user: %s, address %s",
 1924:                               (msg_type, msg_size, msg_content, conn.init.target_user, conn.addr))
 1925: 
 1926:             idx += msg_size_total
 1927:             buffer_len -= msg_size_total
 1928: 
```

### U-175 distributed frame loop

```text
 2488:         msg_content_offset = 5
 2489:         idx = 0
 2490: 
 2491:         # Distributed messages are 5 bytes or greater in length
 2492:         while buffer_len >= msg_content_offset:
 2493:             msg_size, = UINT32_UNPACK(in_buffer, idx)
 2494: 
 2495:             if msg_size > self.MAX_INCOMING_MESSAGE_SIZE_SMALL:
 2496:                 log.add_conn("Received message larger than maximum size %s from user %s. "
 2497:                              "Closing connection.", (self.MAX_INCOMING_MESSAGE_SIZE_SMALL, conn.init.target_user))
 2498:                 self._close_connection(conn)
 2499:                 break
 2500: 
 2501:             msg_size_total = msg_size + 4
 2502: 
 2503:             if msg_size_total > buffer_len:
 2504:                 # Buffer is being filled
 2505:                 conn.has_post_init_activity = True
 2506:                 break
 2507: 
 2508:             # Unpack distributed messages
 2509:             msg_type = in_buffer[idx + 4]
 2510: 
 2511:             if msg_type in DISTRIBUTED_MESSAGE_CLASSES:
 2512:                 if not self._process_distrib_message(
 2513:                     conn, msg_type, msg_size, memoryview(in_buffer)[idx + msg_content_offset:idx + msg_size_total]
 2514:                 ):
 2515:                     self._close_connection(conn)
 2516:                     return
 2517:             else:
 2518:                 msg_content = in_buffer[idx + msg_content_offset:idx + min(50, msg_size_total)]
 2519:                 log.add_debug("Distrib message type %s size %s contents %s unknown",
 2520:                               (msg_type, msg_size, msg_content))
 2521: 
 2522:             idx += msg_size_total
 2523:             buffer_len -= msg_size_total
 2524: 
```

The frame loops compute `msg_size_total = msg_size + 4` and advance by that amount. The probe demonstrates that server/peer `msg_size` values 0..3 and distributed `msg_size` 0 are not rejected as shorter than the mandatory message-code field before buffer advancement.
