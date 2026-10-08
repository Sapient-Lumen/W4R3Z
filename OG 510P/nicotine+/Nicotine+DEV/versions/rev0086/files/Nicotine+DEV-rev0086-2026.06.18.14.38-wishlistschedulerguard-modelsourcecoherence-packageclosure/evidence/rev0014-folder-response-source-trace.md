# rev0014 FolderContentsResponse source trace

External source bundle is not embedded in this cube. Snippets were taken from the local extraction of rev0003 upstream source lanes.

## github-tag-3.3.10
### downloads.py — enqueue_folder sends a request token
```text
  765:     def enqueue_folder(self, username, folder_path, download_folder_path=None):
  766: 
  767:         requested_folder = self._requested_folders.get(username, {}).get(folder_path)
  768: 
  769:         if requested_folder is None:
  770:             self._requested_folders[username][folder_path] = requested_folder = RequestedFolder(
  771:                 username, folder_path, download_folder_path
  772:             )
  773: 
  774:         # First timeout is shorter to get a response sooner in case the first request
  775:         # failed. Second timeout is longer in case the response is delayed.
  776:         timeout = 60 if requested_folder.has_retried else 15
  777: 
  778:         if requested_folder.request_timer_id is not None:
  779:             events.cancel_scheduled(requested_folder.request_timer_id)
  780:             requested_folder.request_timer_id = None
  781: 
  782:         requested_folder.request_timer_id = events.schedule(
  783:             delay=timeout, callback=self._requested_folder_timeout, callback_args=(requested_folder,)
  784:         )
  785: 
  786:         log.add_transfer("Requesting contents of folder %s from user %s", (folder_path, username))
  787: 
  788:         self._requested_folder_token = increment_token(self._requested_folder_token)
  789: 
  790:         core.send_message_to_peer(
  791:             username, FolderContentsRequest(
  792:                 folder_path, self._requested_folder_token, legacy_client=requested_folder.legacy_attempt
  793:             )
  794:         )
  795: 
  796:     def enqueue_download(self, username, virtual_path, folder_path=None, size=0, file_attributes=None,
  797:                          bypass_filter=False):
```
### downloads.py — _folder_contents_response consumes by username+folder and ignores msg.token
```text
  993:     def _folder_contents_response(self, msg, check_num_files=True):
  994:         """Peer code 37."""
  995: 
  996:         username = msg.username
  997:         folder_path = msg.dir
  998: 
  999:         if username not in self._requested_folders:
 1000:             return
 1001: 
 1002:         requested_folder = self._requested_folders[username].get(msg.dir)
 1003: 
 1004:         if requested_folder is None:
 1005:             return
 1006: 
 1007:         log.add_transfer("Received response for folder content request for folder %s "
 1008:                          "from user %s", (folder_path, username))
 1009: 
 1010:         if requested_folder.request_timer_id is not None:
 1011:             events.cancel_scheduled(requested_folder.request_timer_id)
 1012:             requested_folder.request_timer_id = None
 1013: 
 1014:         if not msg.list and not requested_folder.legacy_attempt:
 1015:             log.add_transfer("Folder content response is empty. Trying legacy latin-1 request.")
 1016:             requested_folder.legacy_attempt = True
 1017:             self.enqueue_folder(username, folder_path, requested_folder.download_folder_path)
 1018:             return
 1019: 
 1020:         for i_folder_path, files in msg.list.items():
 1021:             if i_folder_path != folder_path:
 1022:                 continue
 1023: 
 1024:             num_files = len(files)
 1025: 
 1026:             if check_num_files and num_files > 100:
 1027:                 check_num_files = False
 1028:                 events.emit(
 1029:                     "download-large-folder", username, folder_path, num_files,
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
```
### slskmessages.py — response parser materializes folders after decompression
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
 3523: 
 3524: 
 3525: class TransferRequest(PeerMessage):
 3526:     """Peer code 40.
 3527: 
 3528:     This message is sent by a peer once they are ready to start
 3529:     uploading a file. A TransferResponse message is expected from the
```

## github-branch-3.3.x
### downloads.py — enqueue_folder sends a request token
```text
  776:     def enqueue_folder(self, username, folder_path, download_folder_path=None):
  777: 
  778:         requested_folder = self._requested_folders.get(username, {}).get(folder_path)
  779: 
  780:         if requested_folder is None:
  781:             self._requested_folders[username][folder_path] = requested_folder = RequestedFolder(
  782:                 username, folder_path, download_folder_path
  783:             )
  784: 
  785:         # First timeout is shorter to get a response sooner in case the first request
  786:         # failed. Second timeout is longer in case the response is delayed.
  787:         timeout = 60 if requested_folder.has_retried else 15
  788: 
  789:         if requested_folder.request_timer_id is not None:
  790:             events.cancel_scheduled(requested_folder.request_timer_id)
  791:             requested_folder.request_timer_id = None
  792: 
  793:         requested_folder.request_timer_id = events.schedule(
  794:             delay=timeout, callback=self._requested_folder_timeout, callback_args=(requested_folder,)
  795:         )
  796: 
  797:         log.add_transfer("Requesting contents of folder %s from user %s", (folder_path, username))
  798: 
  799:         self._requested_folder_token = increment_token(self._requested_folder_token)
  800: 
  801:         core.send_message_to_peer(
  802:             username, FolderContentsRequest(
  803:                 folder_path, self._requested_folder_token, legacy_client=requested_folder.legacy_attempt
  804:             )
  805:         )
  806: 
  807:     def enqueue_download(self, username, virtual_path, folder_path=None, size=0, file_attributes=None,
  808:                          bypass_filter=False):
```
### downloads.py — _folder_contents_response consumes by username+folder and ignores msg.token
```text
 1004:     def _folder_contents_response(self, msg, check_num_files=True):
 1005:         """Peer code 37."""
 1006: 
 1007:         username = msg.username
 1008:         folder_path = msg.dir
 1009: 
 1010:         if username not in self._requested_folders:
 1011:             return
 1012: 
 1013:         requested_folder = self._requested_folders[username].get(msg.dir)
 1014: 
 1015:         if requested_folder is None:
 1016:             return
 1017: 
 1018:         log.add_transfer("Received response for folder content request for folder %s "
 1019:                          "from user %s", (folder_path, username))
 1020: 
 1021:         if requested_folder.request_timer_id is not None:
 1022:             events.cancel_scheduled(requested_folder.request_timer_id)
 1023:             requested_folder.request_timer_id = None
 1024: 
 1025:         if not msg.list and not requested_folder.legacy_attempt:
 1026:             log.add_transfer("Folder content response is empty. Trying legacy latin-1 request.")
 1027:             requested_folder.legacy_attempt = True
 1028:             self.enqueue_folder(username, folder_path, requested_folder.download_folder_path)
 1029:             return
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
```
### slskmessages.py — response parser materializes folders after decompression
```text
 3483: 
 3484:         return msg
 3485: 
 3486:     def parse_network_message(self, message):
 3487:         pos, self.token = self.unpack_uint32(message)
 3488:         pos, self.dir = self.unpack_string(message, pos)
 3489: 
 3490: 
 3491: class FolderContentsResponse(PeerMessage):
 3492:     """Peer code 37.
 3493: 
 3494:     A peer responds with the contents of a particular folder (with all
 3495:     subfolders) after we've sent a FolderContentsRequest.
 3496:     """
 3497: 
 3498:     __slots__ = ("dir", "token", "list")
 3499: 
 3500:     def __init__(self, directory=None, token=None, shares=None):
 3501:         PeerMessage.__init__(self)
 3502:         self.dir = directory
 3503:         self.token = token
 3504:         self.list = shares
 3505: 
 3506:     def parse_network_message(self, message):
 3507:         decompressor = zlib.decompressobj()
 3508:         max_uncompressed_size = 134217728  # 128 MiB
 3509:         decompressed_message = decompressor.decompress(message, max_uncompressed_size)
 3510: 
 3511:         if not decompressor.unconsumed_tail:
 3512:             self._parse_network_message(memoryview(decompressed_message))
 3513: 
 3514:     def _parse_network_message(self, message):
 3515:         pos, self.token = self.unpack_uint32(message)
 3516:         pos, self.dir = self.unpack_string(message, pos)
 3517:         pos, ndir = self.unpack_uint32(message, pos)
 3518: 
 3519:         folders = {}
 3520: 
 3521:         for _ in range(ndir):
 3522:             pos, directory = self.unpack_string(message, pos)
 3523:             directory = directory.replace("/", "\\")
 3524:             pos, nfiles = self.unpack_uint32(message, pos)
 3525: 
 3526:             ext = None
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
 3567: 
 3568:     This message was formerly used to send a download request (direction
 3569:     0) as well, but Nicotine+ >= 3.0.3, Museek+ and the official clients
 3570:     use the QueueUpload message for this purpose today.  Clients like
 3571:     slskd and Seeker still use this method for downloading, so we need to
 3572:     ensure we still understand such requests.
 3573:     """
 3574: 
 3575:     __slots__ = ("direction", "token", "file", "filesize")
 3576: 
 3577:     def __init__(self, direction=None, token=None, file=None, filesize=None):
 3578:         PeerMessage.__init__(self)
```

## github-branch-master
### downloads.py — request_folder sends allowed-response by username+folder and request token separately
```text
  751:     def request_folder(self, username, folder_path):
  752: 
  753:         requested_folder = self._requested_folders.get(username, {}).get(folder_path)
  754: 
  755:         if requested_folder is None:
  756:             self._requested_folders[username][folder_path] = requested_folder = RequestedFolder(
  757:                 username, folder_path
  758:             )
  759: 
  760:         if requested_folder.request_timer_id is not None:
  761:             events.cancel_scheduled(requested_folder.request_timer_id)
  762:             requested_folder.request_timer_id = None
  763: 
  764:         requested_folder.request_timer_id = events.schedule(
  765:             delay=5, callback=self._requested_folder_timeout, callback_args=(requested_folder,)
  766:         )
  767: 
  768:         log.add_transfer("Requesting contents of folder %s from user %s", (folder_path, username))
  769: 
  770:         self._requested_folder_token = increment_token(self._requested_folder_token)
  771: 
  772:         core.send_message_to_network_thread(
  773:             AddAllowedResponse(FolderContentsResponse, username + folder_path)
  774:         )
  775:         core.send_message_to_peer(
  776:             username, FolderContentsRequest(
  777:                 folder_path, self._requested_folder_token, legacy_client=requested_folder.legacy_attempt
  778:             )
  779:         )
```
### downloads.py — _folder_contents_response removes allowed response and consumes request by username+folder, not token
```text
  990:     def _folder_contents_response(self, msg):
  991:         """Peer code 37."""
  992: 
  993:         if msg.list is None:
  994:             # Response was rejected
  995:             msg.token = msg.dir = None
  996:             return
  997: 
  998:         username = msg.username
  999:         folder_path = msg.dir
 1000: 
 1001:         core.send_message_to_network_thread(
 1002:             RemoveAllowedResponse(FolderContentsResponse, username + folder_path)
 1003:         )
 1004: 
 1005:         if username not in self._requested_folders:
 1006:             msg.token = msg.dir = None
 1007:             return
 1008: 
 1009:         requested_folder = self._requested_folders[username].get(msg.dir)
 1010: 
 1011:         if requested_folder is None:
 1012:             msg.token = msg.dir = None
 1013:             return
 1014: 
 1015:         log.add_transfer("Received response for folder content request for folder %s "
 1016:                          "from user %s", (folder_path, username))
 1017: 
 1018:         if requested_folder.request_timer_id is not None:
 1019:             events.cancel_scheduled(requested_folder.request_timer_id)
 1020:             requested_folder.request_timer_id = None
 1021: 
 1022:         if not msg.list and not requested_folder.legacy_attempt:
 1023:             log.add_transfer("Folder content response is empty. Trying legacy latin-1 request.")
 1024:             requested_folder.legacy_attempt = True
 1025:             self.request_folder(username, folder_path)
 1026:             return
 1027: 
 1028:         del self._requested_folders[username][folder_path]
 1029: 
```
### slskmessages.py — parser reads token+dir, checks allowed username+dir, then parses remaining folders
```text
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
 3672: 
 3673:     def _parse_remaining_network_message(self):
 3674:         ndir = self.unpack_uint32()
 3675:         folders = {}
 3676: 
 3677:         for _ in range(ndir):
 3678:             directory = self.unpack_string().replace("/", "\\")
 3679:             nfiles = self.unpack_uint32()
 3680: 
 3681:             ext = None
 3682:             folders[directory] = []
 3683: 
 3684:             for _ in range(nfiles):
 3685:                 code = self.unpack_uint8()
 3686:                 name = self.unpack_string()
 3687:                 size = self.unpack_file_size()
 3688:                 ext_len = self.unpack_uint32()  # Obsolete, ignore
 3689:                 self._offset += ext_len
 3690:                 attrs = self.unpack_file_attributes()
 3691: 
 3692:                 folders[directory].append((code, name, size, ext, attrs))
 3693: 
 3694:             if nfiles > 1:
 3695:                 folders[directory].sort(key=itemgetter(1))
 3696: 
 3697:         self.list = folders
 3698: 
 3699:     def make_network_message(self):
 3700:         msg = bytearray()
 3701:         msg += self.pack_uint32(self.token)
 3702:         msg += self.pack_string(self.dir)
 3703: 
 3704:         if self.list is not None:
 3705:             msg += self.pack_uint32(1)
 3706:             msg += self.pack_string(self.dir)
 3707: 
 3708:             # We already saved the folder contents as a bytearray when scanning our shares
```
### gtkgui/dialogs/download.py — UI filters parsed folders by msg.dir
```text
  419:     def folder_contents_response(self, msg):
  420: 
  421:         if msg.dir is None:
  422:             return
  423: 
  424:         username = msg.username
  425: 
  426:         if username not in self.pending_folders:
  427:             return
  428: 
  429:         if msg.dir not in self.pending_folders[username]:
  430:             return
  431: 
  432:         self.tree_view.freeze()
  433: 
  434:         selected = True
  435: 
  436:         for folder_path, files in msg.list.items():
  437:             if folder_path != msg.dir:
  438:                 continue
  439: 
  440:             parent_iterator, child_iterators = self.parent_iterators[username + folder_path]
  441:             unselected_parent = False
  442: 
  443:             for _code, file_name, size, _ext, file_attributes, *_unused in reversed(files):
  444:                 file_path = "\\".join([folder_path, file_name])
  445: 
  446:                 if username + file_path in self.tree_view.iterators:
  447:                     continue
  448: 
  449:                 iterator = self.tree_view.add_row(
  450:                     [
  451:                         file_name,
  452:                         "",
  453:                         human_size(size),
  454:                         selected,
  455:                         username,
  456:                         folder_path,
  457:                         size,
  458:                         file_attributes,
  459:                         False,
  460:                         username + file_path
  461:                     ],
  462:                     select_row=False, parent_iterator=parent_iterator
  463:                 )
  464:                 child_iterators.appendleft(iterator)
  465:                 self.num_files[username][folder_path] += 1
  466: 
  467:                 self.total_selected_size += size
  468:                 self.num_selected_files[username][folder_path] += 1
  469: 
  470:                 if not unselected_parent:
  471:                     self.initial_selected_iterators.discard(parent_iterator)
  472:                     unselected_parent = True
  473: 
  474:             if not files:
  475:                 self.set_failed(username, folder_path)
  476: 
  477:             self.pending_folders[username].remove(folder_path)
  478:             self.failed_usernames.discard(username)
  479:             self.tree_view.set_row_value(parent_iterator, "incomplete", "")
  480: 
  481:             if not self.pending_folders[username]:
  482:                 del self.pending_folders[username]
  483: 
  484:         self.update_title()
  485: 
  486:         if not self.pending_folders:
  487:             self.set_finished()
  488: 
  489:         elif not msg.list:
  490:             self.set_failed(username, msg.dir)
  491: 
  492:         self.tree_view.unfreeze()
```
