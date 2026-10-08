# rev0008 U-123 source trace: transfer session map and F-connection callbacks

## github-tag-3.3.10

### `pynicotine/transfers.py` `Transfers._activate_transfer` lines 527-546

Function SHA256: `93597ef81bccf25629e40a420f43f7f9b43c43fc9784e2fa59dc430c4470227b`

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
```

### `pynicotine/transfers.py` `Transfers._deactivate_transfer` lines 548-572

Function SHA256: `ed6c1cfcca4221e7660166416f8cc5a693ef07212978420f1d213b7147e19385`

```text
  548:     def _deactivate_transfer(self, transfer):
  549: 
  550:         username = transfer.username
  551:         token = transfer.token
  552: 
  553:         if token is None or token not in self.active_users.get(username, {}):
  554:             return False
  555: 
  556:         del self.active_users[username][token]
  557: 
  558:         if not self.active_users[username]:
  559:             del self.active_users[username]
  560: 
  561:         if transfer.speed > 0:
  562:             self.total_bandwidth = max(0, self.total_bandwidth - transfer.speed)
  563: 
  564:         if transfer.request_timer_id is not None:
  565:             events.cancel_scheduled(transfer.request_timer_id)
  566:             transfer.request_timer_id = None
  567: 
  568:         transfer.speed = transfer.avg_speed
  569:         transfer.sock = None
  570:         transfer.token = None
  571: 
  572:         return True
```

### `pynicotine/downloads.py` `Downloads._transfer_request_downloads` lines 1063-1129

Function SHA256: `a7f5f9dd52d21e6809e6292ba041a3c9b9e45b0d117a8cb0de795b0934bcc6ff`

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
 1098: 
 1099:         download = self.transfers.get(username + virtual_path)
 1100:         cancel_reason = TransferRejectReason.CANCELLED
 1101: 
 1102:         if download is not None:
 1103:             if download.status == TransferStatus.FINISHED:
 1104:                 # SoulseekQt sends "Complete" as the reason for rejecting the download if it exists
 1105:                 cancel_reason = TransferRejectReason.COMPLETE
 1106: 
 1107:         elif self.can_upload(username):
 1108:             # Check if download exists in our default download folder
 1109:             _file_path, file_exists = self.get_complete_download_file_path(username, virtual_path, size)
 1110: 
 1111:             if file_exists:
 1112:                 cancel_reason = TransferRejectReason.COMPLETE
 1113:             else:
 1114:                 # If this file is not in your download queue, then it must be
 1115:                 # a remotely initiated download and someone is manually uploading to you
 1116:                 parent_folder_path = virtual_path.replace("/", "\\").split("\\")[-2]
 1117:                 received_folder_path = os.path.normpath(os.path.expandvars(config.sections["transfers"]["uploaddir"]))
 1118:                 folder_path = os.path.join(received_folder_path, username, parent_folder_path)
 1119: 
 1120:                 transfer = Transfer(username, virtual_path, folder_path, size)
 1121: 
 1122:                 self._append_transfer(transfer)
 1123:                 self._activate_transfer(transfer, token)
 1124:                 self._update_transfer(transfer)
 1125: 
 1126:                 return TransferResponse(allowed=True, token=token)
 1127: 
 1128:         log.add_transfer("Denied file request: user %s, message %s", (username, msg))
 1129:         return TransferResponse(allowed=False, reason=cancel_reason, token=token)
```

### `pynicotine/downloads.py` `Downloads._transfer_request` lines 1048-1061

Function SHA256: `8043e2135504843ae821a551d2fbdf47fd75216911248825b8909bafe53d13ae`

```text
 1048:     def _transfer_request(self, msg):
 1049:         """Peer code 40."""
 1050: 
 1051:         if msg.direction != TransferDirection.UPLOAD:
 1052:             return
 1053: 
 1054:         username = msg.username
 1055:         response = self._transfer_request_downloads(msg)
 1056: 
 1057:         log.add_transfer("Responding to download request with token %s for file %s "
 1058:                          "from user: %s, allowed: %s, reason: %s",
 1059:                          (response.token, msg.file, username, response.allowed, response.reason))
 1060: 
 1061:         core.send_message_to_peer(username, response)
```

### `pynicotine/downloads.py` `Downloads._file_transfer_init` lines 1152-1243

Function SHA256: `c2298b4cfd721dcf6c889c98a161d59b6bdb5c37f29d626377bd409a6fcf8ac6`

```text
 1152:     def _file_transfer_init(self, msg):
 1153:         """A peer is requesting to start uploading a file to us."""
 1154: 
 1155:         if msg.is_outgoing:
 1156:             # Upload init message sent to ourselves, ignore
 1157:             return
 1158: 
 1159:         username = msg.username
 1160:         token = msg.token
 1161:         download = self.active_users.get(username, {}).get(token)
 1162: 
 1163:         if download is None or download.sock is not None:
 1164:             return
 1165: 
 1166:         virtual_path = download.virtual_path
 1167:         incomplete_folder_path = self.get_incomplete_download_folder()
 1168:         sock = download.sock = msg.sock
 1169:         need_update = True
 1170:         download_started = False
 1171: 
 1172:         log.add_transfer("Received file download init with token %s for file %s from user %s",
 1173:                          (token, virtual_path, username))
 1174: 
 1175:         try:
 1176:             incomplete_folder_path_encoded = encode_path(incomplete_folder_path)
 1177: 
 1178:             if not os.path.isdir(incomplete_folder_path_encoded):
 1179:                 os.makedirs(incomplete_folder_path_encoded)
 1180: 
 1181:             incomplete_file_path = self.get_incomplete_download_file_path(username, virtual_path)
 1182:             file_handle = open(encode_path(incomplete_file_path), "ab+")  # pylint: disable=consider-using-with
 1183: 
 1184:             try:
 1185:                 import fcntl
 1186:                 try:
 1187:                     fcntl.lockf(file_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
 1188:                 except OSError as error:
 1189:                     log.add(_("Can't get an exclusive lock on file - I/O error: %s"), error)
 1190:             except ImportError:
 1191:                 pass
 1192: 
 1193:             if download.size_changed:
 1194:                 # Remote user sent a different file size than we originally requested,
 1195:                 # wipe any existing data in the incomplete file to avoid corruption
 1196:                 file_handle.truncate(0)
 1197: 
 1198:             # Seek to the end of the file for resuming the download
 1199:             offset = file_handle.seek(0, os.SEEK_END)
 1200: 
 1201:         except OSError as error:
 1202:             log.add(_("Cannot save file in %(folder_path)s: %(error)s"), {
 1203:                 "folder_path": incomplete_folder_path,
 1204:                 "error": error
 1205:             })
 1206:             self._abort_transfer(download, status=TransferStatus.DOWNLOAD_FOLDER_ERROR)
 1207:             core.notifications.show_download_notification(
 1208:                 str(error), title=_("Download Folder Error"), high_priority=True)
 1209:             need_update = False
 1210: 
 1211:         else:
 1212:             download.file_handle = file_handle
 1213:             download.last_byte_offset = offset
 1214:             download.start_time = time.monotonic() - download.time_elapsed
 1215:             download.retry_attempt = False
 1216: 
 1217:             core.statistics.append_stat_value("started_downloads", 1)
 1218:             download_started = True
 1219: 
 1220:             log.add_download(
 1221:                 _("Download started: user %(user)s, file %(file)s"), {
 1222:                     "user": username,
 1223:                     "file": file_handle.name.decode("utf-8", "replace")
 1224:                 }
 1225:             )
 1226: 
 1227:             if download.size > offset:
 1228:                 download.status = TransferStatus.TRANSFERRING
 1229:                 core.send_message_to_network_thread(DownloadFile(
 1230:                     sock=sock, token=token, file=file_handle, leftbytes=(download.size - offset)
 1231:                 ))
 1232:                 core.send_message_to_peer(username, FileOffset(sock, offset))
 1233: 
 1234:             else:
 1235:                 self._finish_transfer(download)
 1236:                 need_update = False
 1237: 
 1238:         if need_update:
 1239:             self._update_transfer(download)
 1240: 
 1241:         if download_started:
 1242:             # Must be emitted after the final update to prevent inconsistent state
 1243:             core.pluginhandler.download_started_notification(username, virtual_path, incomplete_file_path)
```

### `pynicotine/downloads.py` `Downloads._file_download_progress` lines 1329-1345

Function SHA256: `3b44315751ca3698fb19db78754e4c5c6a8e3a5e8a6b0a99a4e1f270b1f142fa`

```text
 1329:     def _file_download_progress(self, username, token, bytes_left, speed=None):
 1330:         """A file download is in progress."""
 1331: 
 1332:         download = self.active_users.get(username, {}).get(token)
 1333: 
 1334:         if download is None:
 1335:             return
 1336: 
 1337:         if download.request_timer_id is not None:
 1338:             events.cancel_scheduled(download.request_timer_id)
 1339:             download.request_timer_id = None
 1340: 
 1341:         self._update_transfer_progress(
 1342:             download, stat_id="downloaded_size",
 1343:             current_byte_offset=(download.size - bytes_left), speed=speed
 1344:         )
 1345:         self._update_transfer(download)
```

### `pynicotine/downloads.py` `Downloads._file_connection_closed` lines 1347-1367

Function SHA256: `973956bf54b301faf77223d1384dabffc82b3b2234cdf2dd57d70a0f2d784e99`

```text
 1347:     def _file_connection_closed(self, username, token, sock, **_unused):
 1348:         """A file download connection has closed for any reason."""
 1349: 
 1350:         download = self.active_users.get(username, {}).get(token)
 1351: 
 1352:         if download is None:
 1353:             return
 1354: 
 1355:         if download.sock != sock:
 1356:             return
 1357: 
 1358:         if download.current_byte_offset is not None and download.current_byte_offset >= download.size:
 1359:             self._finish_transfer(download)
 1360:             return
 1361: 
 1362:         if core.users.statuses.get(download.username) == UserStatus.OFFLINE:
 1363:             status = TransferStatus.USER_LOGGED_OFF
 1364:         else:
 1365:             status = TransferStatus.CANCELLED
 1366: 
 1367:         self._abort_transfer(download, status=status)
```

### `pynicotine/downloads.py` `Downloads._transfer_timeout` lines 1131-1139

Function SHA256: `84e2944b533378f61608147430b0895ed55cad5b79c3ea348f84212eb46513f9`

```text
 1131:     def _transfer_timeout(self, transfer):
 1132: 
 1133:         if transfer.request_timer_id is None:
 1134:             return
 1135: 
 1136:         log.add_transfer("Download %s with token %s for user %s timed out",
 1137:                          (transfer.virtual_path, transfer.token, transfer.username))
 1138: 
 1139:         super()._transfer_timeout(transfer)
```

## github-branch-3.3.x

### `pynicotine/transfers.py` `Transfers._activate_transfer` lines 530-549

Function SHA256: `93597ef81bccf25629e40a420f43f7f9b43c43fc9784e2fa59dc430c4470227b`

```text
  530:     def _activate_transfer(self, transfer, token):
  531: 
  532:         core.users.watch_user(transfer.username, context=self._name)
  533: 
  534:         transfer.status = TransferStatus.GETTING_STATUS
  535:         transfer.token = token
  536:         transfer.speed = transfer.avg_speed = 0
  537:         transfer.queue_position = 0
  538: 
  539:         # When our port is closed, certain clients can take up to ~30 seconds before they
  540:         # initiate a 'F' connection, since they only send an indirect connection request after
  541:         # attempting to connect to our port for a certain time period.
  542:         # Known clients: Nicotine+ 2.2.0 - 3.2.0, 2 s; Soulseek NS, ~20 s; soulseeX, ~30 s.
  543:         # To account for potential delays while initializing the connection, add 15 seconds
  544:         # to the timeout value.
  545: 
  546:         transfer.request_timer_id = events.schedule(
  547:             delay=45, callback=self._transfer_timeout, callback_args=(transfer,))
  548: 
  549:         self.active_users[transfer.username][token] = transfer
```

### `pynicotine/transfers.py` `Transfers._deactivate_transfer` lines 551-575

Function SHA256: `ed6c1cfcca4221e7660166416f8cc5a693ef07212978420f1d213b7147e19385`

```text
  551:     def _deactivate_transfer(self, transfer):
  552: 
  553:         username = transfer.username
  554:         token = transfer.token
  555: 
  556:         if token is None or token not in self.active_users.get(username, {}):
  557:             return False
  558: 
  559:         del self.active_users[username][token]
  560: 
  561:         if not self.active_users[username]:
  562:             del self.active_users[username]
  563: 
  564:         if transfer.speed > 0:
  565:             self.total_bandwidth = max(0, self.total_bandwidth - transfer.speed)
  566: 
  567:         if transfer.request_timer_id is not None:
  568:             events.cancel_scheduled(transfer.request_timer_id)
  569:             transfer.request_timer_id = None
  570: 
  571:         transfer.speed = transfer.avg_speed
  572:         transfer.sock = None
  573:         transfer.token = None
  574: 
  575:         return True
```

### `pynicotine/downloads.py` `Downloads._transfer_request_downloads` lines 1074-1140

Function SHA256: `a7f5f9dd52d21e6809e6292ba041a3c9b9e45b0d117a8cb0de795b0934bcc6ff`

```text
 1074:     def _transfer_request_downloads(self, msg):
 1075: 
 1076:         username = msg.username
 1077:         virtual_path = msg.file
 1078:         size = msg.filesize
 1079:         token = msg.token
 1080: 
 1081:         log.add_transfer("Received download request with token %s for file %s from user %s",
 1082:                          (token, virtual_path, username))
 1083: 
 1084:         download = (self.queued_users.get(username, {}).get(virtual_path)
 1085:                     or self.failed_users.get(username, {}).get(virtual_path))
 1086: 
 1087:         if download is not None:
 1088:             # Remote peer is signaling a transfer is ready, attempting to download it
 1089: 
 1090:             # If the file is larger than 2GB, the SoulseekQt client seems to
 1091:             # send a malformed file size (0 bytes) in the TransferRequest response.
 1092:             # In that case, we rely on the cached, correct file size we received when
 1093:             # we initially added the download.
 1094: 
 1095:             self._unfail_transfer(download)
 1096:             self._dequeue_transfer(download)
 1097: 
 1098:             if size > 0:
 1099:                 if download.size != size:
 1100:                     # The remote user's file contents have changed since we queued the download
 1101:                     download.size_changed = True
 1102: 
 1103:                 download.size = size
 1104: 
 1105:             self._activate_transfer(download, token)
 1106:             self._update_transfer(download)
 1107: 
 1108:             return TransferResponse(allowed=True, token=token)
 1109: 
 1110:         download = self.transfers.get(username + virtual_path)
 1111:         cancel_reason = TransferRejectReason.CANCELLED
 1112: 
 1113:         if download is not None:
 1114:             if download.status == TransferStatus.FINISHED:
 1115:                 # SoulseekQt sends "Complete" as the reason for rejecting the download if it exists
 1116:                 cancel_reason = TransferRejectReason.COMPLETE
 1117: 
 1118:         elif self.can_upload(username):
 1119:             # Check if download exists in our default download folder
 1120:             _file_path, file_exists = self.get_complete_download_file_path(username, virtual_path, size)
 1121: 
 1122:             if file_exists:
 1123:                 cancel_reason = TransferRejectReason.COMPLETE
 1124:             else:
 1125:                 # If this file is not in your download queue, then it must be
 1126:                 # a remotely initiated download and someone is manually uploading to you
 1127:                 parent_folder_path = virtual_path.replace("/", "\\").split("\\")[-2]
 1128:                 received_folder_path = os.path.normpath(os.path.expandvars(config.sections["transfers"]["uploaddir"]))
 1129:                 folder_path = os.path.join(received_folder_path, username, parent_folder_path)
 1130: 
 1131:                 transfer = Transfer(username, virtual_path, folder_path, size)
 1132: 
 1133:                 self._append_transfer(transfer)
 1134:                 self._activate_transfer(transfer, token)
 1135:                 self._update_transfer(transfer)
 1136: 
 1137:                 return TransferResponse(allowed=True, token=token)
 1138: 
 1139:         log.add_transfer("Denied file request: user %s, message %s", (username, msg))
 1140:         return TransferResponse(allowed=False, reason=cancel_reason, token=token)
```

### `pynicotine/downloads.py` `Downloads._transfer_request` lines 1059-1072

Function SHA256: `8043e2135504843ae821a551d2fbdf47fd75216911248825b8909bafe53d13ae`

```text
 1059:     def _transfer_request(self, msg):
 1060:         """Peer code 40."""
 1061: 
 1062:         if msg.direction != TransferDirection.UPLOAD:
 1063:             return
 1064: 
 1065:         username = msg.username
 1066:         response = self._transfer_request_downloads(msg)
 1067: 
 1068:         log.add_transfer("Responding to download request with token %s for file %s "
 1069:                          "from user: %s, allowed: %s, reason: %s",
 1070:                          (response.token, msg.file, username, response.allowed, response.reason))
 1071: 
 1072:         core.send_message_to_peer(username, response)
```

### `pynicotine/downloads.py` `Downloads._file_transfer_init` lines 1163-1257

Function SHA256: `6d2fb0de913b433418ce6536cfffa33d7f6b986ebcddabf841a3f1e77d3b5f57`

```text
 1163:     def _file_transfer_init(self, msg):
 1164:         """A peer is requesting to start uploading a file to us."""
 1165: 
 1166:         if msg.is_outgoing:
 1167:             # Transfer init message sent to another peer, ignore
 1168:             return
 1169: 
 1170:         username = msg.username
 1171:         token = msg.token
 1172:         download = self.active_users.get(username, {}).get(token)
 1173: 
 1174:         if download is None or download.sock is not None:
 1175:             log.add_transfer("Received file transfer init message with unknown token %s, closing connection", token)
 1176:             core.send_message_to_network_thread(CloseConnection(msg.sock))
 1177:             return
 1178: 
 1179:         virtual_path = download.virtual_path
 1180:         incomplete_folder_path = self.get_incomplete_download_folder()
 1181:         sock = download.sock = msg.sock
 1182:         need_update = True
 1183:         download_started = False
 1184: 
 1185:         log.add_transfer("Received file download init with token %s for file %s from user %s",
 1186:                          (token, virtual_path, username))
 1187: 
 1188:         try:
 1189:             incomplete_folder_path_encoded = encode_path(incomplete_folder_path)
 1190: 
 1191:             if not os.path.isdir(incomplete_folder_path_encoded):
 1192:                 os.makedirs(incomplete_folder_path_encoded)
 1193: 
 1194:             incomplete_file_path = self.get_incomplete_download_file_path(username, virtual_path)
 1195:             file_handle = open(encode_path(incomplete_file_path), "ab+")  # pylint: disable=consider-using-with
 1196: 
 1197:             try:
 1198:                 import fcntl
 1199:                 try:
 1200:                     fcntl.lockf(file_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
 1201:                 except OSError as error:
 1202:                     log.add(_("Can't get an exclusive lock on file - I/O error: %s"), error)
 1203:             except ImportError:
 1204:                 pass
 1205: 
 1206:             if download.size_changed:
 1207:                 # Remote user sent a different file size than we originally requested,
 1208:                 # wipe any existing data in the incomplete file to avoid corruption
 1209:                 file_handle.truncate(0)
 1210: 
 1211:             # Seek to the end of the file for resuming the download
 1212:             offset = file_handle.seek(0, os.SEEK_END)
 1213: 
 1214:         except OSError as error:
 1215:             log.add(_("Cannot save file in %(folder_path)s: %(error)s"), {
 1216:                 "folder_path": incomplete_folder_path,
 1217:                 "error": error
 1218:             })
 1219:             self._abort_transfer(download, status=TransferStatus.DOWNLOAD_FOLDER_ERROR)
 1220:             core.notifications.show_download_notification(
 1221:                 str(error), title=_("Download Folder Error"), high_priority=True)
 1222:             need_update = False
 1223: 
 1224:         else:
 1225:             download.file_handle = file_handle
 1226:             download.last_byte_offset = offset
 1227:             download.start_time = time.monotonic() - download.time_elapsed
 1228:             download.retry_attempt = False
 1229: 
 1230:             core.statistics.append_stat_value("started_downloads", 1)
 1231:             download_started = True
 1232: 
 1233:             log.add_download(
 1234:                 _("Download started: user %(user)s, file %(file)s"), {
 1235:                     "user": username,
 1236:                     "file": file_handle.name.decode("utf-8", "replace")
 1237:                 }
 1238:             )
 1239: 
 1240:             if download.size > offset:
 1241:                 download.status = TransferStatus.TRANSFERRING
 1242:                 core.send_message_to_network_thread(DownloadFile(
 1243:                     sock=sock, token=token, file=file_handle, leftbytes=(download.size - offset)
 1244:                 ))
 1245:                 core.send_message_to_peer(username, FileOffset(sock, offset))
 1246: 
 1247:             else:
 1248:                 core.send_message_to_network_thread(CloseConnection(sock))
 1249:                 self._finish_transfer(download)
 1250:                 need_update = False
 1251: 
 1252:         if need_update:
 1253:             self._update_transfer(download)
 1254: 
 1255:         if download_started:
 1256:             # Must be emitted after the final update to prevent inconsistent state
 1257:             core.pluginhandler.download_started_notification(username, virtual_path, incomplete_file_path)
```

### `pynicotine/downloads.py` `Downloads._file_download_progress` lines 1343-1359

Function SHA256: `3b44315751ca3698fb19db78754e4c5c6a8e3a5e8a6b0a99a4e1f270b1f142fa`

```text
 1343:     def _file_download_progress(self, username, token, bytes_left, speed=None):
 1344:         """A file download is in progress."""
 1345: 
 1346:         download = self.active_users.get(username, {}).get(token)
 1347: 
 1348:         if download is None:
 1349:             return
 1350: 
 1351:         if download.request_timer_id is not None:
 1352:             events.cancel_scheduled(download.request_timer_id)
 1353:             download.request_timer_id = None
 1354: 
 1355:         self._update_transfer_progress(
 1356:             download, stat_id="downloaded_size",
 1357:             current_byte_offset=(download.size - bytes_left), speed=speed
 1358:         )
 1359:         self._update_transfer(download)
```

### `pynicotine/downloads.py` `Downloads._file_connection_closed` lines 1361-1381

Function SHA256: `973956bf54b301faf77223d1384dabffc82b3b2234cdf2dd57d70a0f2d784e99`

```text
 1361:     def _file_connection_closed(self, username, token, sock, **_unused):
 1362:         """A file download connection has closed for any reason."""
 1363: 
 1364:         download = self.active_users.get(username, {}).get(token)
 1365: 
 1366:         if download is None:
 1367:             return
 1368: 
 1369:         if download.sock != sock:
 1370:             return
 1371: 
 1372:         if download.current_byte_offset is not None and download.current_byte_offset >= download.size:
 1373:             self._finish_transfer(download)
 1374:             return
 1375: 
 1376:         if core.users.statuses.get(download.username) == UserStatus.OFFLINE:
 1377:             status = TransferStatus.USER_LOGGED_OFF
 1378:         else:
 1379:             status = TransferStatus.CANCELLED
 1380: 
 1381:         self._abort_transfer(download, status=status)
```

### `pynicotine/downloads.py` `Downloads._transfer_timeout` lines 1142-1150

Function SHA256: `84e2944b533378f61608147430b0895ed55cad5b79c3ea348f84212eb46513f9`

```text
 1142:     def _transfer_timeout(self, transfer):
 1143: 
 1144:         if transfer.request_timer_id is None:
 1145:             return
 1146: 
 1147:         log.add_transfer("Download %s with token %s for user %s timed out",
 1148:                          (transfer.virtual_path, transfer.token, transfer.username))
 1149: 
 1150:         super()._transfer_timeout(transfer)
```

## github-branch-master

### `pynicotine/transfers.py` `Transfers._activate_transfer` lines 528-547

Function SHA256: `93597ef81bccf25629e40a420f43f7f9b43c43fc9784e2fa59dc430c4470227b`

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

### `pynicotine/transfers.py` `Transfers._deactivate_transfer` lines 549-573

Function SHA256: `ed6c1cfcca4221e7660166416f8cc5a693ef07212978420f1d213b7147e19385`

```text
  549:     def _deactivate_transfer(self, transfer):
  550: 
  551:         username = transfer.username
  552:         token = transfer.token
  553: 
  554:         if token is None or token not in self.active_users.get(username, {}):
  555:             return False
  556: 
  557:         del self.active_users[username][token]
  558: 
  559:         if not self.active_users[username]:
  560:             del self.active_users[username]
  561: 
  562:         if transfer.speed > 0:
  563:             self.total_bandwidth = max(0, self.total_bandwidth - transfer.speed)
  564: 
  565:         if transfer.request_timer_id is not None:
  566:             events.cancel_scheduled(transfer.request_timer_id)
  567:             transfer.request_timer_id = None
  568: 
  569:         transfer.speed = transfer.avg_speed
  570:         transfer.sock = None
  571:         transfer.token = None
  572: 
  573:         return True
```

### `pynicotine/downloads.py` `Downloads._transfer_request_downloads` lines 1045-1111

Function SHA256: `f8830fe17196bff5afb00048018f8a171530ea0a3da42aaf572d613e24abf72f`

```text
 1045:     def _transfer_request_downloads(self, msg):
 1046: 
 1047:         username = msg.username
 1048:         virtual_path = msg.file
 1049:         size = msg.filesize
 1050:         token = msg.token
 1051: 
 1052:         log.add_transfer("Received download request with token %s for file %s from user %s",
 1053:                          (token, virtual_path, username))
 1054: 
 1055:         download = (self.queued_users.get(username, {}).get(virtual_path)
 1056:                     or self.failed_users.get(username, {}).get(virtual_path))
 1057: 
 1058:         if download is not None:
 1059:             # Remote peer is signaling a transfer is ready, attempting to download it
 1060: 
 1061:             # If the file is larger than 2GB, the SoulseekQt client seems to
 1062:             # send a malformed file size (0 bytes) in the TransferRequest response.
 1063:             # In that case, we rely on the cached, correct file size we received when
 1064:             # we initially added the download.
 1065: 
 1066:             self._unfail_transfer(download)
 1067:             self._dequeue_transfer(download)
 1068: 
 1069:             if size > 0:
 1070:                 if download.size != size:
 1071:                     # The remote user's file contents have changed since we queued the download
 1072:                     download.size_changed = True
 1073: 
 1074:                 download.size = size
 1075: 
 1076:             self._activate_transfer(download, token)
 1077:             self._update_transfer(download)
 1078: 
 1079:             return TransferResponse(allowed=True, token=token)
 1080: 
 1081:         download = self.transfers.get(username + virtual_path)
 1082:         cancel_reason = TransferRejectReason.CANCELLED
 1083: 
 1084:         if download is not None:
 1085:             if download.status == TransferStatus.FINISHED:
 1086:                 # SoulseekQt sends "Complete" as the reason for rejecting the download if it exists
 1087:                 cancel_reason = TransferRejectReason.COMPLETE
 1088: 
 1089:         elif self.can_send_any_files(username):
 1090:             # Check if download exists in our default download folder
 1091:             _file_path, file_exists = self.get_complete_download_file_path(username, virtual_path, size)
 1092: 
 1093:             if file_exists:
 1094:                 cancel_reason = TransferRejectReason.COMPLETE
 1095:             else:
 1096:                 # If this file is not in your download queue, then it must be
 1097:                 # a remotely initiated download and someone is manually uploading to you
 1098:                 parent_folder_path = virtual_path.replace("/", "\\").split("\\")[-2]
 1099:                 received_folder_path = os.path.normpath(os.path.expandvars(config.sections["transfers"]["uploaddir"]))
 1100:                 folder_path = os.path.join(received_folder_path, username, parent_folder_path)
 1101: 
 1102:                 transfer = Transfer(username, virtual_path, folder_path, size)
 1103: 
 1104:                 self._append_transfer(transfer)
 1105:                 self._activate_transfer(transfer, token)
 1106:                 self._update_transfer(transfer)
 1107: 
 1108:                 return TransferResponse(allowed=True, token=token)
 1109: 
 1110:         log.add_transfer("Denied file request: user %s, message %s", (username, msg))
 1111:         return TransferResponse(allowed=False, reason=cancel_reason, token=token)
```

### `pynicotine/downloads.py` `Downloads._transfer_request` lines 1030-1043

Function SHA256: `8043e2135504843ae821a551d2fbdf47fd75216911248825b8909bafe53d13ae`

```text
 1030:     def _transfer_request(self, msg):
 1031:         """Peer code 40."""
 1032: 
 1033:         if msg.direction != TransferDirection.UPLOAD:
 1034:             return
 1035: 
 1036:         username = msg.username
 1037:         response = self._transfer_request_downloads(msg)
 1038: 
 1039:         log.add_transfer("Responding to download request with token %s for file %s "
 1040:                          "from user: %s, allowed: %s, reason: %s",
 1041:                          (response.token, msg.file, username, response.allowed, response.reason))
 1042: 
 1043:         core.send_message_to_peer(username, response)
```

### `pynicotine/downloads.py` `Downloads._file_transfer_init` lines 1134-1228

Function SHA256: `6d2fb0de913b433418ce6536cfffa33d7f6b986ebcddabf841a3f1e77d3b5f57`

```text
 1134:     def _file_transfer_init(self, msg):
 1135:         """A peer is requesting to start uploading a file to us."""
 1136: 
 1137:         if msg.is_outgoing:
 1138:             # Transfer init message sent to another peer, ignore
 1139:             return
 1140: 
 1141:         username = msg.username
 1142:         token = msg.token
 1143:         download = self.active_users.get(username, {}).get(token)
 1144: 
 1145:         if download is None or download.sock is not None:
 1146:             log.add_transfer("Received file transfer init message with unknown token %s, closing connection", token)
 1147:             core.send_message_to_network_thread(CloseConnection(msg.sock))
 1148:             return
 1149: 
 1150:         virtual_path = download.virtual_path
 1151:         incomplete_folder_path = self.get_incomplete_download_folder()
 1152:         sock = download.sock = msg.sock
 1153:         need_update = True
 1154:         download_started = False
 1155: 
 1156:         log.add_transfer("Received file download init with token %s for file %s from user %s",
 1157:                          (token, virtual_path, username))
 1158: 
 1159:         try:
 1160:             incomplete_folder_path_encoded = encode_path(incomplete_folder_path)
 1161: 
 1162:             if not os.path.isdir(incomplete_folder_path_encoded):
 1163:                 os.makedirs(incomplete_folder_path_encoded)
 1164: 
 1165:             incomplete_file_path = self.get_incomplete_download_file_path(username, virtual_path)
 1166:             file_handle = open(encode_path(incomplete_file_path), "ab+")  # pylint: disable=consider-using-with
 1167: 
 1168:             try:
 1169:                 import fcntl
 1170:                 try:
 1171:                     fcntl.lockf(file_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
 1172:                 except OSError as error:
 1173:                     log.add(_("Can't get an exclusive lock on file - I/O error: %s"), error)
 1174:             except ImportError:
 1175:                 pass
 1176: 
 1177:             if download.size_changed:
 1178:                 # Remote user sent a different file size than we originally requested,
 1179:                 # wipe any existing data in the incomplete file to avoid corruption
 1180:                 file_handle.truncate(0)
 1181: 
 1182:             # Seek to the end of the file for resuming the download
 1183:             offset = file_handle.seek(0, os.SEEK_END)
 1184: 
 1185:         except OSError as error:
 1186:             log.add(_("Cannot save file in %(folder_path)s: %(error)s"), {
 1187:                 "folder_path": incomplete_folder_path,
 1188:                 "error": error
 1189:             })
 1190:             self._abort_transfer(download, status=TransferStatus.DOWNLOAD_FOLDER_ERROR)
 1191:             core.notifications.show_download_notification(
 1192:                 str(error), title=_("Download Folder Error"), high_priority=True)
 1193:             need_update = False
 1194: 
 1195:         else:
 1196:             download.file_handle = file_handle
 1197:             download.last_byte_offset = offset
 1198:             download.start_time = time.monotonic() - download.time_elapsed
 1199:             download.retry_attempt = False
 1200: 
 1201:             core.statistics.append_stat_value("started_downloads", 1)
 1202:             download_started = True
 1203: 
 1204:             log.add_download(
 1205:                 _("Download started: user %(user)s, file %(file)s"), {
 1206:                     "user": username,
 1207:                     "file": file_handle.name.decode("utf-8", "replace")
 1208:                 }
 1209:             )
 1210: 
 1211:             if download.size > offset:
 1212:                 download.status = TransferStatus.TRANSFERRING
 1213:                 core.send_message_to_network_thread(DownloadFile(
 1214:                     sock=sock, token=token, file=file_handle, leftbytes=(download.size - offset)
 1215:                 ))
 1216:                 core.send_message_to_peer(username, FileOffset(sock, offset))
 1217: 
 1218:             else:
 1219:                 core.send_message_to_network_thread(CloseConnection(sock))
 1220:                 self._finish_transfer(download)
 1221:                 need_update = False
 1222: 
 1223:         if need_update:
 1224:             self._update_transfer(download)
 1225: 
 1226:         if download_started:
 1227:             # Must be emitted after the final update to prevent inconsistent state
 1228:             core.pluginhandler.download_started_notification(username, virtual_path, incomplete_file_path)
```

### `pynicotine/downloads.py` `Downloads._file_download_progress` lines 1314-1330

Function SHA256: `3b44315751ca3698fb19db78754e4c5c6a8e3a5e8a6b0a99a4e1f270b1f142fa`

```text
 1314:     def _file_download_progress(self, username, token, bytes_left, speed=None):
 1315:         """A file download is in progress."""
 1316: 
 1317:         download = self.active_users.get(username, {}).get(token)
 1318: 
 1319:         if download is None:
 1320:             return
 1321: 
 1322:         if download.request_timer_id is not None:
 1323:             events.cancel_scheduled(download.request_timer_id)
 1324:             download.request_timer_id = None
 1325: 
 1326:         self._update_transfer_progress(
 1327:             download, stat_id="downloaded_size",
 1328:             current_byte_offset=(download.size - bytes_left), speed=speed
 1329:         )
 1330:         self._update_transfer(download)
```

### `pynicotine/downloads.py` `Downloads._file_connection_closed` lines 1332-1352

Function SHA256: `973956bf54b301faf77223d1384dabffc82b3b2234cdf2dd57d70a0f2d784e99`

```text
 1332:     def _file_connection_closed(self, username, token, sock, **_unused):
 1333:         """A file download connection has closed for any reason."""
 1334: 
 1335:         download = self.active_users.get(username, {}).get(token)
 1336: 
 1337:         if download is None:
 1338:             return
 1339: 
 1340:         if download.sock != sock:
 1341:             return
 1342: 
 1343:         if download.current_byte_offset is not None and download.current_byte_offset >= download.size:
 1344:             self._finish_transfer(download)
 1345:             return
 1346: 
 1347:         if core.users.statuses.get(download.username) == UserStatus.OFFLINE:
 1348:             status = TransferStatus.USER_LOGGED_OFF
 1349:         else:
 1350:             status = TransferStatus.CANCELLED
 1351: 
 1352:         self._abort_transfer(download, status=status)
```

### `pynicotine/downloads.py` `Downloads._transfer_timeout` lines 1113-1121

Function SHA256: `84e2944b533378f61608147430b0895ed55cad5b79c3ea348f84212eb46513f9`

```text
 1113:     def _transfer_timeout(self, transfer):
 1114: 
 1115:         if transfer.request_timer_id is None:
 1116:             return
 1117: 
 1118:         log.add_transfer("Download %s with token %s for user %s timed out",
 1119:                          (transfer.virtual_path, transfer.token, transfer.username))
 1120: 
 1121:         super()._transfer_timeout(transfer)
```
