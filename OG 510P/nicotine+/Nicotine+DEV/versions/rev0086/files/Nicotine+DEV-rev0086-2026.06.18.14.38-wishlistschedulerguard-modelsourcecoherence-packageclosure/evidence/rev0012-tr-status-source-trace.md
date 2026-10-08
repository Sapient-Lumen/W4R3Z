# rev0012 TR-STATUS-01 source trace

Scope: Downloads handlers for UploadDenied, UploadFailed and PlaceInQueueResponse, plus the peer-message parser shapes. The trace covers the archived 3.3.10, 3.3.x and master lanes from the rev0003 source bundle.

## github-tag-3.3.10

### pynicotine/downloads.py handlers

#### `def _upload_denied` around line 1245

```python
 1241:         if download_started:
 1242:             # Must be emitted after the final update to prevent inconsistent state
 1243:             core.pluginhandler.download_started_notification(username, virtual_path, incomplete_file_path)
 1244: 
 1245:     def _upload_denied(self, msg):
 1246:         """Peer code 50."""
 1247: 
 1248:         username = msg.username
 1249:         virtual_path = msg.file
 1250:         reason = msg.reason
 1251:         queued_downloads = self.queued_users.get(username, {})
 1252:         download = queued_downloads.get(virtual_path)
 1253: 
 1254:         if download is None:
 1255:             return
 1256: 
 1257:         if reason in TransferStatus.__dict__.values():
 1258:             # Don't allow internal statuses as reason
 1259:             reason = TransferRejectReason.CANCELLED
 1260: 
 1261:         if reason == TransferRejectReason.FILE_NOT_SHARED and not download.legacy_attempt:
 1262:             # The peer is possibly using an old client that doesn't support Unicode
 1263:             # (Soulseek NS). Attempt to request file name encoded as latin-1 once.
 1264: 
 1265:             log.add_transfer("User %s responded with reason '%s' for download request %s. "
 1266:                              "Attempting to request file as latin-1.", (username, reason, virtual_path))
 1267: 
 1268:             self._dequeue_transfer(download)
 1269:             download.legacy_attempt = True
 1270: 
 1271:             if self._enqueue_transfer(download):
 1272:                 self._update_transfer(download)
 1273: 
 1274:             return
 1275: 
 1276:         if (reason in {TransferRejectReason.TOO_MANY_FILES, TransferRejectReason.TOO_MANY_MEGABYTES}
 1277:                 or reason.startswith("User limit of")):
 1278:             # Make limited downloads appear as queued, and automatically resume them later
 1279:             reason = TransferRejectReason.QUEUED
 1280:             self._user_queue_limits[username] = max(5, len(queued_downloads) - 1)
 1281: 
 1282:         self._abort_transfer(download, status=reason)
 1283:         self._update_transfer(download)
 1284: 
 1285:         log.add_transfer("Download request denied by user %s for file %s. Reason: %s",
 1286:                          (username, virtual_path, msg.reason))
 1287: 
 1288:     def _upload_failed(self, msg):
 1289:         """Peer code 46."""
 1290: 
```

#### `def _upload_failed` around line 1288

```python
 1284: 
 1285:         log.add_transfer("Download request denied by user %s for file %s. Reason: %s",
 1286:                          (username, virtual_path, msg.reason))
 1287: 
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
 1303:         if download.status in {TransferStatus.DOWNLOAD_FOLDER_ERROR, TransferStatus.LOCAL_FILE_ERROR}:
 1304:             # Local error, no need to retry
 1305:             return
 1306: 
 1307:         if not download.retry_attempt:
 1308:             # Attempt to request file name encoded as latin-1 once
 1309: 
 1310:             # We mark download as failed when aborting it, to avoid a redundant request
 1311:             # to unwatch the user. Need to call _unfail_transfer() to undo this.
 1312:             self._abort_transfer(download, status=TransferStatus.CONNECTION_CLOSED)
 1313:             self._unfail_transfer(download)
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
```

#### `def _place_in_queue_response` around line 1369

```python
 1365:             status = TransferStatus.CANCELLED
 1366: 
 1367:         self._abort_transfer(download, status=status)
 1368: 
 1369:     def _place_in_queue_response(self, msg):
 1370:         """Peer code 44.
 1371: 
 1372:         The peer tells us our place in queue for a particular transfer
 1373:         """
 1374: 
 1375:         username = msg.username
 1376:         virtual_path = msg.filename
 1377:         download = self.queued_users.get(username, {}).get(virtual_path)
 1378: 
 1379:         if download is None:
 1380:             return
 1381: 
 1382:         download.queue_position = msg.place
 1383:         self._update_transfer(download, update_parent=False)
```

### pynicotine/slskmessages.py message shapes

#### `class PlaceInQueueResponse` around line 3647

```python
 3645: 
 3646: 
 3647: class PlaceInQueueResponse(PeerMessage):
 3648:     """Peer code 44.
 3649: 
 3650:     The peer replies with the upload queue placement of the requested
 3651:     file.
 3652:     """
 3653: 
 3654:     __slots__ = ("filename", "place")
 3655: 
 3656:     def __init__(self, filename=None, place=None):
 3657:         PeerMessage.__init__(self)
 3658:         self.filename = filename
 3659:         self.place = place
 3660: 
 3661:     def make_network_message(self):
 3662:         msg = bytearray()
 3663:         msg += self.pack_string(self.filename)
 3664:         msg += self.pack_uint32(self.place)
 3665: 
 3666:         return msg
 3667: 
 3668:     def parse_network_message(self, message):
 3669:         pos, self.filename = self.unpack_string(message)
 3670:         pos, self.place = self.unpack_uint32(message, pos)
 3671: 
 3672: 
 3673: class UploadFailed(PeerMessage):
 3674:     """Peer code 46.
```

#### `class UploadFailed` around line 3673

```python
 3671: 
 3672: 
 3673: class UploadFailed(PeerMessage):
 3674:     """Peer code 46.
 3675: 
 3676:     This message is sent whenever a file connection of an active upload
 3677:     closes. Soulseek NS clients can also send this message when a file
 3678:     cannot be read. The recipient either re-queues the upload (download
 3679:     on their end), or ignores the message if the transfer finished.
 3680:     """
 3681: 
 3682:     __slots__ = ("file",)
 3683: 
 3684:     def __init__(self, file=None):
 3685:         PeerMessage.__init__(self)
 3686:         self.file = file
 3687: 
 3688:     def make_network_message(self):
 3689:         return self.pack_string(self.file)
 3690: 
 3691:     def parse_network_message(self, message):
 3692:         _pos, self.file = self.unpack_string(message)
 3693: 
 3694: 
 3695: class UploadDenied(PeerMessage):
 3696:     """Peer code 50.
 3697: 
 3698:     This message is sent to reject QueueUpload attempts and previously
 3699:     queued files. The reason for rejection will appear in the transfer
 3700:     list of the recipient.
```

#### `class UploadDenied` around line 3695

```python
 3693: 
 3694: 
 3695: class UploadDenied(PeerMessage):
 3696:     """Peer code 50.
 3697: 
 3698:     This message is sent to reject QueueUpload attempts and previously
 3699:     queued files. The reason for rejection will appear in the transfer
 3700:     list of the recipient.
 3701:     """
 3702: 
 3703:     __slots__ = ("file", "reason")
 3704: 
 3705:     def __init__(self, file=None, reason=None):
 3706:         PeerMessage.__init__(self)
 3707:         self.file = file
 3708:         self.reason = reason
 3709: 
 3710:     def make_network_message(self):
 3711:         msg = bytearray()
 3712:         msg += self.pack_string(self.file)
 3713:         msg += self.pack_string(self.reason)
 3714: 
 3715:         return msg
 3716: 
 3717:     def parse_network_message(self, message):
 3718:         pos, self.file = self.unpack_string(message)
 3719:         pos, self.reason = self.unpack_string(message, pos)
 3720: 
 3721: 
 3722: class PlaceInQueueRequest(PeerMessage):
```

## github-branch-3.3.x

### pynicotine/downloads.py handlers

#### `def _upload_denied` around line 1259

```python
 1255:         if download_started:
 1256:             # Must be emitted after the final update to prevent inconsistent state
 1257:             core.pluginhandler.download_started_notification(username, virtual_path, incomplete_file_path)
 1258: 
 1259:     def _upload_denied(self, msg):
 1260:         """Peer code 50."""
 1261: 
 1262:         username = msg.username
 1263:         virtual_path = msg.file
 1264:         reason = msg.reason
 1265:         queued_downloads = self.queued_users.get(username, {})
 1266:         download = queued_downloads.get(virtual_path)
 1267: 
 1268:         if download is None:
 1269:             return
 1270: 
 1271:         if reason in TransferStatus.__dict__.values():
 1272:             # Don't allow internal statuses as reason
 1273:             reason = TransferRejectReason.CANCELLED
 1274: 
 1275:         if reason == TransferRejectReason.FILE_NOT_SHARED and not download.legacy_attempt:
 1276:             # The peer is possibly using an old client that doesn't support Unicode
 1277:             # (Soulseek NS). Attempt to request file name encoded as latin-1 once.
 1278: 
 1279:             log.add_transfer("User %s responded with reason '%s' for download request %s. "
 1280:                              "Attempting to request file as latin-1.", (username, reason, virtual_path))
 1281: 
 1282:             self._dequeue_transfer(download)
 1283:             download.legacy_attempt = True
 1284: 
 1285:             if self._enqueue_transfer(download):
 1286:                 self._update_transfer(download)
 1287: 
 1288:             return
 1289: 
 1290:         if (reason in {TransferRejectReason.TOO_MANY_FILES, TransferRejectReason.TOO_MANY_MEGABYTES}
 1291:                 or reason.startswith("User limit of")):
 1292:             # Make limited downloads appear as queued, and automatically resume them later
 1293:             reason = TransferRejectReason.QUEUED
 1294:             self._user_queue_limits[username] = max(5, len(queued_downloads) - 1)
 1295: 
 1296:         self._abort_transfer(download, status=reason)
 1297:         self._update_transfer(download)
 1298: 
 1299:         log.add_transfer("Download request denied by user %s for file %s. Reason: %s",
 1300:                          (username, virtual_path, msg.reason))
 1301: 
 1302:     def _upload_failed(self, msg):
 1303:         """Peer code 46."""
 1304: 
```

#### `def _upload_failed` around line 1302

```python
 1298: 
 1299:         log.add_transfer("Download request denied by user %s for file %s. Reason: %s",
 1300:                          (username, virtual_path, msg.reason))
 1301: 
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
```

#### `def _place_in_queue_response` around line 1383

```python
 1379:             status = TransferStatus.CANCELLED
 1380: 
 1381:         self._abort_transfer(download, status=status)
 1382: 
 1383:     def _place_in_queue_response(self, msg):
 1384:         """Peer code 44.
 1385: 
 1386:         The peer tells us our place in queue for a particular transfer
 1387:         """
 1388: 
 1389:         username = msg.username
 1390:         virtual_path = msg.filename
 1391:         download = self.queued_users.get(username, {}).get(virtual_path)
 1392: 
 1393:         if download is None:
 1394:             return
 1395: 
 1396:         download.queue_position = msg.place
 1397:         self._update_transfer(download, update_parent=False)
```

### pynicotine/slskmessages.py message shapes

#### `class PlaceInQueueResponse` around line 3692

```python
 3690: 
 3691: 
 3692: class PlaceInQueueResponse(PeerMessage):
 3693:     """Peer code 44.
 3694: 
 3695:     The peer replies with the upload queue placement of the requested
 3696:     file.
 3697:     """
 3698: 
 3699:     __slots__ = ("filename", "place")
 3700: 
 3701:     def __init__(self, filename=None, place=None):
 3702:         PeerMessage.__init__(self)
 3703:         self.filename = filename
 3704:         self.place = place
 3705: 
 3706:     def make_network_message(self):
 3707:         msg = bytearray()
 3708:         msg += self.pack_string(self.filename)
 3709:         msg += self.pack_uint32(self.place)
 3710: 
 3711:         return msg
 3712: 
 3713:     def parse_network_message(self, message):
 3714:         pos, self.filename = self.unpack_string(message)
 3715:         pos, self.place = self.unpack_uint32(message, pos)
 3716: 
 3717: 
 3718: class UploadFailed(PeerMessage):
 3719:     """Peer code 46.
```

#### `class UploadFailed` around line 3718

```python
 3716: 
 3717: 
 3718: class UploadFailed(PeerMessage):
 3719:     """Peer code 46.
 3720: 
 3721:     This message is sent whenever a file connection of an active upload
 3722:     closes. Soulseek NS clients can also send this message when a file
 3723:     cannot be read. The recipient either re-queues the upload (download
 3724:     on their end), or ignores the message if the transfer finished.
 3725:     """
 3726: 
 3727:     __slots__ = ("file",)
 3728: 
 3729:     def __init__(self, file=None):
 3730:         PeerMessage.__init__(self)
 3731:         self.file = file
 3732: 
 3733:     def make_network_message(self):
 3734:         return self.pack_string(self.file)
 3735: 
 3736:     def parse_network_message(self, message):
 3737:         _pos, self.file = self.unpack_string(message)
 3738: 
 3739: 
 3740: class UploadDenied(PeerMessage):
 3741:     """Peer code 50.
 3742: 
 3743:     This message is sent to reject QueueUpload attempts and previously
 3744:     queued files. The reason for rejection will appear in the transfer
 3745:     list of the recipient.
```

#### `class UploadDenied` around line 3740

```python
 3738: 
 3739: 
 3740: class UploadDenied(PeerMessage):
 3741:     """Peer code 50.
 3742: 
 3743:     This message is sent to reject QueueUpload attempts and previously
 3744:     queued files. The reason for rejection will appear in the transfer
 3745:     list of the recipient.
 3746:     """
 3747: 
 3748:     __slots__ = ("file", "reason")
 3749: 
 3750:     def __init__(self, file=None, reason=None):
 3751:         PeerMessage.__init__(self)
 3752:         self.file = file
 3753:         self.reason = reason
 3754: 
 3755:     def make_network_message(self):
 3756:         msg = bytearray()
 3757:         msg += self.pack_string(self.file)
 3758:         msg += self.pack_string(self.reason)
 3759: 
 3760:         return msg
 3761: 
 3762:     def parse_network_message(self, message):
 3763:         pos, self.file = self.unpack_string(message)
 3764:         pos, self.reason = self.unpack_string(message, pos)
 3765: 
 3766: 
 3767: class PlaceInQueueRequest(PeerMessage):
```

## github-branch-master

### pynicotine/downloads.py handlers

#### `def _upload_denied` around line 1230

```python
 1226:         if download_started:
 1227:             # Must be emitted after the final update to prevent inconsistent state
 1228:             core.pluginhandler.download_started_notification(username, virtual_path, incomplete_file_path)
 1229: 
 1230:     def _upload_denied(self, msg):
 1231:         """Peer code 50."""
 1232: 
 1233:         username = msg.username
 1234:         virtual_path = msg.file
 1235:         reason = msg.reason
 1236:         queued_downloads = self.queued_users.get(username, {})
 1237:         download = queued_downloads.get(virtual_path)
 1238: 
 1239:         if download is None:
 1240:             return
 1241: 
 1242:         if reason in TransferStatus.__dict__.values():
 1243:             # Don't allow internal statuses as reason
 1244:             reason = TransferRejectReason.CANCELLED
 1245: 
 1246:         if reason == TransferRejectReason.FILE_NOT_SHARED and not download.legacy_attempt:
 1247:             # The peer is possibly using an old client that doesn't support Unicode
 1248:             # (Soulseek NS). Attempt to request file name encoded as latin-1 once.
 1249: 
 1250:             log.add_transfer("User %s responded with reason '%s' for download request %s. "
 1251:                              "Attempting to request file as latin-1.", (username, reason, virtual_path))
 1252: 
 1253:             self._dequeue_transfer(download)
 1254:             download.legacy_attempt = True
 1255: 
 1256:             if self._enqueue_transfer(download):
 1257:                 self._update_transfer(download)
 1258: 
 1259:             return
 1260: 
 1261:         if (reason in {TransferRejectReason.TOO_MANY_FILES, TransferRejectReason.TOO_MANY_MEGABYTES}
 1262:                 or reason.startswith("User limit of")):
 1263:             # Make limited downloads appear as queued, and automatically resume them later
 1264:             reason = TransferRejectReason.QUEUED
 1265:             self._user_queue_limits[username] = max(5, len(queued_downloads) - 1)
 1266: 
 1267:         self._abort_transfer(download, status=reason)
 1268:         self._update_transfer(download)
 1269: 
 1270:         log.add_transfer("Download request denied by user %s for file %s. Reason: %s",
 1271:                          (username, virtual_path, msg.reason))
 1272: 
 1273:     def _upload_failed(self, msg):
 1274:         """Peer code 46."""
 1275: 
```

#### `def _upload_failed` around line 1273

```python
 1269: 
 1270:         log.add_transfer("Download request denied by user %s for file %s. Reason: %s",
 1271:                          (username, virtual_path, msg.reason))
 1272: 
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
 1288:         if download.status in {TransferStatus.DOWNLOAD_FOLDER_ERROR, TransferStatus.LOCAL_FILE_ERROR}:
 1289:             # Local error, no need to retry
 1290:             return
 1291: 
 1292:         if not download.retry_attempt:
 1293:             # Attempt to request file name encoded as latin-1 once
 1294: 
 1295:             # We mark download as failed when aborting it, to avoid a redundant request
 1296:             # to unwatch the user. Need to call _unfail_transfer() to undo this.
 1297:             self._abort_transfer(download, status=TransferStatus.CONNECTION_CLOSED)
 1298:             self._unfail_transfer(download)
 1299: 
 1300:             download.legacy_attempt = download.retry_attempt = True
 1301: 
 1302:             if self._enqueue_transfer(download):
 1303:                 self._update_transfer(download)
 1304: 
 1305:             return
 1306: 
 1307:         # Already failed once previously, give up
 1308:         self._abort_transfer(download, status=TransferStatus.CONNECTION_CLOSED)
 1309:         download.retry_attempt = False
 1310: 
 1311:         log.add_transfer("Upload attempt by user %s for file %s failed. Reason: %s",
 1312:                          (virtual_path, username, download.status))
 1313: 
 1314:     def _file_download_progress(self, username, token, bytes_left, speed=None):
 1315:         """A file download is in progress."""
 1316: 
 1317:         download = self.active_users.get(username, {}).get(token)
 1318: 
```

#### `def _place_in_queue_response` around line 1354

```python
 1350:             status = TransferStatus.CANCELLED
 1351: 
 1352:         self._abort_transfer(download, status=status)
 1353: 
 1354:     def _place_in_queue_response(self, msg):
 1355:         """Peer code 44.
 1356: 
 1357:         The peer tells us our place in queue for a particular transfer
 1358:         """
 1359: 
 1360:         username = msg.username
 1361:         virtual_path = msg.filename
 1362:         download = self.queued_users.get(username, {}).get(virtual_path)
 1363: 
 1364:         if download is None:
 1365:             return
 1366: 
 1367:         download.queue_position = msg.place
 1368:         self._update_transfer(download, update_parent=False)
```

### pynicotine/slskmessages.py message shapes

#### `class PlaceInQueueResponse` around line 3850

```python
 3848: 
 3849: 
 3850: class PlaceInQueueResponse(PeerMessage):
 3851:     """Peer code 44.
 3852: 
 3853:     The peer replies with the upload queue placement of the requested
 3854:     file.
 3855:     """
 3856: 
 3857:     __slots__ = ("filename", "place")
 3858: 
 3859:     def __init__(self, filename=None, place=None, *, msg_content=None):
 3860:         PeerMessage.__init__(self, msg_content)
 3861:         self.filename = filename
 3862:         self.place = place
 3863: 
 3864:     def make_network_message(self):
 3865:         msg = bytearray()
 3866:         msg += self.pack_string(self.filename)
 3867:         msg += self.pack_uint32(self.place)
 3868: 
 3869:         return msg
 3870: 
 3871:     def parse_network_message(self):
 3872:         self.filename = self.unpack_string()
 3873:         self.place = self.unpack_uint32()
 3874: 
 3875: 
 3876: class UploadFailed(PeerMessage):
 3877:     """Peer code 46.
```

#### `class UploadFailed` around line 3876

```python
 3874: 
 3875: 
 3876: class UploadFailed(PeerMessage):
 3877:     """Peer code 46.
 3878: 
 3879:     This message is sent whenever a file connection of an active upload
 3880:     closes. Soulseek NS clients can also send this message when a file
 3881:     cannot be read. The recipient either re-queues the upload (download
 3882:     on their end), or ignores the message if the transfer finished.
 3883:     """
 3884: 
 3885:     __slots__ = ("file",)
 3886: 
 3887:     def __init__(self, file=None, *, msg_content=None):
 3888:         PeerMessage.__init__(self, msg_content)
 3889:         self.file = file
 3890: 
 3891:     def make_network_message(self):
 3892:         return self.pack_string(self.file)
 3893: 
 3894:     def parse_network_message(self):
 3895:         self.file = self.unpack_string()
 3896: 
 3897: 
 3898: class UploadDenied(PeerMessage):
 3899:     """Peer code 50.
 3900: 
 3901:     This message is sent to reject QueueUpload attempts and previously
 3902:     queued files. The reason for rejection will appear in the transfer
 3903:     list of the recipient.
```

#### `class UploadDenied` around line 3898

```python
 3896: 
 3897: 
 3898: class UploadDenied(PeerMessage):
 3899:     """Peer code 50.
 3900: 
 3901:     This message is sent to reject QueueUpload attempts and previously
 3902:     queued files. The reason for rejection will appear in the transfer
 3903:     list of the recipient.
 3904:     """
 3905: 
 3906:     __slots__ = ("file", "reason")
 3907: 
 3908:     def __init__(self, file=None, reason=None, *, msg_content=None):
 3909:         PeerMessage.__init__(self, msg_content)
 3910:         self.file = file
 3911:         self.reason = reason
 3912: 
 3913:     def make_network_message(self):
 3914:         msg = bytearray()
 3915:         msg += self.pack_string(self.file)
 3916:         msg += self.pack_string(self.reason)
 3917: 
 3918:         return msg
 3919: 
 3920:     def parse_network_message(self):
 3921:         self.file = self.unpack_string()
 3922:         self.reason = self.unpack_string()
 3923: 
 3924: 
 3925: class PlaceInQueueRequest(PeerMessage):
```
