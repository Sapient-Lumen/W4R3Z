# rev0007 U-123 source trace — handler/timer path

This evidence file records only compact excerpts from the external rev0003 source lanes. The source bundle itself remains external and is not embedded in this cube.

The relevant state machine is:

1. `TransferRequest` carries a peer-supplied `token`, `file`, and `filesize`.
2. `Downloads._transfer_request_downloads()` looks up the queued download by `username + virtual_path`, then calls `_activate_transfer(download, token)` using the peer-supplied token.
3. `Transfers._activate_transfer()` writes `active_users[username][token] = transfer` without a same-key collision check.
4. `Transfers._deactivate_transfer()` deletes `active_users[username][token]` without checking that the mapped object is the transfer being deactivated.
5. Therefore a stale timeout/cancel path from the overwritten transfer can delete the replacement transfer's active-map entry.

## github-tag-3.3.10
### downloads.py:1063-1097 — downloads_transfer_request

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
### downloads.py:1152-1164 — downloads_file_init

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
```
### downloads.py:1288-1302 — downloads_upload_failed

```text
 1288:     def _upload_failed(self, msg):
 1289:         """Peer code 46."""
 1290: 
 1291:         username = msg.username
 1292:         virtual_path = msg.file
 1293:         download = self.transfers.get(username + virtual_path)
 1294: 
 1295:         if download is None:
 1296:             return
 1297: 
 1298:         if (download.token not in self.active_users.get(username, {})
 1299:                 and virtual_path not in self.failed_users.get(username, {})
 1300:                 and virtual_path not in self.queued_users.get(username, {})):
 1301:             return
 1302: 
```
### transfers.py:527-567 — transfers_active

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
```
### slskmessages.py:3525-3564 — slsk_transfer_request

```text
 3525: class TransferRequest(PeerMessage):
 3526:     """Peer code 40.
 3527: 
 3528:     This message is sent by a peer once they are ready to start
 3529:     uploading a file. A TransferResponse message is expected from the
 3530:     recipient, either allowing or rejecting the upload attempt.
 3531: 
 3532:     This message was formerly used to send a download request (direction
 3533:     0) as well, but Nicotine+ >= 3.0.3, Museek+ and the official clients
 3534:     use the QueueUpload message for this purpose today.
 3535:     """
 3536: 
 3537:     __slots__ = ("direction", "token", "file", "filesize")
 3538: 
 3539:     def __init__(self, direction=None, token=None, file=None, filesize=None):
 3540:         PeerMessage.__init__(self)
 3541:         self.direction = direction
 3542:         self.token = token
 3543:         self.file = file  # virtual file
 3544:         self.filesize = filesize
 3545: 
 3546:     def make_network_message(self):
 3547:         msg = bytearray()
 3548:         msg += self.pack_uint32(self.direction)
 3549:         msg += self.pack_uint32(self.token)
 3550:         msg += self.pack_string(self.file)
 3551: 
 3552:         if self.direction == TransferDirection.UPLOAD:
 3553:             msg += self.pack_uint64(self.filesize)
 3554: 
 3555:         return msg
 3556: 
 3557:     def parse_network_message(self, message):
 3558:         pos, self.direction = self.unpack_uint32(message)
 3559:         pos, self.token = self.unpack_uint32(message, pos)
 3560:         pos, self.file = self.unpack_string(message, pos)
 3561: 
 3562:         if self.direction == TransferDirection.UPLOAD:
 3563:             pos, self.filesize = self.unpack_uint64(message, pos)
 3564: 
```
## github-branch-3.3.x
### downloads.py:1074-1108 — downloads_transfer_request

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
```
### downloads.py:1163-1175 — downloads_file_init

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
```
### downloads.py:1302-1316 — downloads_upload_failed

```text
 1302:     def _upload_failed(self, msg):
 1303:         """Peer code 46."""
 1304: 
 1305:         username = msg.username
 1306:         virtual_path = msg.file
 1307:         download = self.transfers.get(username + virtual_path)
 1308: 
 1309:         if download is None:
 1310:             return
 1311: 
 1312:         if (download.token not in self.active_users.get(username, {})
 1313:                 and virtual_path not in self.failed_users.get(username, {})
 1314:                 and virtual_path not in self.queued_users.get(username, {})):
 1315:             return
 1316: 
```
### transfers.py:527-567 — transfers_active

```text
  527:         transfer.queue_position = 0
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
```
### slskmessages.py:3527-3566 — slsk_transfer_request

```text
 3527:             folders[directory] = []
 3528: 
 3529:             for _ in range(nfiles):
 3530:                 pos, code = self.unpack_uint8(message, pos)
 3531:                 pos, name = self.unpack_string(message, pos)
 3532:                 pos, size = self.unpack_uint64(message, pos)
 3533:                 pos, ext_len = self.unpack_uint32(message, pos)  # Obsolete, ignore
 3534:                 pos, attrs = FileListMessage.unpack_file_attributes(message, pos + ext_len)
 3535: 
 3536:                 folders[directory].append((code, name, size, ext, attrs))
 3537: 
 3538:             if nfiles > 1:
 3539:                 folders[directory].sort(key=itemgetter(1))
 3540: 
 3541:         self.list = folders
 3542: 
 3543:     def make_network_message(self):
 3544:         msg = bytearray()
 3545:         msg += self.pack_uint32(self.token)
 3546:         msg += self.pack_string(self.dir)
 3547: 
 3548:         if self.list is not None:
 3549:             msg += self.pack_uint32(1)
 3550:             msg += self.pack_string(self.dir)
 3551: 
 3552:             # We already saved the folder contents as a bytearray when scanning our shares
 3553:             msg += self.list
 3554:         else:
 3555:             # No folder contents
 3556:             msg += self.pack_uint32(0)
 3557: 
 3558:         return zlib.compress(msg)
 3559: 
 3560: 
 3561: class TransferRequest(PeerMessage):
 3562:     """Peer code 40.
 3563: 
 3564:     This message is sent by a peer once they are ready to start
 3565:     uploading a file. A TransferResponse message is expected from the
 3566:     recipient, either allowing or rejecting the upload attempt.
```
## github-branch-master
### downloads.py:1045-1079 — downloads_transfer_request

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
```
### downloads.py:1134-1146 — downloads_file_init

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
```
### downloads.py:1273-1287 — downloads_upload_failed

```text
 1273:     def _upload_failed(self, msg):
 1274:         """Peer code 46."""
 1275: 
 1276:         username = msg.username
 1277:         virtual_path = msg.file
 1278:         download = self.transfers.get(username + virtual_path)
 1279: 
 1280:         if download is None:
 1281:             return
 1282: 
 1283:         if (download.token not in self.active_users.get(username, {})
 1284:                 and virtual_path not in self.failed_users.get(username, {})
 1285:                 and virtual_path not in self.queued_users.get(username, {})):
 1286:             return
 1287: 
```
### transfers.py:513-553 — transfers_active

```text
  513:         del self.queued_transfers[transfer]
  514:         del self.queued_users[username][virtual_path]
  515: 
  516:         if self._user_queue_sizes[username] <= 0:
  517:             del self._user_queue_sizes[username]
  518: 
  519:         if not self.queued_users[username]:
  520:             del self.queued_users[username]
  521: 
  522:             # No more queued transfers, resume limited transfers if present
  523:             self._enqueue_limited_transfers(username)
  524: 
  525:         transfer.queue_position = 0
  526:         return True
  527: 
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
```
### slskmessages.py:3543-3582 — slsk_transfer_request

```text
 3543:     __slots__ = ()
 3544: 
 3545:     def make_network_message(self):
 3546:         return b""
 3547: 
 3548:     def parse_network_message(self):
 3549:         # Empty message
 3550:         pass
 3551: 
 3552: 
 3553: class UserInfoResponse(PeerMessage):
 3554:     """Peer code 16.
 3555: 
 3556:     A peer responds with this after we've sent a UserInfoRequest.
 3557:     """
 3558: 
 3559:     __slots__ = ("descr", "pic", "totalupl", "queuesize", "slotsavail", "uploadallowed", "has_pic")
 3560:     __excluded_attrs__ = {"pic"}
 3561: 
 3562:     def __init__(self, descr=None, pic=None, totalupl=None, queuesize=None,
 3563:                  slotsavail=None, uploadallowed=None, *, msg_content=None):
 3564:         PeerMessage.__init__(self, msg_content)
 3565:         self.descr = descr
 3566:         self.pic = pic
 3567:         self.totalupl = totalupl
 3568:         self.queuesize = queuesize
 3569:         self.slotsavail = slotsavail
 3570:         self.uploadallowed = uploadallowed
 3571:         self.has_pic = None
 3572: 
 3573:     def make_network_message(self):
 3574:         msg = bytearray()
 3575:         msg += self.pack_string(self.descr)
 3576: 
 3577:         if self.pic is not None:
 3578:             msg += self.pack_bool(True)
 3579:             msg += self.pack_bytes(self.pic)
 3580:         else:
 3581:             msg += self.pack_bool(False)
 3582: 
```
