# rev0036 U-123 source trace

Line anchors for the production-draft packet. This is an anchor map, not a source copy.

## github-tag-3.3.10

### `pynicotine/transfers.py`

sha256: `78e864766dd96a33a790b571eb44a8f052c9ee1064fcb99f98c798900ba29db7`

- line 527: `def _activate_transfer(self, transfer, token):`
- line 543: `transfer.request_timer_id = events.schedule(`
- line 546: `self.active_users[transfer.username][token] = transfer`
- line 548: `def _deactivate_transfer(self, transfer):`
- line 553: `if token is None or token not in self.active_users.get(username, {}):`
- line 556: `del self.active_users[username][token]`
- line 569: `transfer.sock = None`
- line 570: `transfer.token = None`
- line 389: `def _transfer_timeout(self, transfer):`
- line 390: `self._abort_transfer(transfer, status=TransferStatus.CONNECTION_TIMEOUT)`
- line 397: `def _abort_transfer(self, transfer, status=None, denied_message=None):`
- line 419: `self._deactivate_transfer(transfer)`
- line 467: `self._deactivate_transfer(transfer)`

### `pynicotine/downloads.py`

sha256: `d4cf926ce5d24b8dc8bfd394edf83c9a9386844c41ee3a768622818cd73e6ddd`

- line 1131: `def _transfer_timeout(self, transfer):`
- line 1139: `super()._transfer_timeout(transfer)`
- line 1152: `def _file_transfer_init(self, msg):`
- line 1144: `download = self.active_users.get(username, {}).get(token)`
- line 1161: `download = self.active_users.get(username, {}).get(token)`
- line 1332: `download = self.active_users.get(username, {}).get(token)`
- line 1350: `download = self.active_users.get(username, {}).get(token)`
- line 1163: `if download is None or download.sock is not None:`
- line 1168: `sock = download.sock = msg.sock`
- line 1329: `def _file_download_progress(self, username, token, bytes_left, speed=None):`
- line 1347: `def _file_connection_closed(self, username, token, sock, **_unused):`
- line 1355: `if download.sock != sock:`

### `pynicotine/slskmessages.py`

sha256: `152fba05c9ac127c9eb46c3aad834659e076744315fe034fc93d836b47f86fab`

- line 3525: `class TransferRequest(PeerMessage):`
- line 3787: `class FileTransferInit(FileMessage):`
- line 205: `self.token = token`
- line 216: `self.token = token`
- line 1035: `self.token = token`
- line 1124: `self.token = token`
- line 1152: `self.token = token`
- line 1224: `self.token = token`

## github-branch-3.3.x

### `pynicotine/transfers.py`

sha256: `61e3c42c9f761d171c716892cd4832ef98fd6fd05cb45d553c0d7c3f132a4e55`

- line 530: `def _activate_transfer(self, transfer, token):`
- line 546: `transfer.request_timer_id = events.schedule(`
- line 549: `self.active_users[transfer.username][token] = transfer`
- line 551: `def _deactivate_transfer(self, transfer):`
- line 556: `if token is None or token not in self.active_users.get(username, {}):`
- line 559: `del self.active_users[username][token]`
- line 572: `transfer.sock = None`
- line 573: `transfer.token = None`
- line 392: `def _transfer_timeout(self, transfer):`
- line 393: `self._abort_transfer(transfer, status=TransferStatus.CONNECTION_TIMEOUT)`
- line 400: `def _abort_transfer(self, transfer, status=None, denied_message=None):`
- line 422: `self._deactivate_transfer(transfer)`
- line 470: `self._deactivate_transfer(transfer)`

### `pynicotine/downloads.py`

sha256: `e1d6697fde4b520d7aed76f9e565857abfe8d2a9edd87e1eed2bb2ef7cda01d4`

- line 1142: `def _transfer_timeout(self, transfer):`
- line 1150: `super()._transfer_timeout(transfer)`
- line 1163: `def _file_transfer_init(self, msg):`
- line 1155: `download = self.active_users.get(username, {}).get(token)`
- line 1172: `download = self.active_users.get(username, {}).get(token)`
- line 1346: `download = self.active_users.get(username, {}).get(token)`
- line 1364: `download = self.active_users.get(username, {}).get(token)`
- line 1174: `if download is None or download.sock is not None:`
- line 1181: `sock = download.sock = msg.sock`
- line 1343: `def _file_download_progress(self, username, token, bytes_left, speed=None):`
- line 1361: `def _file_connection_closed(self, username, token, sock, **_unused):`
- line 1369: `if download.sock != sock:`

### `pynicotine/slskmessages.py`

sha256: `c0c237898334447a2ecb9d8d921586e35a7c1a399dedcb3ba038834657bf9e2e`

- line 3561: `class TransferRequest(PeerMessage):`
- line 3832: `class FileTransferInit(FileMessage):`
- line 205: `self.token = token`
- line 216: `self.token = token`
- line 1046: `self.token = token`
- line 1135: `self.token = token`
- line 1163: `self.token = token`
- line 1235: `self.token = token`

## github-branch-master

### `pynicotine/transfers.py`

sha256: `e8f04ede0635635f4eaf3445afa5ae417677af3489f3c306f9d1e43bc7e0a2cd`

- line 528: `def _activate_transfer(self, transfer, token):`
- line 544: `transfer.request_timer_id = events.schedule(`
- line 547: `self.active_users[transfer.username][token] = transfer`
- line 549: `def _deactivate_transfer(self, transfer):`
- line 554: `if token is None or token not in self.active_users.get(username, {}):`
- line 557: `del self.active_users[username][token]`
- line 570: `transfer.sock = None`
- line 571: `transfer.token = None`
- line 390: `def _transfer_timeout(self, transfer):`
- line 391: `self._abort_transfer(transfer, status=TransferStatus.CONNECTION_TIMEOUT)`
- line 398: `def _abort_transfer(self, transfer, status=None, denied_message=None):`
- line 420: `self._deactivate_transfer(transfer)`
- line 468: `self._deactivate_transfer(transfer)`

### `pynicotine/downloads.py`

sha256: `0638a8dbcdef278baa4ccc3f81ff2438834d93501f4f845d8aa91f786b8aa2ca`

- line 1113: `def _transfer_timeout(self, transfer):`
- line 1121: `super()._transfer_timeout(transfer)`
- line 1134: `def _file_transfer_init(self, msg):`
- line 1126: `download = self.active_users.get(username, {}).get(token)`
- line 1143: `download = self.active_users.get(username, {}).get(token)`
- line 1317: `download = self.active_users.get(username, {}).get(token)`
- line 1335: `download = self.active_users.get(username, {}).get(token)`
- line 1145: `if download is None or download.sock is not None:`
- line 1152: `sock = download.sock = msg.sock`
- line 1314: `def _file_download_progress(self, username, token, bytes_left, speed=None):`
- line 1332: `def _file_connection_closed(self, username, token, sock, **_unused):`
- line 1340: `if download.sock != sock:`

### `pynicotine/slskmessages.py`

sha256: `43787bef158d35b27c7720ac19e89fa8e221f43df515cd73ce05ef494c1dfd78`

- line 3717: `class TransferRequest(PeerMessage):`
- line 3991: `class FileTransferInit(FileMessage):`
- line 208: `self.token = token`
- line 219: `self.token = token`
- line 1064: `self.token = token`
- line 1157: `self.token = token`
- line 1186: `self.token = token`
- line 1270: `self.token = token`
