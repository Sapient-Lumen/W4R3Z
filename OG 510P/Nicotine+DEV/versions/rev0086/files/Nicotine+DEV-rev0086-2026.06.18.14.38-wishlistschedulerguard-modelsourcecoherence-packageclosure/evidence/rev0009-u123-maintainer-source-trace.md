# rev0009 U-123 maintainer package source trace

Source lanes were read from the external rev0003 source bundle. This trace records the small source-shape dependencies used by the maintainer reproducer.

## github-tag-3.3.10

### transfers.py activation/deactivation

```python
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
  573: 
```

### downloads.py token-bearing request/init/progress/close paths

```python
 1030:                     self._folder_contents_response, (msg, check_num_files)
 1031:                 )
 1032:                 return
 1033: 
 1034:             destination_folder_path = self.get_folder_destination(username, folder_path)
 1035: 
 1036:             log.add_transfer("Attempting to download files in folder %s for user %s. "
 1037:                              "Destination path: %s", (folder_path, username, destination_folder_path))
 1038: 
 1039:             for _code, basename, file_size, _ext, file_attributes, *_unused in files:
 1040:                 virtual_path = folder_path.rstrip("\\") + "\\" + basename
 1041: 
 1042:                 self.enqueue_download(
 1043:                     username, virtual_path, folder_path=destination_folder_path, size=file_size,
 1044:                     file_attributes=file_attributes)
 1045: 
 1046:         del self._requested_folders[username][folder_path]
 1047: 
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
 1062: 
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
```

```python
 1134:             return
 1135: 
 1136:         log.add_transfer("Download %s with token %s for user %s timed out",
 1137:                          (transfer.virtual_path, transfer.token, transfer.username))
 1138: 
 1139:         super()._transfer_timeout(transfer)
 1140: 
 1141:     def _download_file_error(self, username, token, error):
 1142:         """Networking thread encountered a local file error for download."""
 1143: 
 1144:         download = self.active_users.get(username, {}).get(token)
 1145: 
 1146:         if download is None:
 1147:             return
 1148: 
 1149:         self._abort_transfer(download, status=TransferStatus.LOCAL_FILE_ERROR)
 1150:         log.add(_("Download I/O error: %s"), error)
 1151: 
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
```

```python
 1314: 
 1315:             download.legacy_attempt = download.retry_attempt = True
 1316: 
 1317:             if self._enqueue_transfer(download):
 1318:                 self._update_transfer(download)
 1319: 
 1320:             return
 1321: 
 1322:         # Already failed once previously, give up
 1323:         self._abort_transfer(download, status=TransferStatus.CONNECTION_CLOSED)
 1324:         download.retry_attempt = False
 1325: 
 1326:         log.add_transfer("Upload attempt by user %s for file %s failed. Reason: %s",
 1327:                          (virtual_path, username, download.status))
 1328: 
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
 1346: 
 1347:     def _file_connection_closed(self, username, token, sock, **_unused):
 1348:         """A file download connection has closed for any reason."""
 1349: 
 1350:         download = self.active_users.get(username, {}).get(token)
 1351: 
 1352:         if download is None:
 1353:             return
 1354: 
 1355:         if download.sock != sock:
```

## github-branch-3.3.x

### transfers.py activation/deactivation

```python
  528:         return True
  529: 
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
  550: 
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
```

### downloads.py token-bearing request/init/progress/close paths

```python
 1030: 
 1031:         for i_folder_path, files in msg.list.items():
 1032:             if i_folder_path != folder_path:
 1033:                 continue
 1034: 
 1035:             num_files = len(files)
 1036: 
 1037:             if check_num_files and num_files > 100:
 1038:                 check_num_files = False
 1039:                 events.emit(
 1040:                     "download-large-folder", username, folder_path, num_files,
 1041:                     self._folder_contents_response, (msg, check_num_files)
 1042:                 )
 1043:                 return
 1044: 
 1045:             destination_folder_path = self.get_folder_destination(username, folder_path)
 1046: 
 1047:             log.add_transfer("Attempting to download files in folder %s for user %s. "
 1048:                              "Destination path: %s", (folder_path, username, destination_folder_path))
 1049: 
 1050:             for _code, basename, file_size, _ext, file_attributes, *_unused in files:
 1051:                 virtual_path = folder_path.rstrip("\\") + "\\" + basename
 1052: 
 1053:                 self.enqueue_download(
 1054:                     username, virtual_path, folder_path=destination_folder_path, size=file_size,
 1055:                     file_attributes=file_attributes)
 1056: 
 1057:         del self._requested_folders[username][folder_path]
 1058: 
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
 1073: 
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
```

```python
 1134:                 self._activate_transfer(transfer, token)
 1135:                 self._update_transfer(transfer)
 1136: 
 1137:                 return TransferResponse(allowed=True, token=token)
 1138: 
 1139:         log.add_transfer("Denied file request: user %s, message %s", (username, msg))
 1140:         return TransferResponse(allowed=False, reason=cancel_reason, token=token)
 1141: 
 1142:     def _transfer_timeout(self, transfer):
 1143: 
 1144:         if transfer.request_timer_id is None:
 1145:             return
 1146: 
 1147:         log.add_transfer("Download %s with token %s for user %s timed out",
 1148:                          (transfer.virtual_path, transfer.token, transfer.username))
 1149: 
 1150:         super()._transfer_timeout(transfer)
 1151: 
 1152:     def _download_file_error(self, username, token, error):
 1153:         """Networking thread encountered a local file error for download."""
 1154: 
 1155:         download = self.active_users.get(username, {}).get(token)
 1156: 
 1157:         if download is None:
 1158:             return
 1159: 
 1160:         self._abort_transfer(download, status=TransferStatus.LOCAL_FILE_ERROR)
 1161:         log.add(_("Download I/O error: %s"), error)
 1162: 
 1163:     def _file_transfer_init(self, msg):
 1164:         """A peer is requesting to start uploading a file to us."""
 1165: 
```

```python
 1314:                 and virtual_path not in self.queued_users.get(username, {})):
 1315:             return
 1316: 
 1317:         if download.status in {TransferStatus.DOWNLOAD_FOLDER_ERROR, TransferStatus.LOCAL_FILE_ERROR}:
 1318:             # Local error, no need to retry
 1319:             return
 1320: 
 1321:         if not download.retry_attempt:
 1322:             # Attempt to request file name encoded as latin-1 once
 1323: 
 1324:             # We mark download as failed when aborting it, to avoid a redundant request
 1325:             # to unwatch the user. Need to call _unfail_transfer() to undo this.
 1326:             self._abort_transfer(download, status=TransferStatus.CONNECTION_CLOSED)
 1327:             self._unfail_transfer(download)
 1328: 
 1329:             download.legacy_attempt = download.retry_attempt = True
 1330: 
 1331:             if self._enqueue_transfer(download):
 1332:                 self._update_transfer(download)
 1333: 
 1334:             return
 1335: 
 1336:         # Already failed once previously, give up
 1337:         self._abort_transfer(download, status=TransferStatus.CONNECTION_CLOSED)
 1338:         download.retry_attempt = False
 1339: 
 1340:         log.add_transfer("Upload attempt by user %s for file %s failed. Reason: %s",
 1341:                          (virtual_path, username, download.status))
 1342: 
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
```

## github-branch-master

### transfers.py activation/deactivation

```python
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
  548: 
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

### downloads.py token-bearing request/init/progress/close paths

```python
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
 1044: 
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
```

```python
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
```

```python
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
 1331: 
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
 1353: 
 1354:     def _place_in_queue_response(self, msg):
 1355:         """Peer code 44.
```
