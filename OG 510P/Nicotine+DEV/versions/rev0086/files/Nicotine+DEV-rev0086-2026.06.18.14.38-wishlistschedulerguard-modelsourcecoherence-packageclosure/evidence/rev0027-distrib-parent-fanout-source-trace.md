# rev0027 source trace — DISTRIB-PARENT-FANOUT-01

This trace records the source shapes used by the rev0027 reproducer. It is intentionally compact and references the external rev0003 source bundle rather than embedding source trees.

## github-tag-3.3.10

### slskmessages.py: PossibleParents parser (2042-2064)

```python
 2042: class PossibleParents(ServerMessage):
 2043:     """Server code 102.
 2044: 
 2045:     The server send us a list of 10 possible distributed parents to
 2046:     connect to. This message is sent to us at regular intervals until we
 2047:     tell the server we don't need more possible parents, through a
 2048:     HaveNoParent message.
 2049:     """
 2050: 
 2051:     __slots__ = ("list",)
 2052: 
 2053:     def __init__(self):
 2054:         self.list = {}
 2055: 
 2056:     def parse_network_message(self, message):
 2057:         pos, num = self.unpack_uint32(message)
 2058: 
 2059:         for _ in range(num):
 2060:             pos, username = self.unpack_string(message, pos)
 2061:             pos, ip_address = self.unpack_ip(message, pos)
 2062:             pos, port = self.unpack_uint32(message, pos)
 2063: 
 2064:             self.list[username] = (ip_address, port)
```

### slskproto.py: PossibleParents handler (1341-1351)

```python
 1341:         elif msg_class is PossibleParents:
 1342:             # Server sent a list of 10 potential parents, whose purpose is to forward us search requests.
 1343:             # We attempt to connect to them all at once, since connection errors are fairly common.
 1344: 
 1345:             self._potential_parents = msg.list
 1346:             log.add_conn("Server sent us a list of %s possible parents", len(msg.list))
 1347: 
 1348:             if self._parent_conn is None and self._potential_parents:
 1349:                 for username, addr in self._potential_parents.items():
 1350:                     log.add_conn("Attempting parent connection to user %s", username)
 1351:                     self._initiate_connection_to_peer(username, ConnectionType.DISTRIBUTED, in_address=addr)
```

### slskproto.py: Distributed child adoption (2062-2109)

```python
 2062:     def _accept_child_peer_connection(self, conn):
 2063: 
 2064:         if conn.init.conn_type != ConnectionType.DISTRIBUTED:
 2065:             return
 2066: 
 2067:         username = conn.init.target_user
 2068: 
 2069:         if username == self._server_username:
 2070:             # We can't connect to ourselves
 2071:             return
 2072: 
 2073:         if username in self._potential_parents:
 2074:             # This is not a child peer, ignore
 2075:             return
 2076: 
 2077:         if self._parent_conn is None and not self._is_server_parent:
 2078:             # We have no parent user and the server hasn't sent search requests, no point
 2079:             # in accepting child peers
 2080:             log.add_conn("Rejecting distributed child peer connection from user %s, since we have no parent", username)
 2081:             self._close_connection(conn)
 2082:             return
 2083: 
 2084:         if username in self._child_peers:
 2085:             log.add_conn("Rejecting distributed child peer connection from user %s, since an existing connection "
 2086:                          "already exists", username)
 2087:             self._close_connection(conn)
 2088:             return
 2089: 
 2090:         if len(self._child_peers) >= self._max_distrib_children:
 2091:             log.add_conn("Rejecting distributed child peer connection from user %s, since child peer limit "
 2092:                          "of %s was reached", (username, self._max_distrib_children))
 2093:             self._close_connection(conn)
 2094:             return
 2095: 
 2096:         self._child_peers[username] = conn
 2097:         self._send_message_to_peer(username, DistribBranchLevel(self._branch_level))
 2098: 
 2099:         if self._parent_conn is not None:
 2100:             # Only sent when we're not the branch root
 2101:             self._send_message_to_peer(username, DistribBranchRoot(self._branch_root))
 2102: 
 2103:         log.add_conn("Adopting user %s as distributed child peer. Number of current child peers: %s",
 2104:                      (username, len(self._child_peers)))
 2105: 
 2106:         if len(self._child_peers) >= self._max_distrib_children:
 2107:             log.add_conn("Maximum number of distributed child peers reached (%s), "
 2108:                          "no longer accepting new connections", self._max_distrib_children)
 2109:             self._send_message_to_server(AcceptChildren(False))
```

### slskproto.py: 3.3.10 EmbeddedMessage before-validation fanout (1254-1256)

```python
 1254:         if msg_class is EmbeddedMessage:
 1255:             self._distribute_embedded_message(msg)
 1256:             msg = self._unpack_embedded_message(msg)
```

### slskproto.py: 3.3.10 _distribute_embedded_message raw fanout (2137-2145)

```python
 2137:     def _distribute_embedded_message(self, msg):
 2138:         """Distributes an embedded message from the server to our child
 2139:         peers."""
 2140: 
 2141:         if self._parent_conn is not None:
 2142:             # The server shouldn't send embedded messages while it's not our parent, but let's be safe
 2143:             return
 2144: 
 2145:         self._send_message_to_child_peers(DistribEmbeddedMessage(msg.distrib_code, msg.distrib_message))
```

### slskproto.py: DistribBranchRoot parent handler (2299-2304)

```python
 2299:         elif msg_class is DistribBranchRoot:
 2300:             if not self._verify_parent_connection(conn, msg_class):
 2301:                 return False
 2302: 
 2303:             self._set_branch_root(msg.root_username)
 2304: 
```

## github-branch-3.3.x

### slskmessages.py: PossibleParents parser (2057-2084)

```python
 2057: class PossibleParents(ServerMessage):
 2058:     """Server code 102.
 2059: 
 2060:     The server send us a list of max 10 possible distributed parents to
 2061:     connect to. Messages of this type are sent to us at regular intervals,
 2062:     until we tell the server we don't need more possible parents with a
 2063:     HaveNoParent message.
 2064: 
 2065:     The received list always contains users whose upload speed is higher than
 2066:     our own. If we have the highest upload speed on the server, we become a
 2067:     branch root, and start receiving EmbeddedMessage messages directly from
 2068:     the server.
 2069:     """
 2070: 
 2071:     __slots__ = ("list",)
 2072: 
 2073:     def __init__(self):
 2074:         self.list = {}
 2075: 
 2076:     def parse_network_message(self, message):
 2077:         pos, num = self.unpack_uint32(message)
 2078: 
 2079:         for _ in range(num):
 2080:             pos, username = self.unpack_string(message, pos)
 2081:             pos, ip_address = self.unpack_ip(message, pos)
 2082:             pos, port = self.unpack_uint32(message, pos)
 2083: 
 2084:             self.list[username] = (ip_address, port)
```

### slskproto.py: PossibleParents handler (1421-1431)

```python
 1421:         elif msg_class is PossibleParents:
 1422:             # Server sent a list of 10 potential parents, whose purpose is to forward us search requests.
 1423:             # We attempt to connect to them all at once, since connection errors are fairly common.
 1424: 
 1425:             self._potential_parents = msg.list
 1426:             log.add_conn("Server sent us a list of %s possible parents", len(msg.list))
 1427: 
 1428:             if self._parent_conn is None and self._potential_parents:
 1429:                 for username, addr in self._potential_parents.items():
 1430:                     log.add_conn("Attempting parent connection to user %s", username)
 1431:                     self._initiate_connection_to_peer(username, ConnectionType.DISTRIBUTED, in_address=addr)
```

### slskproto.py: Distributed child adoption (2145-2190)

```python
 2145:     def _accept_child_peer_connection(self, conn):
 2146: 
 2147:         if conn.init.conn_type != ConnectionType.DISTRIBUTED:
 2148:             return
 2149: 
 2150:         username = conn.init.target_user
 2151: 
 2152:         if username == self._server_username:
 2153:             # We can't connect to ourselves
 2154:             return
 2155: 
 2156:         if username in self._potential_parents:
 2157:             # This is not a child peer, ignore
 2158:             return
 2159: 
 2160:         if self._parent_conn is None and not self._is_server_parent:
 2161:             # We have no parent user and the server hasn't sent search requests, no point
 2162:             # in accepting child peers
 2163:             log.add_conn("Rejecting distributed child peer connection from user %s, since we have no parent", username)
 2164:             self._close_connection(conn)
 2165:             return
 2166: 
 2167:         if username in self._child_peers:
 2168:             log.add_conn("Rejecting distributed child peer connection from user %s, since an existing connection "
 2169:                          "already exists", username)
 2170:             self._close_connection(conn)
 2171:             return
 2172: 
 2173:         if len(self._child_peers) >= self._max_distrib_children:
 2174:             log.add_conn("Rejecting distributed child peer connection from user %s, since child peer limit "
 2175:                          "of %s was reached", (username, self._max_distrib_children))
 2176:             self._close_connection(conn)
 2177:             return
 2178: 
 2179:         self._child_peers[username] = conn
 2180:         self._send_message_to_peer(username, DistribBranchLevel(self._branch_level))
 2181:         self._send_message_to_peer(username, DistribBranchRoot(self._branch_root))
 2182: 
 2183:         log.add_conn("Adopting user %s as distributed child peer. Number of current child peers: %s",
 2184:                      (username, len(self._child_peers)))
 2185: 
 2186:         if len(self._child_peers) >= self._max_distrib_children:
 2187:             log.add_conn("Maximum number of distributed child peers reached (%s), "
 2188:                          "no longer accepting new connections", self._max_distrib_children)
 2189:             self._send_message_to_server(AcceptChildren(False))
 2190: 
```

### slskproto.py: EmbeddedMessage unpack only supports DistribSearch (710-732)

```python
  710:     def _unpack_embedded_message(cls, msg, sock=None, username=None):
  711:         """This message embeds a distributed message.
  712: 
  713:         We unpack the distributed message and process it.
  714:         """
  715: 
  716:         msg_type = msg.distrib_code
  717:         distrib_class = DISTRIBUTED_MESSAGE_CLASSES.get(msg_type)
  718: 
  719:         if distrib_class is not DistribSearch:
  720:             log.add_debug("Embedded distrib message type %s unexpected, ignoring", msg_type)
  721:             return None
  722: 
  723:         unpacked_msg = cls._unpack_network_message(
  724:             distrib_class,
  725:             msg.distrib_message,
  726:             len(msg.distrib_message),
  727:             conn_type="distrib",
  728:             sock=sock,
  729:             username=username
  730:         )
  731: 
  732:         return unpacked_msg
```

### slskproto.py: DistribBranchRoot parent handler (2356-2361)

```python
 2356:         elif msg_class is DistribBranchRoot:
 2357:             if not self._verify_parent_connection(conn, msg_class):
 2358:                 return False
 2359: 
 2360:             self._set_branch_root(msg.root_username)
 2361: 
```

## github-branch-master

### slskmessages.py: PossibleParents parser (2144-2172)

```python
 2144: class PossibleParents(ServerMessage):
 2145:     """Server code 102.
 2146: 
 2147:     The server send us a list of max 10 possible distributed parents to
 2148:     connect to. Messages of this type are sent to us at regular intervals,
 2149:     until we tell the server we don't need more possible parents with a
 2150:     HaveNoParent message.
 2151: 
 2152:     The received list always contains users whose upload speed is higher than
 2153:     our own. If we have the highest upload speed on the server, we become a
 2154:     branch root, and start receiving EmbeddedMessage messages directly from
 2155:     the server.
 2156:     """
 2157: 
 2158:     __slots__ = ("list",)
 2159: 
 2160:     def __init__(self, *, msg_content=None):
 2161:         ServerMessage.__init__(self, msg_content)
 2162:         self.list = {}
 2163: 
 2164:     def parse_network_message(self):
 2165:         num = self.unpack_uint32()
 2166: 
 2167:         for _ in range(num):
 2168:             username = self.unpack_string()
 2169:             ip_address = self.unpack_ip()
 2170:             port = self.unpack_uint32()
 2171: 
 2172:             self.list[username] = ParentCandidate(username, ip_address, port)
```

### slskproto.py: PossibleParents handler (1457-1472)

```python
 1457:         elif msg_class is PossibleParents:
 1458:             # Server sent a list of 10 potential parents, whose purpose is to forward us search requests.
 1459:             # We attempt to connect to them all at once, since connection errors are fairly common.
 1460: 
 1461:             if self._parent is None:
 1462:                 self._close_parent_candidate_connections()
 1463: 
 1464:                 self._potential_parents = msg.list
 1465:                 log.add_conn("Server sent us a list of %s possible parents", len(msg.list))
 1466: 
 1467:                 for username, parent_candidate in self._potential_parents.items():
 1468:                     log.add_conn("Attempting parent connection to user %s", username)
 1469:                     self._initiate_connection_to_peer(
 1470:                         username, ConnectionType.DISTRIBUTED,
 1471:                         in_address=(parent_candidate.ip_address, parent_candidate.port)
 1472:                     )
```

### slskproto.py: Distributed child adoption (2182-2227)

```python
 2182:     def _accept_child_peer_connection(self, conn):
 2183: 
 2184:         if conn.init.conn_type != ConnectionType.DISTRIBUTED:
 2185:             return
 2186: 
 2187:         username = conn.init.target_user
 2188: 
 2189:         if username == self._server_username:
 2190:             # We can't connect to ourselves
 2191:             return
 2192: 
 2193:         if username in self._potential_parents:
 2194:             # This is not a child peer, ignore
 2195:             return
 2196: 
 2197:         if self._parent is None and not self._is_server_parent:
 2198:             # We have no parent user and the server hasn't sent search requests, no point
 2199:             # in accepting child peers
 2200:             log.add_conn("Rejecting distributed child peer connection from user %s, since we have no parent", username)
 2201:             self._close_connection(conn)
 2202:             return
 2203: 
 2204:         if username in self._child_peers:
 2205:             log.add_conn("Rejecting distributed child peer connection from user %s, since an existing connection "
 2206:                          "already exists", username)
 2207:             self._close_connection(conn)
 2208:             return
 2209: 
 2210:         if len(self._child_peers) >= self._max_distrib_children:
 2211:             log.add_conn("Rejecting distributed child peer connection from user %s, since child peer limit "
 2212:                          "of %s was reached", (username, self._max_distrib_children))
 2213:             self._close_connection(conn)
 2214:             return
 2215: 
 2216:         self._child_peers[username] = conn
 2217:         self._send_message_to_peer(username, DistribBranchLevel(self._branch_level))
 2218:         self._send_message_to_peer(username, DistribBranchRoot(self._branch_root))
 2219: 
 2220:         log.add_conn("Adopting user %s as distributed child peer. Number of current child peers: %s",
 2221:                      (username, len(self._child_peers)))
 2222: 
 2223:         if len(self._child_peers) >= self._max_distrib_children:
 2224:             log.add_conn("Maximum number of distributed child peers reached (%s), "
 2225:                          "no longer accepting new connections", self._max_distrib_children)
 2226:             self._send_message_to_server(AcceptChildren(False))
 2227: 
```

### slskproto.py: EmbeddedMessage server handler validates before fanout (1345-1366)

```python
 1345:         if msg_class is EmbeddedMessage:
 1346:             if self._parent is not None:
 1347:                 # Another peer is currently our parent. The server shouldn't send embedded messages
 1348:                 # while it's not our parent, but let's be safe.
 1349:                 return True
 1350: 
 1351:             unpacked_msg = self._unpack_embedded_message(msg)
 1352: 
 1353:             if unpacked_msg is None:
 1354:                 # Ignore unknown message and keep connection open
 1355:                 return True
 1356: 
 1357:             if not self._is_server_parent:
 1358:                 self._is_server_parent = True
 1359: 
 1360:                 if len(self._child_peers) < self._max_distrib_children:
 1361:                     self._send_message_to_server(AcceptChildren(True))
 1362: 
 1363:                 log.add_conn("Server is our parent, ready to distribute search requests as a branch root")
 1364: 
 1365:             self._send_message_to_child_peers(unpacked_msg, msg.distrib_message)
 1366:             msg = unpacked_msg
```

### slskproto.py: EmbeddedMessage unpack only supports valid DistribSearch (727-753)

```python
  727:     def _unpack_embedded_message(cls, msg, sock=None, username=None):
  728:         """This message embeds a distributed message.
  729: 
  730:         We unpack the distributed message and process it.
  731:         """
  732: 
  733:         msg_type = msg.distrib_code
  734:         distrib_class = DISTRIBUTED_MESSAGE_CLASSES.get(msg_type)
  735: 
  736:         if distrib_class is not DistribSearch:
  737:             log.add_debug("Embedded distrib message type %s unexpected, ignoring", msg_type)
  738:             return None
  739: 
  740:         unpacked_msg = cls._unpack_network_message(
  741:             distrib_class,
  742:             msg.distrib_message,
  743:             len(msg.distrib_message),
  744:             conn_type="distrib",
  745:             sock=sock,
  746:             username=username
  747:         )
  748: 
  749:         if unpacked_msg.identifier != "1":
  750:             # Ignore invalid message
  751:             return None
  752: 
  753:         return unpacked_msg
```

### slskproto.py: DistribBranchRoot parent handler (2452-2475)

```python
 2452:         elif msg_class is DistribBranchRoot:
 2453:             if not msg.root_username:
 2454:                 log.add_conn("Received an empty branch root value from user %s. "
 2455:                              "Closing connection.", username)
 2456:                 return False
 2457: 
 2458:             parent_status = self._verify_parent_status(conn, msg_class)
 2459: 
 2460:             if parent_status == ParentStatus.ACCEPTED:
 2461:                 self._branch_root = msg.root_username
 2462:                 self._send_message_to_server(BranchRoot(self._branch_root))
 2463:                 self._send_message_to_child_peers(DistribBranchRoot(self._branch_root))
 2464: 
 2465:                 log.add_conn("Received a branch root update from our parent. Our new branch root is %s",
 2466:                              self._branch_root)
 2467: 
 2468:             elif parent_status == ParentStatus.WAITING and username in self._potential_parents:
 2469:                 parent_candidate = self._potential_parents[username]
 2470:                 parent_candidate.conn = conn
 2471:                 parent_candidate.branch_root = msg.root_username
 2472: 
 2473:             self._emit_network_message_event(msg)
 2474: 
 2475:             if parent_status == ParentStatus.REJECTED:
```
