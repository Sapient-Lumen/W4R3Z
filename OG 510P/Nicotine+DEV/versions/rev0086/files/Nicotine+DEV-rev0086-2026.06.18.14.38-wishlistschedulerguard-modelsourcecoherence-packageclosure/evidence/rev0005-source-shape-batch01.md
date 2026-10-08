# rev0005 source-shape batch 01

This file records compact source evidence from the external rev0003 source bundle. The bundle is not embedded in this datacube; it remains an external analysis inventory.

## Source lanes

- `github-tag-3.3.10`: `caf9e101a841ff2e0a96aebc8e07bbf7ff1b2026`
- `github-branch-3.3.x`: `98089ac233aa57786e8dbdc48123f6ac1c4767d8`
- `github-branch-master`: `f4e17d59783dbc48ea31d2e899a681e2dd1ed500`

## Main observations

1. `FileSearchResponse` still decompresses a username-length/token prefix before token rejection in all three source lanes checked. 3.3.x and master add a 128 MiB cap to the rest of the uncompressed message, which partially overlaps U-267/U-262/U-266 style resource-budget concerns.
2. 3.3.10 download/upload FileTransferInit handlers silently return on unknown/already-bound tokens, while 3.3.x and master close unknown-token connections. This makes U-169/U-170 an upstream-overlap/backport/regression lane rather than a clean fresh strict finding.
3. Master adds `allowed_responses` gating to `FolderContentsResponse` before decompressing the rest of the response, which overlaps U-167/U-255/U-268.
4. PlaceInQueueRequest parsing and `_place_in_queue_request()` queue lookup still appear to use the decoded path directly in the lanes sampled, but public discussion and PR overlap mean this is not a clean novelty claim.

### github-tag-3.3.10: `pynicotine/slskmessages.py` FileSearchResponse parse/result-list path

```text
 3280:     def parse_network_message(self, message):
 3281:         decompressor = zlib.decompressobj()
 3282:         _pos, username_len = self.unpack_uint32(decompressor.decompress(message, 4))
 3283:         _pos, self.token = self.unpack_uint32(
 3284:             decompressor.decompress(decompressor.unconsumed_tail, username_len + 4), username_len)
 3285: 
 3286:         if self.token not in SEARCH_TOKENS_ALLOWED:
 3287:             # Results are no longer accepted for this search token, stop parsing message
 3288:             self.list = []
 3289:             return
 3290: 
 3291:         # Optimization: only decompress the rest of the message when needed
 3292:         self._parse_remaining_network_message(
 3293:             memoryview(decompressor.decompress(decompressor.unconsumed_tail))
 3294:         )
 3295: 
 3296:     def _parse_remaining_network_message(self, message):
 3297:         pos, self.list = self._parse_result_list(message)
 3298:         pos, self.freeulslots = self.unpack_bool(message, pos)
 3299:         pos, self.ulspeed = self.unpack_uint32(message, pos)
 3300:         pos, self.inqueue = self.unpack_uint32(message, pos)
 3301: 
 3302:         if message[pos:]:
 3303:             pos, self.unknown = self.unpack_uint32(message, pos)
 3304: 
 3305:         if message[pos:]:
 3306:             pos, self.privatelist = self._parse_result_list(message, pos)
 3307: 
 3308:     def _parse_result_list(self, message, pos=0):
 3309:         pos, nfiles = self.unpack_uint32(message, pos)
 3310: 
 3311:         ext = None
 3312:         results = []
 3313: 
 3314:         for _ in range(nfiles):
 3315:             pos, code = self.unpack_uint8(message, pos)
 3316:             pos, name = self.unpack_string(message, pos)
 3317:             pos, size = FileListMessage.parse_file_size(message, pos)
 3318:             pos, ext_len = self.unpack_uint32(message, pos)  # Obsolete, ignore
 3319:             pos, attrs = FileListMessage.unpack_file_attributes(message, pos + ext_len)
 3320: 
 3321:             results.append((code, name.replace("/", "\\"), size, ext, attrs))
 3322: 
 3323:         if nfiles > 1:
 3324:             results.sort(key=itemgetter(1))
 3325: 
 3326:         return pos, results
```
### github-branch-3.3.x: `pynicotine/slskmessages.py` FileSearchResponse parse/result-list path

```text
 3308:     def parse_network_message(self, message):
 3309:         decompressor = zlib.decompressobj()
 3310:         max_uncompressed_size = 134217728  # 128 MiB
 3311: 
 3312:         _pos, username_len = self.unpack_uint32(decompressor.decompress(message, 4))
 3313:         _pos, self.token = self.unpack_uint32(
 3314:             decompressor.decompress(decompressor.unconsumed_tail, username_len + 4), username_len)
 3315: 
 3316:         if self.token not in SEARCH_TOKENS_ALLOWED:
 3317:             # Results are no longer accepted for this search token, stop parsing message
 3318:             self.list = []
 3319:             return
 3320: 
 3321:         # Optimization: only decompress the rest of the message when needed
 3322:         decompressed_message = decompressor.decompress(decompressor.unconsumed_tail, max_uncompressed_size)
 3323: 
 3324:         if not decompressor.unconsumed_tail:
 3325:             self._parse_remaining_network_message(memoryview(decompressed_message))
 3326: 
 3327:     def _parse_remaining_network_message(self, message):
 3328:         pos, self.list = self._parse_result_list(message)
 3329:         pos, self.freeulslots = self.unpack_bool(message, pos)
 3330:         pos, self.ulspeed = self.unpack_uint32(message, pos)
 3331:         pos, self.inqueue = self.unpack_uint32(message, pos)
 3332: 
 3333:         if message[pos:]:
 3334:             pos, self.unknown = self.unpack_uint32(message, pos)
 3335: 
 3336:         if message[pos:]:
 3337:             pos, self.privatelist = self._parse_result_list(message, pos)
 3338: 
 3339:     def _parse_result_list(self, message, pos=0):
 3340:         pos, nfiles = self.unpack_uint32(message, pos)
 3341: 
 3342:         ext = None
 3343:         results = []
 3344: 
 3345:         for _ in range(nfiles):
 3346:             pos, code = self.unpack_uint8(message, pos)
 3347:             pos, name = self.unpack_string(message, pos)
 3348:             pos, size = FileListMessage.parse_file_size(message, pos)
 3349:             pos, ext_len = self.unpack_uint32(message, pos)  # Obsolete, ignore
 3350:             pos, attrs = FileListMessage.unpack_file_attributes(message, pos + ext_len)
 3351: 
 3352:             results.append((code, name.replace("/", "\\"), size, ext, attrs))
 3353: 
 3354:         if nfiles > 1:
 3355:             results.sort(key=itemgetter(1))
 3356: 
 3357:         return pos, results
```
### github-branch-master: `pynicotine/slskmessages.py` FileSearchResponse parse/result-list path

```text
 3481:     def parse_network_message(self):
 3482:         decompressor = zlib.decompressobj()
 3483:         max_uncompressed_size = 134217728  # 128 MiB
 3484: 
 3485:         self._offset = 0
 3486:         self._message = memoryview(decompressor.decompress(self._message, 4))
 3487:         self._offset = username_len = self.unpack_uint32()
 3488:         self._message = memoryview(decompressor.decompress(decompressor.unconsumed_tail, username_len + 4))
 3489:         self.token = self.unpack_uint32()
 3490: 
 3491:         if self.token not in self.allowed_responses:
 3492:             # Results are no longer accepted for this search token, stop parsing message
 3493:             return
 3494: 
 3495:         # Optimization: only decompress the rest of the message when needed
 3496:         self._offset = 0
 3497:         self._message = memoryview(decompressor.decompress(decompressor.unconsumed_tail, max_uncompressed_size))
 3498: 
 3499:         if not decompressor.unconsumed_tail:
 3500:             self._parse_remaining_network_message()
 3501: 
 3502:     def _parse_remaining_network_message(self):
 3503:         self.list = self._parse_result_list()
 3504:         self.freeulslots = self.unpack_bool()
 3505:         self.ulspeed = self.unpack_uint32()
 3506:         self.inqueue = self.unpack_uint32()
 3507: 
 3508:         if self.has_remaining_content():
 3509:             self.unknown = self.unpack_uint32()
 3510: 
 3511:         if self.has_remaining_content():
 3512:             self.privatelist = self._parse_result_list()
 3513: 
 3514:     def _parse_result_list(self):
 3515:         nfiles = self.unpack_uint32()
 3516: 
 3517:         ext = None
 3518:         results = []
 3519: 
 3520:         for _ in range(nfiles):
 3521:             code = self.unpack_uint8()
 3522:             name = self.unpack_string()
 3523:             size = self.unpack_file_size()
 3524:             ext_len = self.unpack_uint32()  # Obsolete, ignore
 3525:             self._offset += ext_len
 3526:             attrs = self.unpack_file_attributes()
 3527: 
 3528:             results.append((code, name.replace("/", "\\"), size, ext, attrs))
 3529: 
 3530:         if nfiles > 1:
```
### github-tag-3.3.10: `pynicotine/search.py` `_file_search_response()` policy gate

```text
  452:     def _file_search_response(self, msg):
  453:         """Peer code 9."""
  454: 
  455:         if msg.token not in SEARCH_TOKENS_ALLOWED:
  456:             msg.token = None
  457:             return
  458: 
  459:         search = self.searches.get(msg.token)
  460: 
  461:         if search is None or search.is_ignored:
  462:             msg.token = None
  463:             return
  464: 
  465:         username = msg.username
  466:         ip_address, _port = msg.addr
  467: 
  468:         if core.network_filter.is_user_ignored(username):
  469:             msg.token = None
  470:             return
  471: 
  472:         if core.network_filter.is_user_ip_ignored(username, ip_address):
  473:             msg.token = None
  474: 
```
### github-branch-3.3.x: `pynicotine/search.py` `_file_search_response()` policy gate

```text
  452:     def _file_search_response(self, msg):
  453:         """Peer code 9."""
  454: 
  455:         if msg.token not in SEARCH_TOKENS_ALLOWED:
  456:             msg.token = None
  457:             return
  458: 
  459:         search = self.searches.get(msg.token)
  460: 
  461:         if search is None or search.is_ignored:
  462:             msg.token = None
  463:             return
  464: 
  465:         username = msg.username
  466:         ip_address, _port = msg.addr
  467: 
  468:         if core.network_filter.is_user_ignored(username):
  469:             msg.token = None
  470:             return
  471: 
  472:         if core.network_filter.is_user_ip_ignored(username, ip_address):
  473:             msg.token = None
  474: 
```
### github-branch-master: `pynicotine/search.py` `_file_search_response()` policy gate

```text
  615:     def _file_search_response(self, msg):
  616:         """Peer code 9."""
  617: 
  618:         if msg.list is None:
  619:             # Response was rejected
  620:             msg.token = None
  621:             return
  622: 
  623:         search = self.searches.get(msg.token)
  624:         username = msg.username
  625: 
  626:         if search is None:
  627:             msg.token = None
  628:             return
  629: 
  630:         if isinstance(search, WishSearchRequest) and (search.is_ignored or username in search.ignored_users):
  631:             msg.token = None
  632:             return
  633: 
  634:         ip_address, _port = msg.addr
  635: 
  636:         if core.network_filter.is_user_ignored(username):
  637:             msg.token = None
  638:             return
  639: 
  640:         if core.network_filter.is_user_ip_ignored(username, ip_address):
  641:             msg.token = None
  642: 
```
### github-tag-3.3.10: `pynicotine/downloads.py` FileTransferInit handling

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
### github-branch-3.3.x: `pynicotine/downloads.py` FileTransferInit handling

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
```
### github-branch-master: `pynicotine/downloads.py` FileTransferInit handling

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
```
### github-tag-3.3.10: `pynicotine/uploads.py` FileTransferInit handling

```text
 1066:     def _file_transfer_init(self, msg):
 1067:         """We are requesting to start uploading a file to a peer."""
 1068: 
 1069:         username = msg.username
 1070:         token = msg.token
 1071:         upload = self.active_users.get(username, {}).get(token)
 1072: 
 1073:         if upload is None or upload.sock is not None:
 1074:             return
```
### github-branch-3.3.x: `pynicotine/uploads.py` FileTransferInit handling

```text
 1048:     def _file_transfer_init(self, msg):
 1049:         """We are requesting to start uploading a file to a peer."""
 1050: 
 1051:         if not msg.is_outgoing:
 1052:             # Transfer init message received from another peer, ignore
 1053:             return
 1054: 
 1055:         username = msg.username
 1056:         token = msg.token
 1057:         upload = self.active_users.get(username, {}).get(token)
 1058: 
 1059:         if upload is None or upload.sock is not None:
 1060:             log.add_transfer("Sending file upload init message with unknown token %s, closing connection", token)
 1061:             core.send_message_to_network_thread(CloseConnection(msg.sock))
 1062:             return
```
### github-branch-master: `pynicotine/uploads.py` FileTransferInit handling

```text
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
```
### github-tag-3.3.10: `pynicotine/slskmessages.py` FolderContentsRequest/Response

```text
 3434: class FolderContentsRequest(PeerMessage):
 3435:     """Peer code 36.
 3436: 
 3437:     We ask the peer to send us the contents of a single folder.
 3438:     """
 3439: 
 3440:     __slots__ = ("dir", "token", "legacy_client")
 3441: 
 3442:     def __init__(self, directory=None, token=None, legacy_client=False):
 3443:         PeerMessage.__init__(self)
 3444:         self.dir = directory
 3445:         self.token = token
 3446:         self.legacy_client = legacy_client
 3447: 
 3448:     def make_network_message(self):
 3449:         msg = bytearray()
 3450:         msg += self.pack_uint32(self.token)
 3451:         msg += self.pack_string(self.dir, is_legacy=self.legacy_client)
 3452: 
 3453:         return msg
 3454: 
 3455:     def parse_network_message(self, message):
 3456:         pos, self.token = self.unpack_uint32(message)
 3457:         pos, self.dir = self.unpack_string(message, pos)
 3458: 
 3459: 
 3460: class FolderContentsResponse(PeerMessage):
 3461:     """Peer code 37.
 3462: 
 3463:     A peer responds with the contents of a particular folder (with all
 3464:     subfolders) after we've sent a FolderContentsRequest.
 3465:     """
 3466: 
 3467:     __slots__ = ("dir", "token", "list")
 3468: 
 3469:     def __init__(self, directory=None, token=None, shares=None):
 3470:         PeerMessage.__init__(self)
 3471:         self.dir = directory
 3472:         self.token = token
 3473:         self.list = shares
 3474: 
 3475:     def parse_network_message(self, message):
 3476:         self._parse_network_message(memoryview(zlib.decompress(message)))
 3477: 
 3478:     def _parse_network_message(self, message):
 3479:         pos, self.token = self.unpack_uint32(message)
 3480:         pos, self.dir = self.unpack_string(message, pos)
 3481:         pos, ndir = self.unpack_uint32(message, pos)
 3482: 
 3483:         folders = {}
 3484: 
 3485:         for _ in range(ndir):
 3486:             pos, directory = self.unpack_string(message, pos)
 3487:             directory = directory.replace("/", "\\")
 3488:             pos, nfiles = self.unpack_uint32(message, pos)
 3489: 
 3490:             ext = None
 3491:             folders[directory] = []
 3492: 
 3493:             for _ in range(nfiles):
 3494:                 pos, code = self.unpack_uint8(message, pos)
 3495:                 pos, name = self.unpack_string(message, pos)
 3496:                 pos, size = self.unpack_uint64(message, pos)
 3497:                 pos, ext_len = self.unpack_uint32(message, pos)  # Obsolete, ignore
 3498:                 pos, attrs = FileListMessage.unpack_file_attributes(message, pos + ext_len)
 3499: 
 3500:                 folders[directory].append((code, name, size, ext, attrs))
 3501: 
 3502:             if nfiles > 1:
 3503:                 folders[directory].sort(key=itemgetter(1))
 3504: 
 3505:         self.list = folders
 3506: 
 3507:     def make_network_message(self):
 3508:         msg = bytearray()
 3509:         msg += self.pack_uint32(self.token)
 3510:         msg += self.pack_string(self.dir)
 3511: 
 3512:         if self.list is not None:
 3513:             msg += self.pack_uint32(1)
 3514:             msg += self.pack_string(self.dir)
 3515: 
 3516:             # We already saved the folder contents as a bytearray when scanning our shares
 3517:             msg += self.list
 3518:         else:
 3519:             # No folder contents
 3520:             msg += self.pack_uint32(0)
 3521: 
 3522:         return zlib.compress(msg)
```
### github-branch-master: `pynicotine/slskmessages.py` FolderContentsRequest/Response with allowed_responses gate

```text
 3607: class FolderContentsRequest(PeerMessage):
 3608:     """Peer code 36.
 3609: 
 3610:     We ask the peer to send us the contents of a single folder.
 3611:     """
 3612: 
 3613:     __slots__ = ("dir", "token", "legacy_client")
 3614: 
 3615:     def __init__(self, directory=None, token=None, legacy_client=False, *, msg_content=None):
 3616:         PeerMessage.__init__(self, msg_content)
 3617:         self.dir = directory
 3618:         self.token = token
 3619:         self.legacy_client = legacy_client
 3620: 
 3621:     def make_network_message(self):
 3622:         msg = bytearray()
 3623:         msg += self.pack_uint32(self.token)
 3624:         msg += self.pack_string(self.dir, is_legacy=self.legacy_client)
 3625: 
 3626:         return msg
 3627: 
 3628:     def parse_network_message(self):
 3629:         self.token = self.unpack_uint32()
 3630:         self.dir = self.unpack_string()
 3631: 
 3632: 
 3633: class FolderContentsResponse(PeerMessage):
 3634:     """Peer code 37.
 3635: 
 3636:     A peer responds with the contents of a particular folder (with all
 3637:     subfolders) after we've sent a FolderContentsRequest.
 3638:     """
 3639: 
 3640:     __slots__ = ("dir", "token", "list")
 3641:     __excluded_attrs__ = {"list"}
 3642: 
 3643:     def __init__(self, directory=None, token=None, shares=None, *, msg_content=None):
 3644:         PeerMessage.__init__(self, msg_content)
 3645:         self.dir = directory
 3646:         self.token = token
 3647:         self.list = shares
 3648: 
 3649:     def parse_network_message(self):
 3650:         decompressor = zlib.decompressobj()
 3651:         max_uncompressed_size = 134217728  # 128 MiB
 3652: 
 3653:         self._offset = 0
 3654:         message_bytes = decompressor.decompress(self._message, 8)
 3655:         self._message = memoryview(message_bytes)
 3656:         self.token = self.unpack_uint32()
 3657:         dir_len = self.unpack_uint32()
 3658: 
 3659:         self._offset = 4  # Skip token
 3660:         self._message = memoryview(message_bytes + decompressor.decompress(decompressor.unconsumed_tail, dir_len))
 3661:         self.dir = self.unpack_string()
 3662: 
 3663:         if self.username + self.dir not in self.allowed_responses:
 3664:             return
 3665: 
 3666:         # Optimization: only decompress the rest of the message when needed
 3667:         self._offset = 0
 3668:         self._message = memoryview(decompressor.decompress(decompressor.unconsumed_tail, max_uncompressed_size))
 3669: 
 3670:         if not decompressor.unconsumed_tail:
 3671:             self._parse_remaining_network_message()
```
### github-tag-3.3.10: `pynicotine/uploads.py` _place_in_queue_request

```text
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
### github-branch-3.3.x: `pynicotine/uploads.py` _place_in_queue_request

```text
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
```
### github-branch-master: `pynicotine/uploads.py` _place_in_queue_request

```text
 1272:     def _place_in_queue_request(self, msg):
 1273:         """Peer code 51."""
 1274: 
 1275:         username = msg.username
 1276:         virtual_path = msg.file
 1277:         upload = self.queued_users.get(username, {}).get(virtual_path)
 1278: 
 1279:         if upload is None:
 1280:             return
 1281: 
 1282:         is_fifo_queue = config.sections["transfers"]["fifoqueue"]
 1283:         is_privileged_queue = self.is_privileged(username)
 1284:         privileged_queued_users = {k: len(v) for k, v in self.queued_users.items() if self.is_privileged(k)}
 1285:         queue_position = 0
 1286: 
 1287:         if is_fifo_queue:
 1288:             if is_privileged_queue != self._privileged_position_requested or upload not in self._queue_positions:
 1289:                 self._queue_position_users.clear()
 1290: 
 1291:                 if is_privileged_queue:
 1292:                     self._queue_positions.clear()
 1293:                     position = 1
 1294: 
 1295:                     for i_upload in self.queued_transfers:
 1296:                         if i_upload.username in privileged_queued_users:
 1297:                             self._queue_positions[i_upload] = position
 1298:                             position += 1
 1299:                 else:
 1300:                     self._queue_positions = {
 1301:                         i_upload: position
 1302:                         for position, i_upload in enumerate(self.queued_transfers, start=1)
 1303:                     }
 1304: 
 1305:             queue_position = self._queue_positions[upload]
 1306:         else:
 1307:             user_queue_positions = self._queue_position_users[username]
 1308: 
 1309:             if upload not in user_queue_positions:
 1310:                 self._queue_positions.clear()
 1311:                 user_queue_positions.update({
 1312:                     i_upload: position
 1313:                     for position, i_upload in enumerate(self.queued_users[username].values(), start=1)
 1314:                 })
 1315: 
 1316:             if is_privileged_queue:
 1317:                 num_queued_users = len(privileged_queued_users)
 1318:             else:
 1319:                 # Cycling through privileged users first
 1320:                 queue_position += sum(
 1321:                     num_queued_uploads for num_queued_uploads in privileged_queued_users.values())
 1322:                 num_queued_users = len(self.queued_users)
 1323: 
 1324:             queue_position += num_queued_users + user_queue_positions[upload]
 1325: 
 1326:         self._privileged_position_requested = is_privileged_queue
 1327: 
 1328:         if queue_position > 0:
 1329:             core.send_message_to_peer(
 1330:                 username, PlaceInQueueResponse(virtual_path, queue_position))
 1331: 
 1332:         # Update queue position in our list of uploads
 1333:         upload.queue_position = queue_position
 1334:         self._update_transfer(upload, update_parent=False)
```
### github-tag-3.3.10: `pynicotine/slskmessages.py` PlaceInQueueRequest parser

```text
 3730: 
 3731:     def __init__(self, file=None, legacy_client=False):
 3732:         PeerMessage.__init__(self)
 3733:         self.file = file
 3734:         self.legacy_client = legacy_client
 3735: 
 3736:     def make_network_message(self):
 3737:         return self.pack_string(self.file, is_legacy=self.legacy_client)
 3738: 
 3739:     def parse_network_message(self, message):
 3740:         _pos, self.file = self.unpack_string(message)
 3741: 
 3742: 
 3743: class UploadQueueNotification(PeerMessage):
 3744:     """Peer code 52.
 3745: 
 3746:     This message is sent to inform a peer about an upload attempt
 3747:     initiated by us.
 3748: 
```
### github-branch-3.3.x: `pynicotine/slskmessages.py` PlaceInQueueRequest parser

```text
 3767: class PlaceInQueueRequest(PeerMessage):
 3768:     """Peer code 51.
 3769: 
 3770:     This message is sent when asking for the upload queue placement of a
 3771:     file.
 3772:     """
 3773: 
 3774:     __slots__ = ("file", "legacy_client")
 3775: 
 3776:     def __init__(self, file=None, legacy_client=False):
 3777:         PeerMessage.__init__(self)
 3778:         self.file = file
 3779:         self.legacy_client = legacy_client
 3780: 
 3781:     def make_network_message(self):
 3782:         return self.pack_string(self.file, is_legacy=self.legacy_client)
 3783: 
 3784:     def parse_network_message(self, message):
 3785:         _pos, self.file = self.unpack_string(message)
 3786: 
```
### github-branch-master: `pynicotine/slskmessages.py` PlaceInQueueRequest parser

```text
 3925: class PlaceInQueueRequest(PeerMessage):
 3926:     """Peer code 51.
 3927: 
 3928:     This message is sent when asking for the upload queue placement of a
 3929:     file.
 3930:     """
 3931: 
 3932:     __slots__ = ("file", "legacy_client")
 3933: 
 3934:     def __init__(self, file=None, legacy_client=False, *, msg_content=None):
 3935:         PeerMessage.__init__(self, msg_content)
 3936:         self.file = file
 3937:         self.legacy_client = legacy_client
 3938: 
 3939:     def make_network_message(self):
 3940:         return self.pack_string(self.file, is_legacy=self.legacy_client)
 3941: 
 3942:     def parse_network_message(self):
 3943:         self.file = self.unpack_string()
 3944: 
```

