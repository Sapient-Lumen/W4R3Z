# rev0018 source trace — TRANSFER-SIZE-PROVENANCE-01

Source bundle: `Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z.zip`. Source trees are intentionally external to the compact cube.

This trace supports U-69, U-107, and U-198. It records source shape only; the reproducer in `maintainer_artifacts/transfer-size-provenance-01/` is the behavioral witness.

## github-tag-3.3.10

### U-69 queued-download size mutation from peer TransferRequest

File: `pynicotine/downloads.py` lines approx 1053-1112

```python
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
```

### U-69 F-connection leftbytes uses mutated download.size

File: `pynicotine/downloads.py` lines approx 1080-1249

```python
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
 1130: 
 1131:     def _transfer_timeout(self, transfer):
 1132: 
 1133:         if transfer.request_timer_id is None:
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
 1244: 
 1245:     def _upload_denied(self, msg):
 1246:         """Peer code 50."""
 1247: 
 1248:         username = msg.username
 1249:         virtual_path = msg.file
```

### U-107 network upload read not clamped to remaining advertised size

File: `pynicotine/slskproto.py` lines approx 1963-2013

```python
 1963:         if file_download.leftbytes <= 0:
 1964:             events.emit_main_thread(
 1965:                 "file-download-progress",
 1966:                 username=conn.init.target_user, token=file_download.token,
 1967:                 bytes_left=file_download.leftbytes
 1968:             )
 1969:             return False  # Close the connection
 1970: 
 1971:         return True
 1972: 
 1973:     def _process_upload(self, conn, num_sent_bytes, current_time):
 1974: 
 1975:         file_upload = self._file_upload_msgs[conn]
 1976: 
 1977:         if file_upload.offset is None:
 1978:             return True
 1979: 
 1980:         out_buffer = conn.out_buffer
 1981:         out_buffer_len = len(out_buffer)
 1982:         file_upload.sentbytes += num_sent_bytes
 1983:         total_read_bytes = file_upload.offset + file_upload.sentbytes + out_buffer_len
 1984:         size = file_upload.size
 1985: 
 1986:         try:
 1987:             if total_read_bytes < size:
 1988:                 num_bytes_to_read = int(
 1989:                     (max(4096, num_sent_bytes * 1.25) / max(1, current_time - conn.last_active))
 1990:                     - out_buffer_len
 1991:                 )
 1992:                 if num_bytes_to_read > 0:
 1993:                     out_buffer += file_upload.file.read(num_bytes_to_read)
 1994:                     self._modify_connection_events(conn, selectors.EVENT_READ | selectors.EVENT_WRITE)
 1995: 
 1996:         except (OSError, ValueError) as error:
 1997:             events.emit_main_thread(
 1998:                 "upload-file-error",
 1999:                 username=conn.init.target_user, token=file_upload.token, error=error
 2000:             )
 2001:             return False  # Close the connection
 2002: 
 2003:         file_upload.speed += num_sent_bytes
 2004:         self._total_upload_bandwidth += num_sent_bytes
 2005: 
 2006:         # Upload finished
 2007:         if file_upload.offset + file_upload.sentbytes == size:
 2008:             events.emit_main_thread(
 2009:                 "file-upload-progress",
 2010:                 username=conn.init.target_user, token=file_upload.token,
 2011:                 offset=file_upload.offset, bytes_sent=file_upload.sentbytes
 2012:             )
 2013:         return True
```

### U-198 upload eligibility checks are path/database checks before later open

File: `pynicotine/uploads.py` lines approx 424-494

```python
  424: 
  425:         for failed_uploads in self.failed_users.copy().values():
  426:             for upload in failed_uploads.copy().values():
  427:                 if upload.status != TransferStatus.CONNECTION_TIMEOUT:
  428:                     continue
  429: 
  430:                 self._unfail_transfer(upload)
  431:                 self._enqueue_transfer(upload)
  432:                 self._update_transfer(upload)
  433: 
  434:     def _check_queue_upload_allowed(self, username, addr, virtual_path, real_path, msg):
  435: 
  436:         # Is user allowed to download?
  437:         ip_address, _port = addr
  438:         permission_level, reject_reason = core.shares.check_user_permission(username, ip_address)
  439:         size = None
  440: 
  441:         if permission_level == PermissionLevel.BANNED:
  442:             reject_message = TransferRejectReason.BANNED
  443: 
  444:             if reject_reason:
  445:                 reject_message += f" ({reject_reason})"
  446: 
  447:             return False, reject_message, size
  448: 
  449:         if core.shares.rescanning:
  450:             self._pending_network_msgs.append(msg)
  451:             return False, None, size
  452: 
  453:         # Is that file already in the queue?
  454:         if self.is_upload_queued(username, virtual_path):
  455:             return False, TransferRejectReason.QUEUED, size
  456: 
  457:         # Are we waiting for existing uploads to finish?
  458:         if self.pending_shutdown:
  459:             return False, TransferRejectReason.PENDING_SHUTDOWN, size
  460: 
  461:         # Has user hit queue limit?
  462:         enable_limits = True
  463: 
  464:         if config.sections["transfers"]["friendsnolimits"]:
  465:             if username in core.buddies.users:
  466:                 enable_limits = False
  467: 
  468:         if enable_limits:
  469:             limit_reached, reason = self.is_queue_limit_reached(username)
  470: 
  471:             if limit_reached:
  472:                 return False, reason, size
  473: 
  474:         is_file_shared, size = core.shares.file_is_shared(username, virtual_path, real_path)
  475: 
  476:         # Do we actually share that file with the world?
  477:         if not is_file_shared:
  478:             return False, TransferRejectReason.FILE_NOT_SHARED, size
  479: 
  480:         return True, None, size
  481: 
  482:     def _get_upload_candidate(self):
  483:         """Retrieve a suitable queued transfer for uploading.
  484: 
  485:         Round Robin: Get the first queued item from the oldest user
  486:         FIFO: Get the first queued item in the list
  487:         """
  488: 
  489:         is_fifo_queue = config.sections["transfers"]["fifoqueue"]
  490:         has_active_uploads = bool(self.active_users)
  491:         oldest_time = None
  492:         target_username = None
  493:         upload_candidate = None
  494:         privileged_users = set()
```

### U-198 queued upload rechecks readability/current path size before activation

File: `pynicotine/uploads.py` lines approx 170-565

```python
  170:         # All users
  171:         if config.sections["transfers"]["preferfriends"]:
  172:             return True
  173: 
  174:         # Only explicitly prioritized users
  175:         return bool(user_data.is_prioritized)
  176: 
  177:     # Stats/Limits #
  178: 
  179:     @staticmethod
  180:     def _get_current_file_size(file_path):
  181: 
  182:         try:
  183:             new_size = os.path.getsize(encode_path(file_path))
  184: 
  185:         except Exception:
  186:             new_size = None
  187: 
  188:         return new_size
  189: 
  190:     def get_downloading_users(self):
  191:         return set(self.active_users).union(self.queued_users)
  192: 
  193:     def get_total_uploads_allowed(self):
  194: 
  195:         if config.sections["transfers"]["useupslots"]:
  196:             upload_slots = config.sections["transfers"]["uploadslots"]
  197:         else:
  198:             upload_slots = len(self.active_users)
  199: 
  200:             if self.is_new_upload_accepted():
  201:                 return upload_slots + 1
  202: 
  203:         if upload_slots <= 0:
  204:             upload_slots = 1
  205: 
  206:         return upload_slots
  207: 
  208:     def get_upload_queue_size(self, username):
  209: 
  210:         if self.is_privileged(username):
  211:             return sum(
  212:                 len(queued_uploads)
  213:                 for username, queued_uploads in self.queued_users.items() if self.is_privileged(username)
  214:             )
  215: 
  216:         return len(self.queued_transfers)
  217: 
  218:     def has_active_uploads(self):
  219:         return bool(self.active_users or self.queued_users)
  220: 
  221:     def is_queue_limit_reached(self, username):
  222: 
  223:         file_limit = config.sections["transfers"]["filelimit"]
  224:         queue_size_limit = config.sections["transfers"]["queuelimit"] * 1024 * 1024
  225: 
  226:         if len(self.queued_users.get(username, {})) >= file_limit >= 1:
  227:             return True, TransferRejectReason.TOO_MANY_FILES
  228: 
  229:         if self._user_queue_sizes.get(username, 0) >= queue_size_limit >= 1:
  230:             return True, TransferRejectReason.TOO_MANY_MEGABYTES
  231: 
  232:         return False, None
  233: 
  234:     def is_slot_limit_reached(self):
  235: 
  236:         upload_slot_limit = config.sections["transfers"]["uploadslots"]
  237: 
  238:         if upload_slot_limit <= 0:
  239:             upload_slot_limit = 1
  240: 
  241:         return len(self.active_users) >= upload_slot_limit
  242: 
  243:     def is_bandwidth_limit_reached(self):
  244: 
  245:         bandwidth_limit = config.sections["transfers"]["uploadbandwidth"] * 1024
  246: 
  247:         if not bandwidth_limit:
  248:             return False
  249: 
  250:         return self.total_bandwidth >= bandwidth_limit
  251: 
  252:     def is_new_upload_accepted(self, enforce_limits=True):
  253: 
  254:         if core.shares is None or core.shares.rescanning:
  255:             return False
  256: 
  257:         if not enforce_limits:
  258:             return True
  259: 
  260:         if config.sections["transfers"]["useupslots"]:
  261:             # Limit by upload slots
  262:             if self.is_slot_limit_reached():
  263:                 return False
  264: 
  265:         elif self.is_bandwidth_limit_reached():
  266:             # Limit by maximum bandwidth
  267:             return False
  268: 
  269:         # No limits
  270:         return True
  271: 
  272:     @staticmethod
  273:     def is_file_readable(virtual_path, real_path):
  274: 
  275:         try:
  276:             if os.access(encode_path(real_path), os.R_OK):
  277:                 return True
  278: 
  279:             log.add_transfer("Cannot access file, not sharing: %s with real path %s",
  280:                              (virtual_path, real_path))
  281: 
  282:         except Exception:
  283:             log.add_transfer("Requested file path contains invalid characters or other errors, not sharing: "
  284:                              "%s with real path %s", (virtual_path, real_path))
  285: 
  286:         return False
  287: 
  288:     def is_upload_queued(self, username, virtual_path):
  289: 
  290:         if virtual_path in self.queued_users.get(username, {}):
  291:             return True
  292: 
  293:         return any(upload.virtual_path == virtual_path for upload in self.active_users.get(username, {}).values())
  294: 
  295:     def update_transfer_limits(self):
  296: 
  297:         events.emit("update-upload-limits")
  298: 
  299:         use_speed_limit = config.sections["transfers"]["use_upload_speed_limit"]
  300:         limit_by = config.sections["transfers"]["limitby"]
  301: 
  302:         if use_speed_limit == "primary":
  303:             speed_limit = config.sections["transfers"]["uploadlimit"]
  304: 
  305:         elif use_speed_limit == "alternative":
  306:             speed_limit = config.sections["transfers"]["uploadlimitalt"]
  307: 
  308:         else:
  309:             speed_limit = 0
  310: 
  311:         core.send_message_to_network_thread(SetUploadLimit(speed_limit, limit_by))
  312:         self._check_upload_queue()
  313: 
  314:     # Transfer Actions #
  315: 
  316:     def _enqueue_transfer(self, transfer):
  317: 
  318:         username = transfer.username
  319: 
  320:         super()._enqueue_transfer(transfer)
  321: 
  322:         if self.is_privileged(username):
  323:             transfer.modifier = "privileged" if username in core.users.privileged else "prioritized"
  324: 
  325:         # Clear queue position cache until next position request
  326:         self._queue_positions.clear()
  327:         self._queue_position_users.pop(username, None)
  328: 
  329:         return True
  330: 
  331:     def _dequeue_transfer(self, transfer):
  332: 
  333:         username = transfer.username
  334: 
  335:         if not super()._dequeue_transfer(transfer):
  336:             return False
  337: 
  338:         if username not in self.queued_users:
  339:             self._user_update_counters.pop(username, None)
  340: 
  341:         transfer.modifier = None
  342: 
  343:         # Clear queue position cache until next position request
  344:         self._queue_positions.clear()
  345:         self._queue_position_users.pop(username, None)
  346: 
  347:         return True
  348: 
  349:     def _activate_transfer(self, transfer, token):
  350:         super()._activate_transfer(transfer, token)
  351:         self._user_update_counters.pop(transfer.username, None)
  352: 
  353:     def _update_transfer(self, transfer, update_parent=True):
  354: 
  355:         username = transfer.username
  356: 
  357:         # Don't update existing user counter for queued uploads
  358:         # We don't want to push the user back in the queue if they enqueued new files
  359:         if (username not in self._user_update_counters
  360:                 or transfer.virtual_path not in self.queued_users.get(username, {})):
  361:             self._update_user_counter(username)
  362: 
  363:         events.emit("update-upload", transfer, update_parent)
  364: 
  365:     def _finish_transfer(self, transfer, already_exists=False):
  366: 
  367:         username = transfer.username
  368:         virtual_path = transfer.virtual_path
  369: 
  370:         super()._finish_transfer(transfer)
  371: 
  372:         if not self._auto_clear_transfer(transfer):
  373:             self._update_transfer(transfer)
  374: 
  375:         if not already_exists:
  376:             core.statistics.append_stat_value("completed_uploads", 1)
  377: 
  378:             real_path = core.shares.virtual2real(virtual_path)
  379:             core.pluginhandler.upload_finished_notification(username, virtual_path, real_path)
  380: 
  381:             log.add_upload(
  382:                 _("Upload finished: user %(user)s, IP address %(ip)s, file %(file)s"), {
  383:                     "user": username,
  384:                     "ip": core.users.addresses.get(username),
  385:                     "file": virtual_path
  386:                 }
  387:             )
  388: 
  389:         self._check_upload_queue()
  390: 
  391:     def _abort_transfer(self, transfer, status=None, denied_message=None, update_parent=True):
  392: 
  393:         if transfer.file_handle is not None:
  394:             log.add_upload(
  395:                 _("Upload aborted, user %(user)s file %(file)s"), {
  396:                     "user": transfer.username,
  397:                     "file": transfer.virtual_path
  398:                 }
  399:             )
  400: 
  401:         super()._abort_transfer(transfer, status=status, denied_message=denied_message)
  402:         self._update_user_counter(transfer.username)
  403: 
  404:         if status:
  405:             events.emit("abort-upload", transfer, status, update_parent)
  406: 
  407:     def _clear_transfer(self, transfer, denied_message=None, update_parent=True):
  408: 
  409:         virtual_path = transfer.virtual_path
  410:         username = transfer.username
  411: 
  412:         log.add_transfer("Clearing upload %s to user %s", (virtual_path, username))
  413: 
  414:         try:
  415:             super()._clear_transfer(transfer, denied_message=denied_message)
  416: 
  417:         except KeyError:
  418:             log.add("FIXME: failed to remove upload %s to user %s, not present in list",
  419:                     (virtual_path, username))
  420: 
  421:         events.emit("clear-upload", transfer, update_parent)
  422: 
  423:     def _retry_failed_uploads(self):
  424: 
  425:         for failed_uploads in self.failed_users.copy().values():
  426:             for upload in failed_uploads.copy().values():
  427:                 if upload.status != TransferStatus.CONNECTION_TIMEOUT:
  428:                     continue
  429: 
  430:                 self._unfail_transfer(upload)
  431:                 self._enqueue_transfer(upload)
  432:                 self._update_transfer(upload)
  433: 
  434:     def _check_queue_upload_allowed(self, username, addr, virtual_path, real_path, msg):
  435: 
  436:         # Is user allowed to download?
  437:         ip_address, _port = addr
  438:         permission_level, reject_reason = core.shares.check_user_permission(username, ip_address)
  439:         size = None
  440: 
  441:         if permission_level == PermissionLevel.BANNED:
  442:             reject_message = TransferRejectReason.BANNED
  443: 
  444:             if reject_reason:
  445:                 reject_message += f" ({reject_reason})"
  446: 
  447:             return False, reject_message, size
  448: 
  449:         if core.shares.rescanning:
  450:             self._pending_network_msgs.append(msg)
  451:             return False, None, size
  452: 
  453:         # Is that file already in the queue?
  454:         if self.is_upload_queued(username, virtual_path):
  455:             return False, TransferRejectReason.QUEUED, size
  456: 
  457:         # Are we waiting for existing uploads to finish?
  458:         if self.pending_shutdown:
  459:             return False, TransferRejectReason.PENDING_SHUTDOWN, size
  460: 
  461:         # Has user hit queue limit?
  462:         enable_limits = True
  463: 
  464:         if config.sections["transfers"]["friendsnolimits"]:
  465:             if username in core.buddies.users:
  466:                 enable_limits = False
  467: 
  468:         if enable_limits:
  469:             limit_reached, reason = self.is_queue_limit_reached(username)
  470: 
  471:             if limit_reached:
  472:                 return False, reason, size
  473: 
  474:         is_file_shared, size = core.shares.file_is_shared(username, virtual_path, real_path)
  475: 
  476:         # Do we actually share that file with the world?
  477:         if not is_file_shared:
  478:             return False, TransferRejectReason.FILE_NOT_SHARED, size
  479: 
  480:         return True, None, size
  481: 
  482:     def _get_upload_candidate(self):
  483:         """Retrieve a suitable queued transfer for uploading.
  484: 
  485:         Round Robin: Get the first queued item from the oldest user
  486:         FIFO: Get the first queued item in the list
  487:         """
  488: 
  489:         is_fifo_queue = config.sections["transfers"]["fifoqueue"]
  490:         has_active_uploads = bool(self.active_users)
  491:         oldest_time = None
  492:         target_username = None
  493:         upload_candidate = None
  494:         privileged_users = set()
  495: 
  496:         if not self._user_update_counters:
  497:             # No queued uploads to start right now
  498:             return upload_candidate, has_active_uploads
  499: 
  500:         for username in self._user_update_counters:
  501:             if self.is_privileged(username):
  502:                 privileged_users.add(username)
  503: 
  504:         if is_fifo_queue:
  505:             for upload in self.queued_transfers:
  506:                 username = upload.username
  507: 
  508:                 if privileged_users and username not in privileged_users:
  509:                     continue
  510: 
  511:                 if username not in self._user_update_counters:
  512:                     continue
  513: 
  514:                 target_username = username
  515:                 break
  516:         else:
  517:             for username, update_time in self._user_update_counters.items():
  518:                 if privileged_users and username not in privileged_users:
  519:                     continue
  520: 
  521:                 if not oldest_time:
  522:                     oldest_time = update_time + 1
  523: 
  524:                 if update_time < oldest_time:
  525:                     target_username = username
  526:                     oldest_time = update_time
  527: 
  528:         if target_username is not None:
  529:             upload_candidate = next(iter(self.queued_users[target_username].values()), None)
  530: 
  531:         return upload_candidate, has_active_uploads
  532: 
  533:     def _update_user_counter(self, username):
  534:         """Called when an upload associated with a user has changed.
  535: 
  536:         The user update counter is used by the Round Robin queue system
  537:         to determine which user has waited the longest since their last
  538:         download.
  539:         """
  540: 
  541:         if username in self.queued_users and username not in self.active_users:
  542:             self._user_update_counter += 1
  543:             self._user_update_counters[username] = self._user_update_counter
  544: 
  545:     def _check_upload_queue(self, upload_candidate=None):
  546:         """Find next file to upload."""
  547: 
  548:         final_upload_candidate = None
  549: 
  550:         while final_upload_candidate is None:
  551:             # If a candidate is provided, we want to upload it immediately
  552:             if not self.is_new_upload_accepted(enforce_limits=(upload_candidate is None)):
  553:                 return
  554: 
  555:             if upload_candidate is None:
  556:                 upload_candidate, has_active_uploads = self._get_upload_candidate()
  557: 
  558:                 if upload_candidate is None:
  559:                     if not has_active_uploads and self.pending_shutdown:
  560:                         self.pending_shutdown = False
  561:                         core.quit()
  562:                     return
  563: 
  564:             elif upload_candidate not in self.queued_users.get(upload_candidate.username, {}).values():
  565:                 return
```

### U-198 F-connection opens current path and emits UploadFile with stored size

File: `pynicotine/uploads.py` lines approx 1056-1132

```python
 1056:             status = TransferStatus.CANCELLED
 1057:             error = f"Remote client does not support large file transfers: {error}"
 1058:         else:
 1059:             status = TransferStatus.LOCAL_FILE_ERROR
 1060: 
 1061:         self._abort_transfer(upload, status=status)
 1062: 
 1063:         log.add(_("Upload I/O error: %s"), error)
 1064:         self._check_upload_queue()
 1065: 
 1066:     def _file_transfer_init(self, msg):
 1067:         """We are requesting to start uploading a file to a peer."""
 1068: 
 1069:         username = msg.username
 1070:         token = msg.token
 1071:         upload = self.active_users.get(username, {}).get(token)
 1072: 
 1073:         if upload is None or upload.sock is not None:
 1074:             return
 1075: 
 1076:         virtual_path = upload.virtual_path
 1077:         sock = upload.sock = msg.sock
 1078:         need_update = True
 1079:         upload_started = False
 1080: 
 1081:         log.add_transfer("Initializing upload with token %s for file %s to user %s",
 1082:                          (token, virtual_path, username))
 1083: 
 1084:         real_path = core.shares.virtual2real(virtual_path)
 1085: 
 1086:         try:
 1087:             # Open File
 1088:             file_handle = open(encode_path(real_path), "rb")  # pylint: disable=consider-using-with
 1089: 
 1090:         except OSError as error:
 1091:             log.add(_("Upload I/O error: %s"), error)
 1092:             self._abort_transfer(upload, status=TransferStatus.LOCAL_FILE_ERROR)
 1093:             self._check_upload_queue()
 1094: 
 1095:         else:
 1096:             upload.file_handle = file_handle
 1097:             upload.start_time = time.monotonic() - upload.time_elapsed
 1098: 
 1099:             core.statistics.append_stat_value("started_uploads", 1)
 1100:             upload_started = True
 1101: 
 1102:             log.add_upload(
 1103:                 _("Upload started: user %(user)s, IP address %(ip)s, file %(file)s"), {
 1104:                     "user": username,
 1105:                     "ip": core.users.addresses.get(username),
 1106:                     "file": virtual_path
 1107:                 }
 1108:             )
 1109: 
 1110:             if upload.size > 0:
 1111:                 upload.status = TransferStatus.TRANSFERRING
 1112:                 core.send_message_to_network_thread(UploadFile(
 1113:                     sock=sock, token=token, file=file_handle, size=upload.size
 1114:                 ))
 1115: 
 1116:             else:
 1117:                 self._finish_transfer(upload)
 1118:                 need_update = False
 1119: 
 1120:         if need_update:
 1121:             self._update_transfer(upload)
 1122: 
 1123:         if upload_started:
 1124:             # Must be be emitted after the final update to prevent inconsistent state
 1125:             core.pluginhandler.upload_started_notification(username, virtual_path, real_path)
 1126: 
 1127:     def _file_upload_progress(self, username, token, offset, bytes_sent, speed=None):
 1128:         """A file upload is in progress."""
 1129: 
 1130:         upload = self.active_users.get(username, {}).get(token)
 1131: 
 1132:         if upload is None:
```

### U-198 share DB path membership check

File: `pynicotine/shares.py` lines approx 830-872

```python
  830:                 share_dbs[destination] = Database(encode_path(db_path), overwrite=False)
  831: 
  832:             except Exception as error:
  833:                 exception = error
  834:                 cls.remove_db_file(db_path)
  835: 
  836:         if exception:
  837:             cls.close_shares(share_dbs)
  838:             raise exception
  839: 
  840:     def file_is_shared(self, username, virtual_path, real_path):
  841: 
  842:         log.add_transfer("Checking if file is shared: %s with real path %s",
  843:                          (virtual_path, real_path))
  844: 
  845:         public_shared_files = self.share_dbs.get("public_files")
  846:         buddy_shared_files = self.share_dbs.get("buddy_files")
  847:         trusted_shared_files = self.share_dbs.get("trusted_files")
  848:         file_is_shared = False
  849:         size = None
  850: 
  851:         if not real_path.startswith("__INVALID_SHARE__"):
  852:             if public_shared_files is not None and real_path in public_shared_files:
  853:                 file_is_shared = True
  854:                 _file_name, size, *_unused = public_shared_files[real_path]
  855: 
  856:             elif (buddy_shared_files is not None and username in core.buddies.users
  857:                     and real_path in buddy_shared_files):
  858:                 file_is_shared = True
  859:                 _file_name, size, *_unused = buddy_shared_files[real_path]
  860: 
  861:             elif trusted_shared_files is not None:
  862:                 user_data = core.buddies.users.get(username)
  863: 
  864:                 if user_data and user_data.is_trusted and real_path in trusted_shared_files:
  865:                     file_is_shared = True
  866:                     _file_name, size, *_unused = trusted_shared_files[real_path]
  867: 
  868:         if not file_is_shared:
  869:             log.add_transfer("File is not present in the database of shared files, not sharing: "
  870:                              "%s with real path %s", (virtual_path, real_path))
  871:             return False, size
  872: 
```

## github-branch-3.3.x

### U-69 queued-download size mutation from peer TransferRequest

File: `pynicotine/downloads.py` lines approx 1064-1123

```python
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
```

### U-69 F-connection leftbytes uses mutated download.size

File: `pynicotine/downloads.py` lines approx 1091-1262

```python
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
 1258: 
 1259:     def _upload_denied(self, msg):
 1260:         """Peer code 50."""
 1261: 
 1262:         username = msg.username
```

### U-107 network upload read not clamped to remaining advertised size

File: `pynicotine/slskproto.py` lines approx 2048-2098

```python
 2048:         if file_download.leftbytes <= 0:
 2049:             events.emit_main_thread(
 2050:                 "file-download-progress",
 2051:                 username=conn.init.target_user, token=file_download.token,
 2052:                 bytes_left=file_download.leftbytes
 2053:             )
 2054:             return False  # Close the connection
 2055: 
 2056:         return True
 2057: 
 2058:     def _process_upload(self, conn, num_sent_bytes, current_time):
 2059: 
 2060:         file_upload = self._file_upload_msgs[conn]
 2061: 
 2062:         if file_upload.offset is None:
 2063:             return True
 2064: 
 2065:         out_buffer = conn.out_buffer
 2066:         out_buffer_len = len(out_buffer)
 2067:         file_upload.sentbytes += num_sent_bytes
 2068:         total_read_bytes = file_upload.offset + file_upload.sentbytes + out_buffer_len
 2069:         size = file_upload.size
 2070: 
 2071:         try:
 2072:             if total_read_bytes < size:
 2073:                 num_bytes_to_read = int(
 2074:                     (max(4096, num_sent_bytes * 1.25) / max(1, current_time - conn.last_active))
 2075:                     - out_buffer_len
 2076:                 )
 2077:                 if num_bytes_to_read > 0:
 2078:                     out_buffer += file_upload.file.read(num_bytes_to_read)
 2079:                     self._modify_connection_events(conn, selectors.EVENT_READ | selectors.EVENT_WRITE)
 2080: 
 2081:         except (OSError, ValueError) as error:
 2082:             events.emit_main_thread(
 2083:                 "upload-file-error",
 2084:                 username=conn.init.target_user, token=file_upload.token, error=error
 2085:             )
 2086:             return False  # Close the connection
 2087: 
 2088:         file_upload.speed += num_sent_bytes
 2089:         self._total_upload_bandwidth += num_sent_bytes
 2090: 
 2091:         # Upload finished
 2092:         if file_upload.offset + file_upload.sentbytes == size:
 2093:             events.emit_main_thread(
 2094:                 "file-upload-progress",
 2095:                 username=conn.init.target_user, token=file_upload.token,
 2096:                 offset=file_upload.offset, bytes_sent=file_upload.sentbytes
 2097:             )
 2098:         return True
```

### U-198 upload eligibility checks are path/database checks before later open

File: `pynicotine/uploads.py` lines approx 425-495

```python
  425: 
  426:         for failed_uploads in self.failed_users.copy().values():
  427:             for upload in failed_uploads.copy().values():
  428:                 if upload.status != TransferStatus.CONNECTION_TIMEOUT:
  429:                     continue
  430: 
  431:                 self._unfail_transfer(upload)
  432:                 self._enqueue_transfer(upload)
  433:                 self._update_transfer(upload)
  434: 
  435:     def _check_queue_upload_allowed(self, username, addr, virtual_path, real_path, msg):
  436: 
  437:         # Is user allowed to download?
  438:         ip_address, _port = addr
  439:         permission_level, reject_reason = core.shares.check_user_permission(username, ip_address)
  440:         size = None
  441: 
  442:         if permission_level == PermissionLevel.BANNED:
  443:             reject_message = TransferRejectReason.BANNED
  444: 
  445:             if reject_reason:
  446:                 reject_message += f" ({reject_reason})"
  447: 
  448:             return False, reject_message, size
  449: 
  450:         if core.shares.rescanning:
  451:             self._pending_network_msgs.append(msg)
  452:             return False, None, size
  453: 
  454:         # Is that file already in the queue?
  455:         if self.is_upload_queued(username, virtual_path):
  456:             return False, TransferRejectReason.QUEUED, size
  457: 
  458:         # Are we waiting for existing uploads to finish?
  459:         if self.pending_shutdown:
  460:             return False, TransferRejectReason.PENDING_SHUTDOWN, size
  461: 
  462:         # Has user hit queue limit?
  463:         enable_limits = True
  464: 
  465:         if config.sections["transfers"]["friendsnolimits"]:
  466:             if username in core.buddies.users:
  467:                 enable_limits = False
  468: 
  469:         if enable_limits:
  470:             limit_reached, reason = self.is_queue_limit_reached(username)
  471: 
  472:             if limit_reached:
  473:                 return False, reason, size
  474: 
  475:         is_file_shared, size = core.shares.file_is_shared(username, virtual_path, real_path)
  476: 
  477:         # Do we actually share that file with the world?
  478:         if not is_file_shared:
  479:             return False, TransferRejectReason.FILE_NOT_SHARED, size
  480: 
  481:         return True, None, size
  482: 
  483:     def _get_upload_candidate(self):
  484:         """Retrieve a suitable queued transfer for uploading.
  485: 
  486:         Round Robin: Get the first queued item from the oldest user
  487:         FIFO: Get the first queued item in the list
  488:         """
  489: 
  490:         is_fifo_queue = config.sections["transfers"]["fifoqueue"]
  491:         has_active_uploads = bool(self.active_users)
  492:         oldest_time = None
  493:         target_username = None
  494:         upload_candidate = None
  495:         privileged_users = set()
```

### U-198 queued upload rechecks readability/current path size before activation

File: `pynicotine/uploads.py` lines approx 171-566

```python
  171:         # All users
  172:         if config.sections["transfers"]["preferfriends"]:
  173:             return True
  174: 
  175:         # Only explicitly prioritized users
  176:         return bool(user_data.is_prioritized)
  177: 
  178:     # Stats/Limits #
  179: 
  180:     @staticmethod
  181:     def _get_current_file_size(file_path):
  182: 
  183:         try:
  184:             new_size = os.path.getsize(encode_path(file_path))
  185: 
  186:         except Exception:
  187:             new_size = None
  188: 
  189:         return new_size
  190: 
  191:     def get_downloading_users(self):
  192:         return set(self.active_users).union(self.queued_users)
  193: 
  194:     def get_total_uploads_allowed(self):
  195: 
  196:         if config.sections["transfers"]["useupslots"]:
  197:             upload_slots = config.sections["transfers"]["uploadslots"]
  198:         else:
  199:             upload_slots = len(self.active_users)
  200: 
  201:             if self.is_new_upload_accepted():
  202:                 return upload_slots + 1
  203: 
  204:         if upload_slots <= 0:
  205:             upload_slots = 1
  206: 
  207:         return upload_slots
  208: 
  209:     def get_upload_queue_size(self, username):
  210: 
  211:         if self.is_privileged(username):
  212:             return sum(
  213:                 len(queued_uploads)
  214:                 for username, queued_uploads in self.queued_users.items() if self.is_privileged(username)
  215:             )
  216: 
  217:         return len(self.queued_transfers)
  218: 
  219:     def has_active_uploads(self):
  220:         return bool(self.active_users or self.queued_users)
  221: 
  222:     def is_queue_limit_reached(self, username):
  223: 
  224:         file_limit = config.sections["transfers"]["filelimit"]
  225:         queue_size_limit = config.sections["transfers"]["queuelimit"] * 1024 * 1024
  226: 
  227:         if len(self.queued_users.get(username, {})) >= file_limit >= 1:
  228:             return True, TransferRejectReason.TOO_MANY_FILES
  229: 
  230:         if self._user_queue_sizes.get(username, 0) >= queue_size_limit >= 1:
  231:             return True, TransferRejectReason.TOO_MANY_MEGABYTES
  232: 
  233:         return False, None
  234: 
  235:     def is_slot_limit_reached(self):
  236: 
  237:         upload_slot_limit = config.sections["transfers"]["uploadslots"]
  238: 
  239:         if upload_slot_limit <= 0:
  240:             upload_slot_limit = 1
  241: 
  242:         return len(self.active_users) >= upload_slot_limit
  243: 
  244:     def is_bandwidth_limit_reached(self):
  245: 
  246:         bandwidth_limit = config.sections["transfers"]["uploadbandwidth"] * 1024
  247: 
  248:         if not bandwidth_limit:
  249:             return False
  250: 
  251:         return self.total_bandwidth >= bandwidth_limit
  252: 
  253:     def is_new_upload_accepted(self, enforce_limits=True):
  254: 
  255:         if core.shares is None or core.shares.rescanning:
  256:             return False
  257: 
  258:         if not enforce_limits:
  259:             return True
  260: 
  261:         if config.sections["transfers"]["useupslots"]:
  262:             # Limit by upload slots
  263:             if self.is_slot_limit_reached():
  264:                 return False
  265: 
  266:         elif self.is_bandwidth_limit_reached():
  267:             # Limit by maximum bandwidth
  268:             return False
  269: 
  270:         # No limits
  271:         return True
  272: 
  273:     @staticmethod
  274:     def is_file_readable(virtual_path, real_path):
  275: 
  276:         try:
  277:             if os.access(encode_path(real_path), os.R_OK):
  278:                 return True
  279: 
  280:             log.add_transfer("Cannot access file, not sharing: %s with real path %s",
  281:                              (virtual_path, real_path))
  282: 
  283:         except Exception:
  284:             log.add_transfer("Requested file path contains invalid characters or other errors, not sharing: "
  285:                              "%s with real path %s", (virtual_path, real_path))
  286: 
  287:         return False
  288: 
  289:     def is_upload_queued(self, username, virtual_path):
  290: 
  291:         if virtual_path in self.queued_users.get(username, {}):
  292:             return True
  293: 
  294:         return any(upload.virtual_path == virtual_path for upload in self.active_users.get(username, {}).values())
  295: 
  296:     def update_transfer_limits(self):
  297: 
  298:         events.emit("update-upload-limits")
  299: 
  300:         use_speed_limit = config.sections["transfers"]["use_upload_speed_limit"]
  301:         limit_by = config.sections["transfers"]["limitby"]
  302: 
  303:         if use_speed_limit == "primary":
  304:             speed_limit = config.sections["transfers"]["uploadlimit"]
  305: 
  306:         elif use_speed_limit == "alternative":
  307:             speed_limit = config.sections["transfers"]["uploadlimitalt"]
  308: 
  309:         else:
  310:             speed_limit = 0
  311: 
  312:         core.send_message_to_network_thread(SetUploadLimit(speed_limit, limit_by))
  313:         self._check_upload_queue()
  314: 
  315:     # Transfer Actions #
  316: 
  317:     def _enqueue_transfer(self, transfer):
  318: 
  319:         username = transfer.username
  320: 
  321:         super()._enqueue_transfer(transfer)
  322: 
  323:         if self.is_privileged(username):
  324:             transfer.modifier = "privileged" if username in core.users.privileged else "prioritized"
  325: 
  326:         # Clear queue position cache until next position request
  327:         self._queue_positions.clear()
  328:         self._queue_position_users.pop(username, None)
  329: 
  330:         return True
  331: 
  332:     def _dequeue_transfer(self, transfer):
  333: 
  334:         username = transfer.username
  335: 
  336:         if not super()._dequeue_transfer(transfer):
  337:             return False
  338: 
  339:         if username not in self.queued_users:
  340:             self._user_update_counters.pop(username, None)
  341: 
  342:         transfer.modifier = None
  343: 
  344:         # Clear queue position cache until next position request
  345:         self._queue_positions.clear()
  346:         self._queue_position_users.pop(username, None)
  347: 
  348:         return True
  349: 
  350:     def _activate_transfer(self, transfer, token):
  351:         super()._activate_transfer(transfer, token)
  352:         self._user_update_counters.pop(transfer.username, None)
  353: 
  354:     def _update_transfer(self, transfer, update_parent=True):
  355: 
  356:         username = transfer.username
  357: 
  358:         # Don't update existing user counter for queued uploads
  359:         # We don't want to push the user back in the queue if they enqueued new files
  360:         if (username not in self._user_update_counters
  361:                 or transfer.virtual_path not in self.queued_users.get(username, {})):
  362:             self._update_user_counter(username)
  363: 
  364:         events.emit("update-upload", transfer, update_parent)
  365: 
  366:     def _finish_transfer(self, transfer, already_exists=False):
  367: 
  368:         username = transfer.username
  369:         virtual_path = transfer.virtual_path
  370: 
  371:         super()._finish_transfer(transfer)
  372: 
  373:         if not self._auto_clear_transfer(transfer):
  374:             self._update_transfer(transfer)
  375: 
  376:         if not already_exists:
  377:             core.statistics.append_stat_value("completed_uploads", 1)
  378: 
  379:             real_path = core.shares.virtual2real(virtual_path)
  380:             core.pluginhandler.upload_finished_notification(username, virtual_path, real_path)
  381: 
  382:             log.add_upload(
  383:                 _("Upload finished: user %(user)s, IP address %(ip)s, file %(file)s"), {
  384:                     "user": username,
  385:                     "ip": core.users.addresses.get(username),
  386:                     "file": virtual_path
  387:                 }
  388:             )
  389: 
  390:         self._check_upload_queue()
  391: 
  392:     def _abort_transfer(self, transfer, status=None, denied_message=None, update_parent=True):
  393: 
  394:         if transfer.file_handle is not None:
  395:             log.add_upload(
  396:                 _("Upload aborted, user %(user)s file %(file)s"), {
  397:                     "user": transfer.username,
  398:                     "file": transfer.virtual_path
  399:                 }
  400:             )
  401: 
  402:         super()._abort_transfer(transfer, status=status, denied_message=denied_message)
  403:         self._update_user_counter(transfer.username)
  404: 
  405:         if status:
  406:             events.emit("abort-upload", transfer, status, update_parent)
  407: 
  408:     def _clear_transfer(self, transfer, denied_message=None, update_parent=True):
  409: 
  410:         virtual_path = transfer.virtual_path
  411:         username = transfer.username
  412: 
  413:         log.add_transfer("Clearing upload %s to user %s", (virtual_path, username))
  414: 
  415:         try:
  416:             super()._clear_transfer(transfer, denied_message=denied_message)
  417: 
  418:         except KeyError:
  419:             log.add("FIXME: failed to remove upload %s to user %s, not present in list",
  420:                     (virtual_path, username))
  421: 
  422:         events.emit("clear-upload", transfer, update_parent)
  423: 
  424:     def _retry_failed_uploads(self):
  425: 
  426:         for failed_uploads in self.failed_users.copy().values():
  427:             for upload in failed_uploads.copy().values():
  428:                 if upload.status != TransferStatus.CONNECTION_TIMEOUT:
  429:                     continue
  430: 
  431:                 self._unfail_transfer(upload)
  432:                 self._enqueue_transfer(upload)
  433:                 self._update_transfer(upload)
  434: 
  435:     def _check_queue_upload_allowed(self, username, addr, virtual_path, real_path, msg):
  436: 
  437:         # Is user allowed to download?
  438:         ip_address, _port = addr
  439:         permission_level, reject_reason = core.shares.check_user_permission(username, ip_address)
  440:         size = None
  441: 
  442:         if permission_level == PermissionLevel.BANNED:
  443:             reject_message = TransferRejectReason.BANNED
  444: 
  445:             if reject_reason:
  446:                 reject_message += f" ({reject_reason})"
  447: 
  448:             return False, reject_message, size
  449: 
  450:         if core.shares.rescanning:
  451:             self._pending_network_msgs.append(msg)
  452:             return False, None, size
  453: 
  454:         # Is that file already in the queue?
  455:         if self.is_upload_queued(username, virtual_path):
  456:             return False, TransferRejectReason.QUEUED, size
  457: 
  458:         # Are we waiting for existing uploads to finish?
  459:         if self.pending_shutdown:
  460:             return False, TransferRejectReason.PENDING_SHUTDOWN, size
  461: 
  462:         # Has user hit queue limit?
  463:         enable_limits = True
  464: 
  465:         if config.sections["transfers"]["friendsnolimits"]:
  466:             if username in core.buddies.users:
  467:                 enable_limits = False
  468: 
  469:         if enable_limits:
  470:             limit_reached, reason = self.is_queue_limit_reached(username)
  471: 
  472:             if limit_reached:
  473:                 return False, reason, size
  474: 
  475:         is_file_shared, size = core.shares.file_is_shared(username, virtual_path, real_path)
  476: 
  477:         # Do we actually share that file with the world?
  478:         if not is_file_shared:
  479:             return False, TransferRejectReason.FILE_NOT_SHARED, size
  480: 
  481:         return True, None, size
  482: 
  483:     def _get_upload_candidate(self):
  484:         """Retrieve a suitable queued transfer for uploading.
  485: 
  486:         Round Robin: Get the first queued item from the oldest user
  487:         FIFO: Get the first queued item in the list
  488:         """
  489: 
  490:         is_fifo_queue = config.sections["transfers"]["fifoqueue"]
  491:         has_active_uploads = bool(self.active_users)
  492:         oldest_time = None
  493:         target_username = None
  494:         upload_candidate = None
  495:         privileged_users = set()
  496: 
  497:         if not self._user_update_counters:
  498:             # No queued uploads to start right now
  499:             return upload_candidate, has_active_uploads
  500: 
  501:         for username in self._user_update_counters:
  502:             if self.is_privileged(username):
  503:                 privileged_users.add(username)
  504: 
  505:         if is_fifo_queue:
  506:             for upload in self.queued_transfers:
  507:                 username = upload.username
  508: 
  509:                 if privileged_users and username not in privileged_users:
  510:                     continue
  511: 
  512:                 if username not in self._user_update_counters:
  513:                     continue
  514: 
  515:                 target_username = username
  516:                 break
  517:         else:
  518:             for username, update_time in self._user_update_counters.items():
  519:                 if privileged_users and username not in privileged_users:
  520:                     continue
  521: 
  522:                 if not oldest_time:
  523:                     oldest_time = update_time + 1
  524: 
  525:                 if update_time < oldest_time:
  526:                     target_username = username
  527:                     oldest_time = update_time
  528: 
  529:         if target_username is not None:
  530:             upload_candidate = next(iter(self.queued_users[target_username].values()), None)
  531: 
  532:         return upload_candidate, has_active_uploads
  533: 
  534:     def _update_user_counter(self, username):
  535:         """Called when an upload associated with a user has changed.
  536: 
  537:         The user update counter is used by the Round Robin queue system
  538:         to determine which user has waited the longest since their last
  539:         download.
  540:         """
  541: 
  542:         if username in self.queued_users and username not in self.active_users:
  543:             self._user_update_counter += 1
  544:             self._user_update_counters[username] = self._user_update_counter
  545: 
  546:     def _check_upload_queue(self, upload_candidate=None):
  547:         """Find next file to upload."""
  548: 
  549:         final_upload_candidate = None
  550: 
  551:         while final_upload_candidate is None:
  552:             # If a candidate is provided, we want to upload it immediately
  553:             if not self.is_new_upload_accepted(enforce_limits=(upload_candidate is None)):
  554:                 return
  555: 
  556:             if upload_candidate is None:
  557:                 upload_candidate, has_active_uploads = self._get_upload_candidate()
  558: 
  559:                 if upload_candidate is None:
  560:                     if not has_active_uploads and self.pending_shutdown:
  561:                         self.pending_shutdown = False
  562:                         core.quit()
  563:                     return
  564: 
  565:             elif upload_candidate not in self.queued_users.get(upload_candidate.username, {}).values():
  566:                 return
```

### U-198 F-connection opens current path and emits UploadFile with stored size

File: `pynicotine/uploads.py` lines approx 1038-1120

```python
 1038:             status = TransferStatus.CANCELLED
 1039:             error = f"Remote client does not support large file transfers: {error}"
 1040:         else:
 1041:             status = TransferStatus.LOCAL_FILE_ERROR
 1042: 
 1043:         self._abort_transfer(upload, status=status)
 1044: 
 1045:         log.add(_("Upload I/O error: %s"), error)
 1046:         self._check_upload_queue()
 1047: 
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
 1063: 
 1064:         virtual_path = upload.virtual_path
 1065:         sock = upload.sock = msg.sock
 1066:         need_update = True
 1067:         upload_started = False
 1068: 
 1069:         log.add_transfer("Initializing upload with token %s for file %s to user %s",
 1070:                          (token, virtual_path, username))
 1071: 
 1072:         real_path = core.shares.virtual2real(virtual_path)
 1073: 
 1074:         try:
 1075:             # Open File
 1076:             file_handle = open(encode_path(real_path), "rb")  # pylint: disable=consider-using-with
 1077: 
 1078:         except OSError as error:
 1079:             log.add(_("Upload I/O error: %s"), error)
 1080:             self._abort_transfer(upload, status=TransferStatus.LOCAL_FILE_ERROR)
 1081:             self._check_upload_queue()
 1082: 
 1083:         else:
 1084:             upload.file_handle = file_handle
 1085:             upload.start_time = time.monotonic() - upload.time_elapsed
 1086: 
 1087:             core.statistics.append_stat_value("started_uploads", 1)
 1088:             upload_started = True
 1089: 
 1090:             log.add_upload(
 1091:                 _("Upload started: user %(user)s, IP address %(ip)s, file %(file)s"), {
 1092:                     "user": username,
 1093:                     "ip": core.users.addresses.get(username),
 1094:                     "file": virtual_path
 1095:                 }
 1096:             )
 1097: 
 1098:             if upload.size > 0:
 1099:                 upload.status = TransferStatus.TRANSFERRING
 1100:                 core.send_message_to_network_thread(UploadFile(
 1101:                     sock=sock, token=token, file=file_handle, size=upload.size
 1102:                 ))
 1103: 
 1104:             else:
 1105:                 self._finish_transfer(upload)
 1106:                 need_update = False
 1107: 
 1108:         if need_update:
 1109:             self._update_transfer(upload)
 1110: 
 1111:         if upload_started:
 1112:             # Must be be emitted after the final update to prevent inconsistent state
 1113:             core.pluginhandler.upload_started_notification(username, virtual_path, real_path)
 1114: 
 1115:     def _file_upload_progress(self, username, token, offset, bytes_sent, speed=None):
 1116:         """A file upload is in progress."""
 1117: 
 1118:         upload = self.active_users.get(username, {}).get(token)
 1119: 
 1120:         if upload is None:
```

### U-198 share DB path membership check

File: `pynicotine/shares.py` lines approx 837-879

```python
  837:                 share_dbs[destination] = Database(encode_path(db_path), overwrite=False)
  838: 
  839:             except Exception as error:
  840:                 exception = error
  841:                 cls.remove_db_file(db_path)
  842: 
  843:         if exception:
  844:             cls.close_shares(share_dbs)
  845:             raise exception
  846: 
  847:     def file_is_shared(self, username, virtual_path, real_path):
  848: 
  849:         log.add_transfer("Checking if file is shared: %s with real path %s",
  850:                          (virtual_path, real_path))
  851: 
  852:         public_shared_files = self.share_dbs.get("public_files")
  853:         buddy_shared_files = self.share_dbs.get("buddy_files")
  854:         trusted_shared_files = self.share_dbs.get("trusted_files")
  855:         file_is_shared = False
  856:         size = None
  857: 
  858:         if not real_path.startswith("__INVALID_SHARE__"):
  859:             if public_shared_files is not None and real_path in public_shared_files:
  860:                 file_is_shared = True
  861:                 _file_name, size, *_unused = public_shared_files[real_path]
  862: 
  863:             elif (buddy_shared_files is not None and username in core.buddies.users
  864:                     and real_path in buddy_shared_files):
  865:                 file_is_shared = True
  866:                 _file_name, size, *_unused = buddy_shared_files[real_path]
  867: 
  868:             elif trusted_shared_files is not None:
  869:                 user_data = core.buddies.users.get(username)
  870: 
  871:                 if user_data and user_data.is_trusted and real_path in trusted_shared_files:
  872:                     file_is_shared = True
  873:                     _file_name, size, *_unused = trusted_shared_files[real_path]
  874: 
  875:         if not file_is_shared:
  876:             log.add_transfer("File is not present in the database of shared files, not sharing: "
  877:                              "%s with real path %s", (virtual_path, real_path))
  878:             return False, size
  879: 
```

## github-branch-master

### U-69 queued-download size mutation from peer TransferRequest

File: `pynicotine/downloads.py` lines approx 1035-1094

```python
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
```

### U-69 F-connection leftbytes uses mutated download.size

File: `pynicotine/downloads.py` lines approx 1062-1233

```python
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
 1112: 
 1113:     def _transfer_timeout(self, transfer):
 1114: 
 1115:         if transfer.request_timer_id is None:
 1116:             return
 1117: 
 1118:         log.add_transfer("Download %s with token %s for user %s timed out",
 1119:                          (transfer.virtual_path, transfer.token, transfer.username))
 1120: 
 1121:         super()._transfer_timeout(transfer)
 1122: 
 1123:     def _download_file_error(self, username, token, error):
 1124:         """Networking thread encountered a local file error for download."""
 1125: 
 1126:         download = self.active_users.get(username, {}).get(token)
 1127: 
 1128:         if download is None:
 1129:             return
 1130: 
 1131:         self._abort_transfer(download, status=TransferStatus.LOCAL_FILE_ERROR)
 1132:         log.add(_("Download I/O error: %s"), error)
 1133: 
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
 1229: 
 1230:     def _upload_denied(self, msg):
 1231:         """Peer code 50."""
 1232: 
 1233:         username = msg.username
```

### U-107 network upload read not clamped to remaining advertised size

File: `pynicotine/slskproto.py` lines approx 2085-2135

```python
 2085:         if file_download.leftbytes <= 0:
 2086:             events.emit_main_thread(
 2087:                 "file-download-progress",
 2088:                 username=conn.init.target_user, token=file_download.token,
 2089:                 bytes_left=file_download.leftbytes
 2090:             )
 2091:             return False  # Close the connection
 2092: 
 2093:         return True
 2094: 
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

### U-198 upload eligibility checks are path/database checks before later open

File: `pynicotine/uploads.py` lines approx 424-496

```python
  424: 
  425:         for failed_uploads in self.failed_users.copy().values():
  426:             for upload in failed_uploads.copy().values():
  427:                 if upload.status != TransferStatus.CONNECTION_TIMEOUT:
  428:                     continue
  429: 
  430:                 self._unfail_transfer(upload)
  431:                 self._enqueue_transfer(upload)
  432:                 self._update_transfer(upload)
  433: 
  434:     def _check_queue_upload_allowed(self, username, addr, virtual_path, msg):
  435: 
  436:         # Is user allowed to download?
  437:         ip_address, _port = addr
  438:         permission_level, reject_reason = core.shares.check_user_permission(username, ip_address)
  439:         real_path = None
  440:         size = None
  441: 
  442:         if permission_level == PermissionLevel.BANNED:
  443:             reject_message = TransferRejectReason.BANNED
  444: 
  445:             if reject_reason:
  446:                 reject_message += f" ({reject_reason})"
  447: 
  448:             return False, reject_message, real_path, size
  449: 
  450:         if core.shares.rescanning:
  451:             self._pending_network_msgs.append(msg)
  452:             return False, None, real_path, size
  453: 
  454:         # Is that file already in the queue?
  455:         if self.is_upload_queued(username, virtual_path):
  456:             return False, TransferRejectReason.QUEUED, real_path, size
  457: 
  458:         # Are we waiting for existing uploads to finish?
  459:         if self.pending_shutdown:
  460:             return False, TransferRejectReason.PENDING_SHUTDOWN, real_path, size
  461: 
  462:         # Has user hit queue limit?
  463:         enable_limits = True
  464: 
  465:         if config.sections["transfers"]["friendsnolimits"]:
  466:             if username in core.buddies.users:
  467:                 enable_limits = False
  468: 
  469:         if enable_limits:
  470:             limit_reached, reason = self.is_queue_limit_reached(username)
  471: 
  472:             if limit_reached:
  473:                 return False, reason, real_path, size
  474: 
  475:         real_path = core.shares.virtual2real(virtual_path)
  476:         is_file_shared, size = core.shares.file_is_shared(username, virtual_path, real_path)
  477: 
  478:         # Do we actually share that file with the world?
  479:         if not is_file_shared:
  480:             return False, TransferRejectReason.FILE_NOT_SHARED, real_path, size
  481: 
  482:         return True, None, real_path, size
  483: 
  484:     def _check_backslash_path_exists(self, username, virtual_path):
  485:         """Replace a backslash sentinel with an actual backslash in a file path, and check
  486:         if a file for the resulting path exists and is shared."""
  487: 
  488:         is_shared = False
  489:         real_path = None
  490:         size = None
  491: 
  492:         if sys.platform != "win32" and core.shares.BACKSLASH_SENTINEL in virtual_path:
  493:             real_path = core.shares.virtual2real(virtual_path, revert_backslash=True)
  494:             is_shared, size = core.shares.file_is_shared(username, virtual_path, real_path)
  495: 
  496:         return is_shared, real_path, size
```

### U-198 queued upload rechecks readability/current path size before activation

File: `pynicotine/uploads.py` lines approx 169-581

```python
  169:         # All users
  170:         if config.sections["transfers"]["preferfriends"]:
  171:             return True
  172: 
  173:         # Only explicitly prioritized users
  174:         return bool(user_data.is_prioritized)
  175: 
  176:     # Stats/Limits #
  177: 
  178:     @staticmethod
  179:     def _get_current_file_size(file_path):
  180: 
  181:         try:
  182:             new_size = os.path.getsize(encode_path(file_path))
  183: 
  184:         except Exception:
  185:             new_size = None
  186: 
  187:         return new_size
  188: 
  189:     def get_downloading_users(self):
  190:         return set(self.active_users).union(self.queued_users)
  191: 
  192:     def get_total_uploads_allowed(self):
  193: 
  194:         if config.sections["transfers"]["useupslots"]:
  195:             upload_slots = config.sections["transfers"]["uploadslots"]
  196:         else:
  197:             upload_slots = len(self.active_users)
  198: 
  199:             if self.is_new_upload_accepted():
  200:                 return upload_slots + 1
  201: 
  202:         if upload_slots <= 0:
  203:             upload_slots = 1
  204: 
  205:         return upload_slots
  206: 
  207:     def get_upload_queue_size(self, username):
  208: 
  209:         if self.is_privileged(username):
  210:             return sum(
  211:                 len(queued_uploads)
  212:                 for username, queued_uploads in self.queued_users.items() if self.is_privileged(username)
  213:             )
  214: 
  215:         return len(self.queued_transfers)
  216: 
  217:     def has_active_uploads(self):
  218:         return bool(self.active_users or self.queued_users)
  219: 
  220:     def is_queue_limit_reached(self, username):
  221: 
  222:         file_limit = config.sections["transfers"]["filelimit"]
  223:         queue_size_limit = config.sections["transfers"]["queuelimit"] * 1024 * 1024
  224: 
  225:         if len(self.queued_users.get(username, {})) >= file_limit >= 1:
  226:             return True, TransferRejectReason.TOO_MANY_FILES
  227: 
  228:         if self._user_queue_sizes.get(username, 0) >= queue_size_limit >= 1:
  229:             return True, TransferRejectReason.TOO_MANY_MEGABYTES
  230: 
  231:         return False, None
  232: 
  233:     def is_slot_limit_reached(self):
  234: 
  235:         upload_slot_limit = config.sections["transfers"]["uploadslots"]
  236: 
  237:         if upload_slot_limit <= 0:
  238:             upload_slot_limit = 1
  239: 
  240:         return len(self.active_users) >= upload_slot_limit
  241: 
  242:     def is_bandwidth_limit_reached(self):
  243: 
  244:         bandwidth_limit = config.sections["transfers"]["uploadbandwidth"] * 1024
  245: 
  246:         if not bandwidth_limit:
  247:             return False
  248: 
  249:         return self.total_bandwidth >= bandwidth_limit
  250: 
  251:     def is_new_upload_accepted(self, enforce_limits=True):
  252: 
  253:         if core.shares is None or core.shares.rescanning:
  254:             return False
  255: 
  256:         if not enforce_limits:
  257:             return True
  258: 
  259:         if config.sections["transfers"]["useupslots"]:
  260:             # Limit by upload slots
  261:             if self.is_slot_limit_reached():
  262:                 return False
  263: 
  264:         elif self.is_bandwidth_limit_reached():
  265:             # Limit by maximum bandwidth
  266:             return False
  267: 
  268:         # No limits
  269:         return True
  270: 
  271:     @staticmethod
  272:     def is_file_readable(virtual_path, real_path):
  273: 
  274:         try:
  275:             if os.access(encode_path(real_path), os.R_OK):
  276:                 return True
  277: 
  278:             log.add_transfer("Cannot access file, not sharing: %s with real path %s",
  279:                              (virtual_path, real_path))
  280: 
  281:         except Exception:
  282:             log.add_transfer("Requested file path contains invalid characters or other errors, not sharing: "
  283:                              "%s with real path %s", (virtual_path, real_path))
  284: 
  285:         return False
  286: 
  287:     def is_upload_queued(self, username, virtual_path):
  288: 
  289:         if virtual_path in self.queued_users.get(username, {}):
  290:             return True
  291: 
  292:         return any(upload.virtual_path == virtual_path for upload in self.active_users.get(username, {}).values())
  293: 
  294:     def update_transfer_limits(self):
  295: 
  296:         events.emit("update-upload-limits")
  297: 
  298:         use_speed_limit = config.sections["transfers"]["use_upload_speed_limit"]
  299:         limit_by = config.sections["transfers"]["limitby"]
  300: 
  301:         if use_speed_limit == "primary":
  302:             speed_limit = config.sections["transfers"]["uploadlimit"]
  303: 
  304:         elif use_speed_limit == "alternative":
  305:             speed_limit = config.sections["transfers"]["uploadlimitalt"]
  306: 
  307:         else:
  308:             speed_limit = 0
  309: 
  310:         core.send_message_to_network_thread(SetUploadLimit(speed_limit, limit_by))
  311:         self._check_upload_queue()
  312: 
  313:     # Transfer Actions #
  314: 
  315:     def _enqueue_transfer(self, transfer, show_notification=False):
  316: 
  317:         username = transfer.username
  318: 
  319:         super()._enqueue_transfer(transfer)
  320: 
  321:         if self.is_privileged(username):
  322:             transfer.modifier = "privileged" if username in core.users.privileged else "prioritized"
  323: 
  324:         # Clear queue position cache until next position request
  325:         self._queue_positions.clear()
  326:         self._queue_position_users.pop(username, None)
  327: 
  328:         if show_notification and config.sections["notifications"]["notification_popup_queued_upload"]:
  329:             self._queue_notification_users[username].append(transfer)
  330: 
  331:         return True
  332: 
  333:     def _dequeue_transfer(self, transfer):
  334: 
  335:         username = transfer.username
  336: 
  337:         if not super()._dequeue_transfer(transfer):
  338:             return False
  339: 
  340:         if username not in self.queued_users:
  341:             self._user_update_counters.pop(username, None)
  342: 
  343:         transfer.modifier = None
  344: 
  345:         # Clear queue position cache until next position request
  346:         self._queue_positions.clear()
  347:         self._queue_position_users.pop(username, None)
  348: 
  349:         return True
  350: 
  351:     def _activate_transfer(self, transfer, token):
  352:         super()._activate_transfer(transfer, token)
  353:         self._user_update_counters.pop(transfer.username, None)
  354: 
  355:     def _update_transfer(self, transfer, update_parent=True):
  356: 
  357:         username = transfer.username
  358: 
  359:         # Don't update existing user counter for queued uploads
  360:         # We don't want to push the user back in the queue if they enqueued new files
  361:         if (username not in self._user_update_counters
  362:                 or transfer.virtual_path not in self.queued_users.get(username, {})):
  363:             self._update_user_counter(username)
  364: 
  365:         events.emit("update-upload", transfer, update_parent)
  366: 
  367:     def _finish_transfer(self, transfer, already_exists=False):
  368: 
  369:         username = transfer.username
  370:         virtual_path = transfer.virtual_path
  371: 
  372:         super()._finish_transfer(transfer)
  373: 
  374:         if not self._auto_clear_transfer(transfer):
  375:             self._update_transfer(transfer)
  376: 
  377:         if not already_exists:
  378:             core.statistics.append_stat_value("completed_uploads", 1)
  379: 
  380:             real_path = core.shares.virtual2real(
  381:                 virtual_path,
  382:                 revert_backslash=transfer.is_backslash_path,
  383:                 is_lowercase_path=transfer.is_lowercase_path
  384:             )
  385:             core.pluginhandler.upload_finished_notification(username, virtual_path, real_path)
  386: 
  387:             log.add_upload(
  388:                 _("Upload finished: user %(user)s, IP address %(ip)s, file %(file)s"), {
  389:                     "user": username,
  390:                     "ip": core.users.addresses.get(username),
  391:                     "file": virtual_path
  392:                 }
  393:             )
  394: 
  395:         self._check_upload_queue()
  396: 
  397:     def _abort_transfer(self, transfer, status=None, denied_message=None, update_parent=True):
  398: 
  399:         if transfer.file_handle is not None:
  400:             log.add_upload(
  401:                 _("Upload aborted, user %(user)s file %(file)s"), {
  402:                     "user": transfer.username,
  403:                     "file": transfer.virtual_path
  404:                 }
  405:             )
  406: 
  407:         super()._abort_transfer(transfer, status=status, denied_message=denied_message)
  408:         self._update_user_counter(transfer.username)
  409: 
  410:         if status:
  411:             events.emit("abort-upload", transfer, status, update_parent)
  412: 
  413:     def _clear_transfer(self, transfer, denied_message=None, update_parent=True):
  414: 
  415:         virtual_path = transfer.virtual_path
  416:         username = transfer.username
  417: 
  418:         log.add_transfer("Clearing upload %s to user %s", (virtual_path, username))
  419:         super()._clear_transfer(transfer, denied_message=denied_message)
  420: 
  421:         events.emit("clear-upload", transfer, update_parent)
  422: 
  423:     def _retry_failed_uploads(self):
  424: 
  425:         for failed_uploads in self.failed_users.copy().values():
  426:             for upload in failed_uploads.copy().values():
  427:                 if upload.status != TransferStatus.CONNECTION_TIMEOUT:
  428:                     continue
  429: 
  430:                 self._unfail_transfer(upload)
  431:                 self._enqueue_transfer(upload)
  432:                 self._update_transfer(upload)
  433: 
  434:     def _check_queue_upload_allowed(self, username, addr, virtual_path, msg):
  435: 
  436:         # Is user allowed to download?
  437:         ip_address, _port = addr
  438:         permission_level, reject_reason = core.shares.check_user_permission(username, ip_address)
  439:         real_path = None
  440:         size = None
  441: 
  442:         if permission_level == PermissionLevel.BANNED:
  443:             reject_message = TransferRejectReason.BANNED
  444: 
  445:             if reject_reason:
  446:                 reject_message += f" ({reject_reason})"
  447: 
  448:             return False, reject_message, real_path, size
  449: 
  450:         if core.shares.rescanning:
  451:             self._pending_network_msgs.append(msg)
  452:             return False, None, real_path, size
  453: 
  454:         # Is that file already in the queue?
  455:         if self.is_upload_queued(username, virtual_path):
  456:             return False, TransferRejectReason.QUEUED, real_path, size
  457: 
  458:         # Are we waiting for existing uploads to finish?
  459:         if self.pending_shutdown:
  460:             return False, TransferRejectReason.PENDING_SHUTDOWN, real_path, size
  461: 
  462:         # Has user hit queue limit?
  463:         enable_limits = True
  464: 
  465:         if config.sections["transfers"]["friendsnolimits"]:
  466:             if username in core.buddies.users:
  467:                 enable_limits = False
  468: 
  469:         if enable_limits:
  470:             limit_reached, reason = self.is_queue_limit_reached(username)
  471: 
  472:             if limit_reached:
  473:                 return False, reason, real_path, size
  474: 
  475:         real_path = core.shares.virtual2real(virtual_path)
  476:         is_file_shared, size = core.shares.file_is_shared(username, virtual_path, real_path)
  477: 
  478:         # Do we actually share that file with the world?
  479:         if not is_file_shared:
  480:             return False, TransferRejectReason.FILE_NOT_SHARED, real_path, size
  481: 
  482:         return True, None, real_path, size
  483: 
  484:     def _check_backslash_path_exists(self, username, virtual_path):
  485:         """Replace a backslash sentinel with an actual backslash in a file path, and check
  486:         if a file for the resulting path exists and is shared."""
  487: 
  488:         is_shared = False
  489:         real_path = None
  490:         size = None
  491: 
  492:         if sys.platform != "win32" and core.shares.BACKSLASH_SENTINEL in virtual_path:
  493:             real_path = core.shares.virtual2real(virtual_path, revert_backslash=True)
  494:             is_shared, size = core.shares.file_is_shared(username, virtual_path, real_path)
  495: 
  496:         return is_shared, real_path, size
  497: 
  498:     def _get_upload_candidate(self):
  499:         """Retrieve a suitable queued transfer for uploading.
  500: 
  501:         Round Robin: Get the first queued item from the oldest user
  502:         FIFO: Get the first queued item in the list
  503:         """
  504: 
  505:         is_fifo_queue = config.sections["transfers"]["fifoqueue"]
  506:         has_active_uploads = bool(self.active_users)
  507:         oldest_time = None
  508:         target_username = None
  509:         upload_candidate = None
  510:         privileged_users = set()
  511: 
  512:         if not self._user_update_counters:
  513:             # No queued uploads to start right now
  514:             return upload_candidate, has_active_uploads
  515: 
  516:         for username in self._user_update_counters:
  517:             if self.is_privileged(username):
  518:                 privileged_users.add(username)
  519: 
  520:         if is_fifo_queue:
  521:             for upload in self.queued_transfers:
  522:                 username = upload.username
  523: 
  524:                 if privileged_users and username not in privileged_users:
  525:                     continue
  526: 
  527:                 if username not in self._user_update_counters:
  528:                     continue
  529: 
  530:                 target_username = username
  531:                 break
  532:         else:
  533:             for username, update_time in self._user_update_counters.items():
  534:                 if privileged_users and username not in privileged_users:
  535:                     continue
  536: 
  537:                 if not oldest_time:
  538:                     oldest_time = update_time + 1
  539: 
  540:                 if update_time < oldest_time:
  541:                     target_username = username
  542:                     oldest_time = update_time
  543: 
  544:         if target_username is not None:
  545:             upload_candidate = next(iter(self.queued_users[target_username].values()), None)
  546: 
  547:         return upload_candidate, has_active_uploads
  548: 
  549:     def _update_user_counter(self, username):
  550:         """Called when an upload associated with a user has changed.
  551: 
  552:         The user update counter is used by the Round Robin queue system
  553:         to determine which user has waited the longest since their last
  554:         download.
  555:         """
  556: 
  557:         if username in self.queued_users and username not in self.active_users:
  558:             self._user_update_counter += 1
  559:             self._user_update_counters[username] = self._user_update_counter
  560: 
  561:     def _check_upload_queue(self, upload_candidate=None):
  562:         """Find next file to upload."""
  563: 
  564:         final_upload_candidate = None
  565: 
  566:         while final_upload_candidate is None:
  567:             # If a candidate is provided, we want to upload it immediately
  568:             if not self.is_new_upload_accepted(enforce_limits=(upload_candidate is None)):
  569:                 return
  570: 
  571:             if upload_candidate is None:
  572:                 upload_candidate, has_active_uploads = self._get_upload_candidate()
  573: 
  574:                 if upload_candidate is None:
  575:                     if not has_active_uploads and self.pending_shutdown:
  576:                         self.pending_shutdown = False
  577:                         core.quit()
  578:                     return
  579: 
  580:             elif upload_candidate not in self.queued_users.get(upload_candidate.username, {}).values():
  581:                 return
```

### U-198 F-connection opens current path and emits UploadFile with stored size

File: `pynicotine/uploads.py` lines approx 1131-1217

```python
 1131:             status = TransferStatus.CANCELLED
 1132:             error = f"Remote client does not support large file transfers: {error}"
 1133:         else:
 1134:             status = TransferStatus.LOCAL_FILE_ERROR
 1135: 
 1136:         self._abort_transfer(upload, status=status)
 1137: 
 1138:         log.add(_("Upload I/O error: %s"), error)
 1139:         self._check_upload_queue()
 1140: 
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
```

### U-198 share DB path membership check

File: `pynicotine/shares.py` lines approx 922-964

```python
  922:                 share_dbs[destination] = Database(encode_path(db_path), overwrite=False)
  923: 
  924:             except Exception as error:
  925:                 exception = error
  926:                 cls.remove_db_file(db_path)
  927: 
  928:         if exception:
  929:             cls.close_shares(share_dbs)
  930:             raise exception
  931: 
  932:     def file_is_shared(self, username, virtual_path, real_path):
  933: 
  934:         log.add_transfer("Checking if file is shared: %s with real path %s",
  935:                          (virtual_path, real_path))
  936: 
  937:         public_shared_files = self.share_dbs.get("public_files")
  938:         buddy_shared_files = self.share_dbs.get("buddy_files")
  939:         trusted_shared_files = self.share_dbs.get("trusted_files")
  940:         file_is_shared = False
  941:         size = None
  942: 
  943:         if not real_path.startswith("__INVALID_SHARE__"):
  944:             if public_shared_files is not None and real_path in public_shared_files:
  945:                 file_is_shared = True
  946:                 _file_name, size, *_unused = public_shared_files[real_path]
  947: 
  948:             elif (buddy_shared_files is not None and username in core.buddies.users
  949:                     and real_path in buddy_shared_files):
  950:                 file_is_shared = True
  951:                 _file_name, size, *_unused = buddy_shared_files[real_path]
  952: 
  953:             elif trusted_shared_files is not None:
  954:                 user_data = core.buddies.users.get(username)
  955: 
  956:                 if user_data and user_data.is_trusted and real_path in trusted_shared_files:
  957:                     file_is_shared = True
  958:                     _file_name, size, *_unused = trusted_shared_files[real_path]
  959: 
  960:         if not file_is_shared:
  961:             log.add_transfer("File is not present in the database of shared files, not sharing: "
  962:                              "%s with real path %s", (virtual_path, real_path))
  963:             return False, size
  964: 
```
