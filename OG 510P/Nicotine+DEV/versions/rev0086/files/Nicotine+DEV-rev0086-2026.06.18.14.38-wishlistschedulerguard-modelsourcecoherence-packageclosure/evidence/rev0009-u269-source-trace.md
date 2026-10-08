# rev0009 U-269 upload completion lifetime source trace

Local probe result: after the networking layer reports offset+bytes_sent == size, the upload remains active until a file-connection-closed event is received. Static source trace explains why this is a hardening item but not promoted strict in rev0009.

## github-tag-3.3.10

### uploads.py FileTransferInit/progress/close

```python
 1141: 
 1142:         self._update_transfer_progress(
 1143:             upload, stat_id="uploaded_size",
 1144:             current_byte_offset=(offset + bytes_sent) if offset is not None else None,
 1145:             speed=speed
 1146:         )
 1147:         self._update_transfer(upload)
 1148: 
 1149:     def _file_connection_closed(self, username, token, sock, timed_out):
 1150:         """A file upload connection has closed for any reason."""
 1151: 
 1152:         upload = self.active_users.get(username, {}).get(token)
 1153: 
 1154:         if upload is None:
 1155:             return
 1156: 
 1157:         if upload.sock != sock:
 1158:             return
 1159: 
 1160:         if not timed_out and upload.current_byte_offset is not None and upload.current_byte_offset >= upload.size:
 1161:             # We finish the upload here in case the downloading peer has a slow/limited download
 1162:             # speed and finishes later than us
 1163: 
 1164:             self._finish_transfer(upload)
 1165: 
 1166:             if upload.avg_speed > 0:
 1167:                 # Inform the server about the average upload speed for this transfer
 1168:                 log.add_transfer("Sending average upload speed %s to the server", upload.avg_speed)
 1169:                 core.send_message_to_server(SendUploadSpeed(upload.avg_speed))
 1170: 
 1171:             return
 1172: 
 1173:         if core.users.statuses.get(upload.username) == UserStatus.OFFLINE:
 1174:             status = TransferStatus.USER_LOGGED_OFF
 1175:         else:
 1176:             status = TransferStatus.CANCELLED
 1177: 
 1178:             # Transfer ended abruptly. Tell the peer to re-queue the file. If the transfer was
 1179:             # intentionally cancelled, the peer should ignore this message.
 1180:             core.send_message_to_peer(upload.username, UploadFailed(upload.virtual_path))
 1181: 
 1182:         if not self._auto_clear_transfer(upload):
 1183:             self._abort_transfer(upload, status=status)
 1184: 
 1185:         self._check_upload_queue()
 1186: 
 1187:     def _place_in_queue_request(self, msg):
 1188:         """Peer code 51."""
 1189: 
 1190:         username = msg.username
 1191:         virtual_path = msg.file
 1192:         upload = self.queued_users.get(username, {}).get(virtual_path)
 1193: 
 1194:         if upload is None:
 1195:             return
 1196: 
 1197:         is_fifo_queue = config.sections["transfers"]["fifoqueue"]
 1198:         is_privileged_queue = self.is_privileged(username)
 1199:         privileged_queued_users = {k: len(v) for k, v in self.queued_users.items() if self.is_privileged(k)}
 1200:         queue_position = 0
 1201: 
 1202:         if is_fifo_queue:
 1203:             if is_privileged_queue != self._privileged_position_requested or upload not in self._queue_positions:
 1204:                 self._queue_position_users.clear()
 1205: 
 1206:                 if is_privileged_queue:
 1207:                     self._queue_positions.clear()
 1208:                     position = 1
 1209: 
 1210:                     for i_upload in self.queued_transfers:
 1211:                         if i_upload.username in privileged_queued_users:
 1212:                             self._queue_positions[i_upload] = position
 1213:                             position += 1
 1214:                 else:
 1215:                     self._queue_positions = {
 1216:                         i_upload: position
 1217:                         for position, i_upload in enumerate(self.queued_transfers, start=1)
 1218:                     }
 1219: 
 1220:             queue_position = self._queue_positions[upload]
 1221:         else:
 1222:             user_queue_positions = self._queue_position_users[username]
 1223: 
 1224:             if upload not in user_queue_positions:
 1225:                 self._queue_positions.clear()
 1226:                 user_queue_positions.update({
 1227:                     i_upload: position
 1228:                     for position, i_upload in enumerate(self.queued_users[username].values(), start=1)
 1229:                 })
 1230: 
 1231:             if is_privileged_queue:
 1232:                 num_queued_users = len(privileged_queued_users)
 1233:             else:
 1234:                 # Cycling through privileged users first
 1235:                 queue_position += sum(
 1236:                     num_queued_uploads for num_queued_uploads in privileged_queued_users.values())
 1237:                 num_queued_users = len(self.queued_users)
 1238: 
 1239:             queue_position += num_queued_users + user_queue_positions[upload]
 1240: 
 1241:         self._privileged_position_requested = is_privileged_queue
 1242: 
 1243:         if queue_position > 0:
 1244:             core.send_message_to_peer(
 1245:                 username, PlaceInQueueResponse(virtual_path, queue_position))
 1246: 
 1247:         # Update queue position in our list of uploads
 1248:         upload.queue_position = queue_position
 1249:         self._update_transfer(upload, update_parent=False)
```

### slskproto.py upload processing and connection checks

```python
  625:         return False
  626: 
  627:     @staticmethod
  628:     def _pack_network_message(msg):
  629: 
  630:         try:
  631:             return msg.make_network_message()
  632: 
  633:         except Exception:
  634:             from traceback import format_exc
```

```python
 1085:         elif self._server_timeout_value == -1:
 1086:             # Add jitter to spread out connection attempts from Nicotine+ clients
 1087:             # in case server goes down
 1088:             self._server_timeout_value = random.randint(5, 15)
 1089: 
 1090:         elif 0 < self._server_timeout_value < 300:
 1091:             # Exponential backoff, max 5 minute wait
 1092:             self._server_timeout_value *= 2
 1093: 
 1094:         self._server_timeout_time = time.monotonic() + self._server_timeout_value
 1095:         log.add(_("Reconnecting to server in %s seconds"), self._server_timeout_value)
 1096: 
 1097:     @staticmethod
 1098:     def _set_server_socket_keepalive(sock, idle=10, interval=2):
 1099:         """Ensure we are disconnected from the server in case of connectivity
 1100:         issues, by sending TCP keepalive pings.
 1101: 
 1102:         Assuming default values are used, once we reach 10 seconds of
 1103:         idle time, we start sending keepalive pings once every 2
 1104:         seconds. If 10 failed pings have been sent in a row (20
 1105:         seconds), the connection is presumed dead.
 1106:         """
 1107: 
 1108:         count = 10
```

```python
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
 2110: 
 2111:     def _remove_child_peer_connection(self, username):
 2112: 
 2113:         self._child_peers.pop(username, None)
 2114: 
 2115:         if not self._should_process_queue:
 2116:             return
 2117: 
 2118:         if len(self._child_peers) == self._max_distrib_children - 1:
 2119:             log.add_conn("Available to accept a new distributed child peer")
 2120:             self._send_message_to_server(AcceptChildren(True))
 2121: 
 2122:         log.add_conn("Number of current child peers: %s", len(self._child_peers))
 2123: 
 2124:     def _send_message_to_child_peers(self, msg):
 2125: 
 2126:         msg_class = msg.__class__
 2127:         msg_attrs = [getattr(msg, s) for s in msg.__slots__]
 2128:         msgs = []
 2129: 
 2130:         for conn in self._child_peers.values():
 2131:             msg_child = msg_class(*msg_attrs)
 2132:             msg_child.sock = conn.sock
 2133:             msgs.append(msg_child)
 2134: 
 2135:         self._process_outgoing_messages(msgs)
```

## github-branch-3.3.x

### uploads.py FileTransferInit/progress/close

```python
 1141: 
 1142:         if upload is None:
 1143:             return
 1144: 
 1145:         if upload.sock != sock:
 1146:             return
 1147: 
 1148:         if not timed_out and upload.current_byte_offset is not None and upload.current_byte_offset >= upload.size:
 1149:             # We finish the upload here in case the downloading peer has a slow/limited download
 1150:             # speed and finishes later than us
 1151: 
 1152:             self._finish_transfer(upload)
 1153: 
 1154:             if upload.avg_speed > 0:
 1155:                 # Inform the server about the average upload speed for this transfer
 1156:                 log.add_transfer("Sending average upload speed %s to the server", upload.avg_speed)
 1157:                 core.send_message_to_server(SendUploadSpeed(upload.avg_speed))
 1158: 
 1159:             return
 1160: 
 1161:         if core.users.statuses.get(upload.username) == UserStatus.OFFLINE:
 1162:             status = TransferStatus.USER_LOGGED_OFF
 1163:         else:
 1164:             status = TransferStatus.CANCELLED
 1165: 
 1166:             # Transfer ended abruptly. Tell the peer to re-queue the file. If the transfer was
 1167:             # intentionally cancelled, the peer should ignore this message.
 1168:             core.send_message_to_peer(upload.username, UploadFailed(upload.virtual_path))
 1169: 
 1170:         if not self._auto_clear_transfer(upload):
 1171:             self._abort_transfer(upload, status=status)
 1172: 
 1173:         self._check_upload_queue()
 1174: 
 1175:     def _place_in_queue_request(self, msg):
 1176:         """Peer code 51."""
 1177: 
 1178:         username = msg.username
 1179:         virtual_path = msg.file
 1180:         upload = self.queued_users.get(username, {}).get(virtual_path)
 1181: 
 1182:         if upload is None:
 1183:             return
 1184: 
 1185:         is_fifo_queue = config.sections["transfers"]["fifoqueue"]
 1186:         is_privileged_queue = self.is_privileged(username)
 1187:         privileged_queued_users = {k: len(v) for k, v in self.queued_users.items() if self.is_privileged(k)}
 1188:         queue_position = 0
 1189: 
 1190:         if is_fifo_queue:
 1191:             if is_privileged_queue != self._privileged_position_requested or upload not in self._queue_positions:
 1192:                 self._queue_position_users.clear()
 1193: 
 1194:                 if is_privileged_queue:
 1195:                     self._queue_positions.clear()
 1196:                     position = 1
 1197: 
 1198:                     for i_upload in self.queued_transfers:
 1199:                         if i_upload.username in privileged_queued_users:
 1200:                             self._queue_positions[i_upload] = position
 1201:                             position += 1
 1202:                 else:
 1203:                     self._queue_positions = {
 1204:                         i_upload: position
 1205:                         for position, i_upload in enumerate(self.queued_transfers, start=1)
 1206:                     }
 1207: 
 1208:             queue_position = self._queue_positions[upload]
 1209:         else:
 1210:             user_queue_positions = self._queue_position_users[username]
 1211: 
 1212:             if upload not in user_queue_positions:
 1213:                 self._queue_positions.clear()
 1214:                 user_queue_positions.update({
 1215:                     i_upload: position
 1216:                     for position, i_upload in enumerate(self.queued_users[username].values(), start=1)
 1217:                 })
 1218: 
 1219:             if is_privileged_queue:
 1220:                 num_queued_users = len(privileged_queued_users)
 1221:             else:
 1222:                 # Cycling through privileged users first
 1223:                 queue_position += sum(
 1224:                     num_queued_uploads for num_queued_uploads in privileged_queued_users.values())
 1225:                 num_queued_users = len(self.queued_users)
 1226: 
 1227:             queue_position += num_queued_users + user_queue_positions[upload]
 1228: 
 1229:         self._privileged_position_requested = is_privileged_queue
 1230: 
 1231:         if queue_position > 0:
 1232:             core.send_message_to_peer(
 1233:                 username, PlaceInQueueResponse(virtual_path, queue_position))
 1234: 
 1235:         # Update queue position in our list of uploads
 1236:         upload.queue_position = queue_position
 1237:         self._update_transfer(upload, update_parent=False)
```

### slskproto.py upload processing and connection checks

```python
  625: 
  626:     def _bind_socket_interface(self, sock):
  627:         """Attempt to bind socket to an IP address, if provided with the
  628:         --bindip CLI argument. Otherwise retrieve the IP address of the
  629:         requested interface name, cache it for later, and bind to it.
  630:         """
  631: 
  632:         if self._interface_address:
  633:             if sock is not self._listen_socket:
  634:                 NetworkInterfaces.bind_to_interface(sock, self._interface_name, self._interface_address)
```

```python
 1085:         inactive_conns = set()
 1086:         stale_conns = set()
 1087: 
 1088:         for conn in self._conns.values():
 1089:             if not conn.is_established:
 1090:                 if (current_time - conn.last_active) > self.IN_PROGRESS_STALE_AFTER:
 1091:                     stale_conns.add(conn)
 1092: 
 1093:             elif self._is_connection_inactive(conn, current_time, num_sockets):
 1094:                 inactive_conns.add(conn)
 1095: 
 1096:             elif conn in self._file_download_msgs:
 1097:                 file_download = self._file_download_msgs[conn]
 1098: 
 1099:                 events.emit_main_thread(
 1100:                     "file-download-progress",
 1101:                     username=conn.init.target_user, token=file_download.token,
 1102:                     bytes_left=file_download.leftbytes, speed=file_download.speed
 1103:                 )
 1104:                 file_download.speed = 0
 1105: 
 1106:             elif conn in self._file_upload_msgs:
 1107:                 file_upload = self._file_upload_msgs[conn]
 1108: 
```

```python
 2095:                 username=conn.init.target_user, token=file_upload.token,
 2096:                 offset=file_upload.offset, bytes_sent=file_upload.sentbytes
 2097:             )
 2098:         return True
 2099: 
 2100:     def _process_file_input(self, conn):
 2101:         """Reads file messages from the input buffer of a 'F' connection."""
 2102: 
 2103:         in_buffer = conn.in_buffer
 2104:         idx = 0
 2105: 
 2106:         if conn not in self._file_init_msgs:
 2107:             idx = self._process_file_init_message(conn, in_buffer)
 2108: 
 2109:         elif conn in self._file_upload_msgs:
 2110:             idx = self._process_file_offset_message(conn, in_buffer)
 2111: 
 2112:         if idx:
 2113:             del in_buffer[:idx]
 2114:             conn.has_post_init_activity = True
 2115: 
 2116:     def _process_file_output(self, conn, msg):
 2117: 
 2118:         msg_class = msg.__class__
 2119: 
 2120:         # Pack file messages
 2121:         if msg_class is FileTransferInit:
 2122:             msg_content = self._pack_network_message(msg)
 2123: 
 2124:             if msg_content is None:
 2125:                 return
 2126: 
 2127:             self._file_init_msgs[conn] = msg
 2128:             conn.out_buffer += msg_content
 2129: 
 2130:             self._emit_network_message_event(msg)
 2131: 
 2132:         elif msg_class is FileOffset:
 2133:             msg_content = self._pack_network_message(msg)
 2134: 
 2135:             if msg_content is None:
```

## github-branch-master

### uploads.py FileTransferInit/progress/close

```python
 1141:     def _file_transfer_init(self, msg):
 1142:         """We are requesting to start uploading a file to a peer."""
 1143: 
 1144:         if not msg.is_outgoing:
 1145:             # Transfer init message received from another peer, ignore
 1146:             return
 1147: 
 1148:         username = msg.username
 1149:         token = msg.token
 1150:         upload = self.active_users.get(username, {}).get(token)
 1151: 
 1152:         if upload is None or upload.sock is not None:
 1153:             log.add_transfer("Sending file upload init message with unknown token %s, closing connection", token)
 1154:             core.send_message_to_network_thread(CloseConnection(msg.sock))
 1155:             return
 1156: 
 1157:         virtual_path = upload.virtual_path
 1158:         sock = upload.sock = msg.sock
 1159:         need_update = True
 1160:         upload_started = False
 1161: 
 1162:         log.add_transfer("Initializing upload with token %s for file %s to user %s",
 1163:                          (token, virtual_path, username))
 1164: 
 1165:         real_path = core.shares.virtual2real(
 1166:             virtual_path,
 1167:             revert_backslash=upload.is_backslash_path,
 1168:             is_lowercase_path=upload.is_lowercase_path
 1169:         )
 1170: 
 1171:         try:
 1172:             # Open File
 1173:             file_handle = open(encode_path(real_path), "rb")  # pylint: disable=consider-using-with
 1174: 
 1175:         except OSError as error:
 1176:             log.add(_("Upload I/O error: %s"), error)
 1177:             self._abort_transfer(upload, status=TransferStatus.LOCAL_FILE_ERROR)
 1178:             self._check_upload_queue()
 1179: 
 1180:         else:
 1181:             upload.file_handle = file_handle
 1182:             upload.start_time = time.monotonic() - upload.time_elapsed
 1183: 
 1184:             core.statistics.append_stat_value("started_uploads", 1)
 1185:             upload_started = True
 1186: 
 1187:             log.add_upload(
 1188:                 _("Upload started: user %(user)s, IP address %(ip)s, file %(file)s"), {
 1189:                     "user": username,
 1190:                     "ip": core.users.addresses.get(username),
 1191:                     "file": virtual_path
 1192:                 }
 1193:             )
 1194: 
 1195:             if upload.size > 0:
 1196:                 upload.status = TransferStatus.TRANSFERRING
 1197:                 core.send_message_to_network_thread(UploadFile(
 1198:                     sock=sock, token=token, file=file_handle, size=upload.size
 1199:                 ))
 1200: 
 1201:             else:
 1202:                 self._finish_transfer(upload)
 1203:                 need_update = False
 1204: 
 1205:         if need_update:
 1206:             self._update_transfer(upload)
 1207: 
 1208:         if upload_started:
 1209:             # Must be be emitted after the final update to prevent inconsistent state
 1210:             core.pluginhandler.upload_started_notification(username, virtual_path, real_path)
 1211: 
 1212:     def _file_upload_progress(self, username, token, offset, bytes_sent, speed=None):
 1213:         """A file upload is in progress."""
 1214: 
 1215:         upload = self.active_users.get(username, {}).get(token)
 1216: 
 1217:         if upload is None:
 1218:             return
 1219: 
 1220:         if upload.request_timer_id is not None:
 1221:             events.cancel_scheduled(upload.request_timer_id)
 1222:             upload.request_timer_id = None
 1223: 
 1224:         if upload.last_byte_offset is None:
 1225:             upload.last_byte_offset = offset
 1226: 
 1227:         self._update_transfer_progress(
 1228:             upload, stat_id="uploaded_size",
 1229:             current_byte_offset=(offset + bytes_sent) if offset is not None else None,
 1230:             speed=speed
 1231:         )
 1232:         self._update_transfer(upload)
 1233: 
 1234:     def _file_connection_closed(self, username, token, sock, timed_out):
 1235:         """A file upload connection has closed for any reason."""
 1236: 
 1237:         upload = self.active_users.get(username, {}).get(token)
 1238: 
 1239:         if upload is None:
 1240:             return
 1241: 
 1242:         if upload.sock != sock:
 1243:             return
 1244: 
 1245:         if not timed_out and upload.current_byte_offset is not None and upload.current_byte_offset >= upload.size:
 1246:             # We finish the upload here in case the downloading peer has a slow/limited download
 1247:             # speed and finishes later than us
 1248: 
 1249:             self._finish_transfer(upload)
 1250: 
 1251:             if upload.avg_speed > 0:
 1252:                 # Inform the server about the average upload speed for this transfer
 1253:                 log.add_transfer("Sending average upload speed %s to the server", upload.avg_speed)
 1254:                 core.send_message_to_server(SendUploadSpeed(upload.avg_speed))
 1255: 
 1256:             return
```

### slskproto.py upload processing and connection checks

```python
  625:     def _is_connection_still_active(self, conn):
  626: 
  627:         init = conn.init
  628: 
  629:         if init is not None and (init.conn_type != "P" or init.target_user == self._server_username):
  630:             # Distributed and file connections, as well as connections to ourselves,
  631:             # are critical. Always assume they are active.
  632:             return True
  633: 
  634:         return len(conn.out_buffer) > 0 or len(conn.in_buffer) > 0
```

```python
 1085:     def _is_connection_inactive(self, conn, current_time, num_sockets):
 1086: 
 1087:         if conn is self._server_conn:
 1088:             return False
 1089: 
 1090:         if num_sockets >= self.MAX_SOCKETS and not self._is_connection_still_active(conn):
 1091:             # Connection limit reached, close connection if inactive
 1092:             return True
 1093: 
 1094:         time_diff = (current_time - conn.last_active)
 1095: 
 1096:         if not conn.has_post_init_activity and time_diff > self.CONNECTION_MAX_IDLE_GHOST:
 1097:             # "Ghost" connections can appear when an indirect connection is established,
 1098:             # search results arrive, we close the connection, and the direct connection attempt
 1099:             # succeeds afterwrds. Since the peer already sent a search result message, this connection
 1100:             # idles without any messages ever being sent beyond PeerInit. Close it sooner than regular
 1101:             # idling connections to prevent connections from piling up.
 1102:             return True
 1103: 
 1104:         if time_diff > self.CONNECTION_MAX_IDLE:
 1105:             # No recent activity, peer connection is stale
 1106:             return True
 1107: 
 1108:         return False
```

```python
 2095:     def _process_upload(self, conn, num_sent_bytes, current_time):
 2096: 
 2097:         file_upload = self._file_upload_msgs[conn]
 2098: 
 2099:         if file_upload.offset is None:
 2100:             return True
 2101: 
 2102:         out_buffer = conn.out_buffer
 2103:         out_buffer_len = len(out_buffer)
 2104:         file_upload.sentbytes += num_sent_bytes
 2105:         total_read_bytes = file_upload.offset + file_upload.sentbytes + out_buffer_len
 2106:         size = file_upload.size
 2107: 
 2108:         try:
 2109:             if total_read_bytes < size:
 2110:                 num_bytes_to_read = int(
 2111:                     (max(4096, num_sent_bytes * 1.25) / max(1, current_time - conn.last_active))
 2112:                     - out_buffer_len
 2113:                 )
 2114:                 if num_bytes_to_read > 0:
 2115:                     out_buffer += file_upload.file.read(num_bytes_to_read)
 2116:                     self._modify_connection_events(conn, selectors.EVENT_READ | selectors.EVENT_WRITE)
 2117: 
 2118:         except (OSError, ValueError) as error:
 2119:             events.emit_main_thread(
 2120:                 "upload-file-error",
 2121:                 username=conn.init.target_user, token=file_upload.token, error=error
 2122:             )
 2123:             return False  # Close the connection
 2124: 
 2125:         file_upload.speed += num_sent_bytes
 2126:         self._total_upload_bandwidth += num_sent_bytes
 2127: 
 2128:         # Upload finished
 2129:         if file_upload.offset + file_upload.sentbytes == size:
 2130:             events.emit_main_thread(
 2131:                 "file-upload-progress",
 2132:                 username=conn.init.target_user, token=file_upload.token,
 2133:                 offset=file_upload.offset, bytes_sent=file_upload.sentbytes
 2134:             )
 2135:         return True
```
